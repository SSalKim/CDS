from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

import numpy as np
from PIL import Image

from public_charts import policy
from public_charts import producer
from public_charts.extended_sources import ExtraFields, winter_fields
from public_charts.sources import Decoded, NotReady
from public_charts_runner import choose
from public_charts_run import (current_render_keys, finalize_cleanup, manifest_bytes, plan_cleanup, recover_rows, resolve_plan)
from public_charts_runtime import prune_checkpoints
from public_charts.sources import Provider


def row(model="aifs", cycle="2026111500", hour=24, product="gph500", domain="asia", size=10, file_id=None):
    return {"model": model, "cycle": cycle, "hour": hour, "product": product, "domain": domain,
            "file_id": file_id or f"{model}-{cycle}-{product}", "size": size, "sha256": "a" * 64,
            "url": "https://drive.usercontent.google.com/download?id=example"}


class PolicyTests(unittest.TestCase):
    def test_zero_and_native_timeline(self):
        for model in policy.RETENTION:
            timeline = policy.hours(model)
            self.assertEqual(timeline[0], 0)
            self.assertEqual(timeline[-1], 240)
            self.assertEqual(len(timeline), 29 if model in {"aifs", "aigfs"} else 43)
            self.assertTrue({84, 90, 96, 108, 120} <= set(timeline))
            keys = policy.expected_keys(model, "2026111500", 0)
            self.assertTrue(any("/surfce/" in key for key in keys))
            self.assertFalse(any("/acrain" in key for key in keys))

    def test_seasons_are_distinct(self):
        self.assertIn("gph200", policy.products("2026101500"))
        self.assertIn("gph300", policy.products("2026111500"))
        self.assertTrue(policy.winter("gfs", "2026101500"))
        self.assertFalse(policy.winter("aigfs", "2026111500"))

    def test_exact_model_names(self):
        self.assertEqual(policy.TITLES["aifs"], "ECMWF AIFS-Single (N320)")
        self.assertEqual(policy.TITLES["cmc"], "CMC GDPS (GEM 0.135\u02da L84)")

    def test_common_six_utc_run_skips_cmc_instead_of_substituting_cycle(self):
        planned=resolve_plan(["gfs","cmc"],"2026111506",[0])
        self.assertEqual(planned,[{"model":"gfs","cycle":"2026111506","hour":0}])

    def test_cycle_selection_utc(self):
        now = datetime(2026, 11, 16, 8, 20, tzinfo=timezone.utc)
        self.assertEqual(policy.cycle_candidates("aifs", now), ["2026111606", "2026111600"])
        self.assertEqual(policy.cycle_candidates("cmc", now), ["2026111600", "2026111512"])

    def test_automatic_plan_starts_at_the_configured_cycle_and_recovers_missed_cycles(self):
        now = datetime(2026, 11, 16, 1, tzinfo=timezone.utc)
        planned = resolve_plan(["aifs", "cmc"], requested_hours=[0, 24], now=now,
                               start_cycle="2026111512")
        self.assertTrue(all(item["cycle"] >= "2026111512" for item in planned))
        self.assertEqual({item["cycle"] for item in planned if item["model"] == "aifs"},
                         {"2026111512", "2026111518", "2026111600"})
        self.assertEqual({item["cycle"] for item in planned if item["model"] == "cmc"},
                         {"2026111512", "2026111600"})
        self.assertEqual([item["hour"] for item in planned[:3]], [0, 0, 0])

    def test_explicit_cycle_cannot_bypass_the_start_floor(self):
        with self.assertRaises(ValueError):
            resolve_plan(["gfs"], cycle="2026111506", start_cycle="2026111512")
        with self.assertRaises(ValueError):
            resolve_plan(["gfs"], start_cycle="2026111513")

    def test_old_render_versions_are_refreshed_without_losing_published_rows(self):
        previous=row()
        rows={policy.row_key(previous):previous}
        self.assertEqual(current_render_keys(rows),set())
        previous["render_version"]=policy.PIPELINE_VERSION
        self.assertEqual(current_render_keys(rows),set(rows))
        self.assertEqual(policy.public_manifest(list(rows.values()))["charts"][0]["render_version"],policy.PIPELINE_VERSION)

    def test_reject_invalid_model_cycle_product_or_hour(self):
        for args in (("cmc", "2026111506", 0, "surfce", "asia"),
                     ("aifs", "2026111500", 3, "gph500", "asia"),
                     ("gfs", "2026111500", 24, "thk500", "asia")):
            with self.assertRaises(ValueError):
                policy.key(*args)

    def test_retention_9_and_5_not_dates_only(self):
        rows = []
        for model, count in policy.RETENTION.items():
            cycles = policy.cycle_candidates(model, datetime(2026, 11, 16, tzinfo=timezone.utc), count + 3)
            rows.extend(row(model=model, cycle=cycle) for cycle in cycles)
        kept, delete = policy.retain(rows)
        for model, count in policy.RETENTION.items():
            self.assertEqual(sum(r["model"] == model for r in kept), count)
        self.assertEqual(len(delete), 12)

    def test_aliases_share_bytes_and_do_not_delete_shared_id(self):
        rows = [row(product="surfce", file_id="same", size=100), row(product="acptot", file_id="same", size=100)]
        self.assertEqual(policy.unique_bytes(rows), 100)
        kept, delete = policy.retain(rows, 100)
        self.assertEqual(len(kept), 2)
        self.assertEqual(delete, [])

    def test_budget_evicts_whole_old_cycle_but_protects_latest(self):
        rows = [row(cycle="2026111500", size=70), row(cycle="2026111506", size=70)]
        kept, _ = policy.retain(rows, 100)
        self.assertEqual([r["cycle"] for r in kept], ["2026111506"])
        with self.assertRaises(ValueError):
            policy.retain(rows, 50)

    def test_full_budget_reserves_space_for_first_new_image(self):
        rows=[row(cycle="2026111500",size=50),row(cycle="2026111506",size=50)]
        inventory=[{"id":r["file_id"],"appProperties":{"kind":"image"}} for r in rows]
        kept, delete=plan_cleanup(rows,inventory,100,reserve_bytes=1)
        self.assertEqual([r["cycle"] for r in kept],["2026111506"])
        self.assertEqual(delete,[rows[0]["file_id"]])


class RunnerTests(unittest.TestCase):
    def test_idle_laptop_only(self):
        good = {"status": "online", "busy": False, "labels": [{"name": "Linux"}, {"name": "cds-vtg"}]}
        self.assertEqual(choose({"runners": [good]}), ["self-hosted", "linux", "cds-vtg"])
        for changed in ({"busy": True}, {"status": "offline"}, {"labels": []}):
            self.assertEqual(choose({"runners": [{**good, **changed}]}), "ubuntu-24.04")
        self.assertEqual(choose({}), "ubuntu-24.04")

    def test_aigfs_uses_operational_s3_prefix_not_legacy_graphcast(self):
        from unittest.mock import Mock
        client=Mock()
        client.get.side_effect=lambda url,*args,**kwargs: b"1:0:d=2026111500:PRMSL:mean sea level:anl:\n2:100:d=2026111500:TMP:surface:anl:\n" if url.endswith('.idx') else b'GRIB'
        expected=object()
        with patch("public_charts.sources.decode",return_value=expected):
            result=Provider("aigfs",client).noaa("2026111500",0,{"pressure_msl"})
        self.assertIs(result["pressure_msl"],expected)
        self.assertTrue(all("noaa-nws-graphcastgfs-pds.s3.amazonaws.com/aigfs.20261115/" in call.args[0] for call in client.get.call_args_list))
        self.assertTrue(all("forecast_13_levels" not in call.args[0] for call in client.get.call_args_list))


class ProductionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.base = {"latitude": np.array([30., 40.]), "longitude": np.array([120., 130.]),
                     "terrain_height": np.zeros((2, 2)), "pressure_msl": np.full((2, 2), 101000.)}

    @staticmethod
    def picture(*args, **kwargs):
        data = np.tile(np.array([0, 255], dtype=np.uint8), (16, 8))
        return Image.fromarray(data).convert("RGB")

    def test_zero_keeps_normal_titles_and_all_three_empty_winter_panels(self):
        entries = []
        with patch.object(producer, "collect", return_value=(self.base, {}, {})), \
                patch.object(producer,"winter_fields",side_effect=lambda extra,base,hour,interval:(base,{})), \
                patch.object(producer, "render", side_effect=self.picture) as render:
            result = producer.produce_lead("aifs", "2026111500", 0, self.root, set(),
                                          lambda product, domain, path, alias_of=None: entries.append((product, domain, path, alias_of)))
        self.assertTrue(result["complete"])
        self.assertEqual(render.call_count, 18)
        self.assertEqual(len(entries), 18)
        self.assertFalse(any(item[0].startswith("acrain") for item in entries))
        self.assertFalse(any(call.kwargs["pressure_only"] for call in render.call_args_list))
        winter_calls=[call for call in render.call_args_list if call.args[3] in ("acptot","acptot_snow","acptot_snowdepth")]
        self.assertEqual(len(winter_calls),3)
        self.assertTrue(all(call.kwargs["precipitation_hours"]==0 for call in winter_calls))
        self.assertTrue(all(not np.any(call.args[0]["precipitation"]) for call in winter_calls))

    def test_zero_winter_fields_use_instantaneous_state_without_accumulation_queries(self):
        from unittest.mock import Mock
        base={**self.base,"precipitation":np.zeros((2,2))}
        for key in ("geopotential_925","geopotential_850","temperature_925","temperature_850","wind_u_925","wind_v_925"):
            base[key]=np.full((2,2),273.)
        extra=ExtraFields(self.root,"aifs","2026111500")
        extra.get=Mock(return_value=Decoded(np.full((2,2),100.),base["latitude"],base["longitude"],{}))
        surface={"latitude":base["latitude"],"longitude":base["longitude"],
                 "temperature_2m":np.full((2,2),273.),"relative_humidity_2m":np.full((2,2),80.),
                 "surface_pressure":np.full((2,2),101000.)}
        with patch("public_charts.extended_sources.near_surface_fields",return_value=surface), \
                patch("public_charts.extended_sources.collect_rainfall",side_effect=AssertionError("No accumulation at zero")):
            fields,metadata=winter_fields(extra,base,0,0)
        extra.get.assert_called_once_with(0,"geopotential_1000")
        self.assertTrue(np.isfinite(fields["wet_bulb_2m"]).all())
        self.assertFalse(np.any(fields["snowfall_water_equivalent"]))
        self.assertFalse(np.any(fields["snowfall_depth_diagnostic"]))
        self.assertIn("zero-length",metadata["snowfall_source"])

    def test_zero_precipitation_title_uses_the_standard_empty_window(self):
        from public_charts.chart_titles import product_title
        for product in ("surfce","acptot","acptot_snow","acptot_snowdepth"):
            self.assertTrue(product_title(product,"hkor",0,0).endswith("[000-000]"))

    def test_pending_rain_does_not_suppress_upper_and_streamline_charts(self):
        entries = []
        def collect(*args, **kwargs):
            if kwargs.get("include_precipitation") is False:
                return self.base, {}, {}
            raise NotReady("Rain not published yet")
        with patch.object(producer, "collect", side_effect=collect), patch.object(producer, "render", side_effect=self.picture):
            result = producer.produce_lead("gfs", "2026111500", 24, self.root, set(),
                                          lambda product, domain, path, alias_of=None: entries.append((product, domain)))
        self.assertFalse(result["complete"])
        self.assertEqual(len(entries), 14)
        self.assertIn(("wnd850", "asia"), entries)

    def test_lossless_encoder_preserves_pixels(self):
        original = self.picture()
        path = self.root / "chart.webp"
        producer.encode(original, path)
        with Image.open(path) as decoded:
            self.assertEqual(decoded.format, "WEBP")
            np.testing.assert_array_equal(np.asarray(original), np.asarray(decoded.convert("RGB")))

    def test_winter_composites_match_the_operational_comparison_size(self):
        panels=[self.picture() for _ in range(3)]
        self.assertEqual(producer.compose(panels,False).size,(1750,660))
        self.assertEqual(producer.compose(panels,True).size,(600,2000))

    def test_rain_prefix_reuses_previous_native_intervals(self):
        extra = ExtraFields(self.root, "gfs", "2026111500")
        field = Decoded(np.ones((2, 2)), self.base["latitude"], self.base["longitude"], {})
        with patch("public_charts.extended_sources.collect_rainfall", return_value=(field.values, field, [])) as collect:
            first = extra.total_rain(6)
            second = extra.total_rain(12)
            self.assertEqual(collect.call_count, 4)
            np.testing.assert_array_equal(first.values, np.full((2, 2), 2.))
            np.testing.assert_array_equal(second.values, np.full((2, 2), 4.))
            again = extra.total_rain(12)
            self.assertEqual(collect.call_count, 4)
            np.testing.assert_array_equal(second.values, again.values)

    def test_checksum_corruption_rejects_checkpoint(self):
        extra = ExtraFields(self.root, "gfs", "2026111500")
        extra.save_checkpoint("rain/003.npz", {"values": np.array([1.])})
        (extra.checkpoints / "rain/003.npz").write_bytes(b"corrupt")
        self.assertIsNone(extra.checkpoint("rain/003.npz"))

    def test_prune_derived_checkpoints_only(self):
        root = self.root / "checkpoints"
        cycles = policy.cycle_candidates("cmc", datetime(2026, 11, 16, tzinfo=timezone.utc), 8)
        for cycle in cycles:
            (root / cycle / "cmc").mkdir(parents=True)
        outside = self.root / "personal.txt"
        outside.write_text("untouched")
        prune_checkpoints(root)
        self.assertEqual(len(list(root.iterdir())), 6)
        self.assertEqual(outside.read_text(), "untouched")


class CleanupTests(unittest.TestCase):
    def setUp(self):
        self.manifest = policy.public_manifest([row(file_id="keep")])
        self.plan = {"namespace": "cds-public-charts-v1", "folder_id": "folder",
                     "manifest_sha256": hashlib.sha256(manifest_bytes(self.manifest)).hexdigest(),
                     "delete_ids": ["expired"]}
        self.deleted = []
        from unittest.mock import Mock
        self.store = Mock(folder_id="folder")
        self.store.read_json.side_effect = lambda name, default: self.manifest if name == "manifest.json" else {}
        self.store.inventory.return_value = [{"id": "expired", "appProperties": {"kind": "image"}}]
        self.store.delete_managed.side_effect = self.deleted.append

    def test_only_after_exact_publication(self):
        with self.assertRaises(ValueError):
            finalize_cleanup(self.store, self.manifest, self.plan, {})
        self.assertEqual(self.deleted, [])
        self.assertEqual(finalize_cleanup(self.store, self.manifest, self.plan, self.manifest, grace_seconds=0), 1)
        self.assertEqual(self.deleted, ["expired"])

    def test_publication_grace_period_preserves_cached_links(self):
        state={}
        self.store.read_json.side_effect=lambda name, default: self.manifest if name=="manifest.json" else state
        self.store.write_json.side_effect=lambda name, payload: state.update(payload)
        self.assertEqual(finalize_cleanup(self.store,self.manifest,self.plan,self.manifest,now=1000),0)
        self.assertEqual(self.deleted,[])
        self.assertEqual(state["pending_delete_after"],{"expired":1600})
        self.assertEqual(finalize_cleanup(self.store,self.manifest,self.plan,self.manifest,now=1601),1)
        self.assertEqual(self.deleted,["expired"])

    def test_retained_files_and_private_json_are_never_deleted(self):
        for file_id in ("keep", "state"):
            self.plan["delete_ids"] = [file_id]
            self.store.inventory.return_value = [{"id": "state", "appProperties": {"kind": "json"}}]
            with self.assertRaises(ValueError):
                finalize_cleanup(self.store, self.manifest, self.plan, self.manifest)
        self.assertEqual(self.deleted, [])

    def test_wrong_folder_or_changed_manifest_blocks_cleanup(self):
        self.plan["folder_id"] = "vtg-folder"
        with self.assertRaises(ValueError):
            finalize_cleanup(self.store, self.manifest, self.plan, self.manifest)
        self.assertEqual(self.deleted, [])


if __name__ == "__main__":
    unittest.main()
