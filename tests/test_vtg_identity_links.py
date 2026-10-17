import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import vtg_archive_state as archive
import vtg_auto as auto
import vtg_identity_links as identity
import vtg_source_backup as backup


START = "202610150600"
BEFORE = "202610150000"
CYCLE = "202610170000"
ATCF = "wp292026"


def job(stage, number, *, data_time=CYCLE):
    td = stage == "TD"
    return auto.StormJob(
        storm_key=f"{stage.lower()}_2026_{number:02d}", stage=stage + "_LINKED", year=2026,
        data_time=data_time, td_number=number if td else None, linked_td_number=None,
        linked_typ_number=None, canonical_storm_stage=stage, canonical_typ_number=number,
        canonical_typ_name="NONAME" if td else "CHAMPI", canonical_typ_name_ko="",
        typ_number=number, data_typ_number=number, typ_name_ko="", typ_name="NONAME" if td else "CHAMPI",
        typ_en="" if td else "CHAMPI", atcf_id=ATCF, skip_atcf=False,
        atcf_match_method="position" if td else "sector_name",
    )


def td_row(number=58, typ=0):
    return {"YY": "2026", "TD": str(number), "TYP": str(typ), "TM_ST": "202610111800", "TM_ED": "210012310000"}


def typ_row():
    return {"YY": "2026", "SEQ": "30", "NOW": "1", "TM_ST": START,
            "TM_ED": "210012310000", "TYP_EN": "CHAMPI", "TYP_NAME": ""}


def link():
    return {"year": 2026, "td_number": 58, "typ_number": 30, "typ_name": "CHAMPI",
            "atcf_id": ATCF, "effective_time_utc": START, "state": "provisional"}


class IdentityInferenceTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.td, self.typ = job("TD", 58), job("TYP", 30)
        self.registry = {"version": 1, "links": []}
        self.status = {"cycles": {BEFORE: {"td_2026_58_240h": {
            "atcf_id": ATCF, "metadata": {"model_count": 10}, "last_status": "ok",
        }}}}
        self.history(self.td, BEFORE, 10.7, 159.4)
        self.history(self.typ, START, 10.9, 158.3)

    def history(self, target, time, lat, lon, source="KMA_OFFICIAL"):
        path = auto.system_dir_from_job(self.root, target) / "metadata/track_history.json"
        auto.write_json(path, {"aliases": ["td_2026_99"], "points": [
            {"time_utc": time, "lat": lat, "lon": lon, "source": source},
        ]})

    def infer(self, jobs=None, rows=None):
        with redirect_stdout(io.StringIO()):
            return auto.infer_provisional_td_links(
                jobs or [self.td, self.typ], td_rows=rows or [td_row()], typ_rows=[typ_row()],
                status=self.status, identity_links=self.registry, output_root=self.root, gts_text=None,
            )

    def test_same_identity_and_official_analysis_confirm_reversible_link(self):
        source = td_row()
        jobs = self.infer(rows=[source])
        self.assertEqual(["typ_2026_30"], [item.storm_key for item in jobs])
        self.assertEqual(58, jobs[0].linked_td_number)
        self.assertEqual(START, jobs[0].td_typ_link["effective_time_utc"])
        self.assertEqual("0", source["TYP"], "Official list data must not be rewritten.")
        self.assertEqual("provisional", self.registry["links"][0]["state"])
        self.assertTrue((auto.system_dir_from_job(self.root, self.td) / "metadata/track_history.json").exists())

    def test_first_typ_analysis_can_come_from_current_official_gts(self):
        (auto.system_dir_from_job(self.root, self.typ) / "metadata/track_history.json").unlink()
        text = ",".join(f"0 2026 30 0 0 {START} {START} 10.9 158.3 - -9 1000 20 -9 -9 -9 - -9 KMA".split())
        with redirect_stdout(io.StringIO()):
            result = auto.infer_provisional_td_links(
                [self.td, self.typ], td_rows=[td_row()], typ_rows=[typ_row()], status=self.status,
                identity_links=self.registry, output_root=self.root, gts_text=text,
            )
        self.assertEqual(["typ_2026_30"], [item.storm_key for item in result])

    def test_official_link_to_other_typ_cannot_be_overridden_by_inference(self):
        self.assertEqual(2, len(self.infer(rows=[td_row(typ=29)])))
        self.assertEqual([], self.registry["links"])

    def test_registry_is_persisted_and_reported_by_automation_but_not_dry_run(self):
        for dry_run in (True, False):
            self.registry = {"version": 1, "links": []}
            changed = self.root / "changed.txt"
            cache = self.root / "cache"
            argv = ["vtg_auto.py", "--auth-key", "unused", "--now", CYCLE[:10],
                    "--output-root", str(self.root), "--kma-cache-dir", str(cache),
                    "--changed-paths-file", str(changed)] + (["--dry-run"] if dry_run else [])

            def build(**kwargs):
                inferred = self.infer()
                kwargs["identity_links"].update(self.registry)
                return inferred

            with patch("sys.argv", argv), patch.object(auto, "fetch_td_rows", return_value=[td_row()]), \
                    patch.object(auto, "fetch_typ_rows", return_value=[typ_row()]), \
                    patch.object(auto, "ensure_kma_gts_now_cache", return_value=None), \
                    patch.object(auto, "build_storm_jobs", side_effect=build), \
                    patch.object(auto, "run_vtg_batch", return_value={120: {"status": "dry_run"}, 240: {"status": "dry_run"}}), \
                    redirect_stdout(io.StringIO()):
                self.assertEqual(0, auto.main())
            path = cache / identity.LINKS_FILENAME
            self.assertEqual(not dry_run, path.exists())
            if not dry_run:
                self.assertEqual(58, json.loads(path.read_text())["links"][0]["td_number"])
                self.assertIn(auto.relative_asset_path(path), changed.read_text().splitlines())

    def test_same_position_without_same_atcf_is_not_enough(self):
        result = self.infer(jobs=[replace(self.td, atcf_id="wp282026"), self.typ])
        self.assertEqual(2, len(result))
        self.assertEqual([], self.registry["links"])

    def test_same_atcf_without_position_continuity_is_not_enough(self):
        self.history(self.typ, START, 35, 125)
        self.assertEqual(2, len(self.infer()))

    def test_model_or_bdeck_coordinates_are_not_official_evidence(self):
        for source in ("BDECK", "MODEL_0H_MEAN", "APIHUB_MODEL_0H_MEAN"):
            self.history(self.typ, START, 10.9, 158.3, source)
            self.assertEqual(2, len(self.infer()), source)

    def test_old_status_and_unverified_typ_identity_cannot_link(self):
        self.status["cycles"]["202610141800"] = self.status["cycles"].pop(BEFORE)
        self.assertEqual(2, len(self.infer()))
        self.status["cycles"][BEFORE] = self.status["cycles"].pop("202610141800")
        self.assertEqual(2, len(self.infer(jobs=[self.td, replace(self.typ, atcf_match_method="position")])))

    def test_ambiguous_td_candidates_are_not_automatically_linked(self):
        other = job("TD", 59)
        self.history(other, BEFORE, 10.8, 159.3)
        self.status["cycles"][BEFORE]["td_2026_59_240h"] = self.status["cycles"][BEFORE]["td_2026_58_240h"]
        self.assertEqual(3, len(self.infer(jobs=[self.td, other, self.typ], rows=[td_row(), td_row(59)])))
        self.assertEqual([], self.registry["links"])

    def test_later_td_episode_and_manual_id_are_not_absorbed(self):
        row = {**td_row(), "TM_ST": "202610160000"}
        self.assertEqual(2, len(self.infer(rows=[row])))
        self.assertEqual(2, len(self.infer(jobs=[replace(self.td, atcf_match_method="manual"), self.typ])))

    def test_known_link_is_used_by_lightweight_precheck(self):
        self.registry["links"] = [link()]
        with redirect_stdout(io.StringIO()):
            jobs = auto.build_storm_jobs(
                now=auto.parse_utc_stamp("202610170500"), data_time=CYCLE, td_rows=[td_row()], typ_rows=[typ_row()],
                manual_map={}, auth_key="unused", atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
                resolve_atcf=False, identity_links=self.registry, output_root=self.root,
            )
        self.assertEqual(["typ_2026_30"], [item.storm_key for item in jobs])
        self.assertEqual(58, jobs[0].linked_td_number)

    def test_before_promotion_keeps_td_label(self):
        self.registry["links"] = [link()]
        with redirect_stdout(io.StringIO()):
            jobs = auto.build_storm_jobs(
                now=auto.parse_utc_stamp(BEFORE), data_time=BEFORE, td_rows=[td_row()], typ_rows=[typ_row()],
                manual_map={}, auth_key="unused", atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
                resolve_atcf=False, identity_links=self.registry, output_root=self.root,
            )
        self.assertEqual(["td_2026_58"], [item.storm_key for item in jobs])
        self.assertEqual("NONAME", jobs[0].typ_name)

    def test_official_pre_typ_link_with_stale_end_does_not_suppress_typ(self):
        with redirect_stdout(io.StringIO()):
            jobs = auto.build_storm_jobs(
                now=auto.parse_utc_stamp(CYCLE), data_time=CYCLE, td_rows=[td_row(typ=30)], typ_rows=[typ_row()],
                manual_map={}, auth_key="unused", atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100, resolve_atcf=False,
            )
        self.assertEqual(["typ_2026_30"], [item.storm_key for item in jobs])


class IdentityLifecycleTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.cache = self.root / "cache"
        self.registry = {"version": 1, "links": [link()]}
        auto.write_json(self.cache / identity.LINKS_FILENAME, self.registry)
        auto.write_json(self.cache / "td_lst_2026.json", {"rows": [td_row()]})
        auto.write_json(self.cache / "typ_lst_2026.json", {"rows": [typ_row()]})

    def test_explicit_official_conflict_disables_link_instead_of_rewriting_it(self):
        result = identity.reconcile_links(self.registry, [td_row(typ=29)], [typ_row()])
        self.assertEqual("conflict", result["links"][0]["state"])
        self.assertEqual([], identity.active_links(result))
        self.assertEqual("0", identity.effective_td_rows([td_row()], [typ_row()], result)[0]["TYP"])

    def test_official_confirmation_and_empty_response(self):
        self.assertEqual("confirmed", identity.reconcile_links(self.registry, [td_row(typ=30)], [typ_row()])["links"][0]["state"])
        self.assertEqual("provisional", identity.reconcile_links(self.registry, [], [])["links"][0]["state"])

    def test_conflicting_time_or_episode_disables_link(self):
        changed = {**typ_row(), "TM_ST": "202610151200"}
        self.assertEqual([], identity.active_links(identity.reconcile_links(self.registry, [td_row()], [changed])))
        changed = {**td_row(), "TM_ST": "202610160000"}
        self.assertEqual([], identity.active_links(identity.reconcile_links(self.registry, [changed], [typ_row()])))

    def test_activity_projection_does_not_mutate_source_rows(self):
        source = td_row()
        projected = identity.effective_td_rows([source], [typ_row()], self.registry)[0]
        self.assertEqual("30", projected["TYP"])
        self.assertEqual(START, projected["TM_ED"])
        self.assertEqual("0", source["TYP"])
        self.assertEqual("210012310000", source["TM_ED"])

    def test_promotion_does_not_trigger_td_dissipation_archive_or_backup_deletion(self):
        now = auto.parse_utc_stamp("202610170500")
        self.assertEqual({}, archive.official_ended_systems(self.cache, now))
        payload = {"version": 1, "storm_key": "td_2026_58", "storm_keys": ["td_2026_58"], "cycle": CYCLE, "rows": []}
        backup.write_snapshot(self.root / "backup", payload)
        with redirect_stdout(io.StringIO()):
            self.assertEqual(1, len(backup.prune(self.root / "backup", self.cache, now=now)["files"]))

    def test_final_typ_end_cleans_both_identity_backups(self):
        ended_typ = {**typ_row(), "NOW": "2", "TM_ED": "202610170000"}
        auto.write_json(self.cache / "typ_lst_2026.json", {"rows": [ended_typ]})
        now = auto.parse_utc_stamp("202610170500")
        self.assertEqual({"typ_2026_30"}, set(archive.official_ended_systems(self.cache, now)))
        for key in ("td_2026_58", "typ_2026_30"):
            backup.write_snapshot(self.root / "backup", {"version": 1, "storm_key": key, "cycle": CYCLE, "rows": []})
        with redirect_stdout(io.StringIO()):
            self.assertEqual({}, backup.prune(self.root / "backup", self.cache, now=now)["files"])

    def test_later_weakened_td_still_protects_typ_from_archive(self):
        rows = [td_row(), {**td_row(59, 30), "TM_ST": "202610170000"}]
        auto.write_json(self.cache / "td_lst_2026.json", {"rows": rows})
        auto.write_json(self.cache / "typ_lst_2026.json", {"rows": [{**typ_row(), "NOW": "2", "TM_ED": "202610170000"}]})
        self.assertEqual({}, archive.official_ended_systems(self.cache, auto.parse_utc_stamp("202610170500")))

    def test_registry_is_in_exact_changed_paths_and_invalid_payload_is_ignored(self):
        self.assertIn(self.cache / identity.LINKS_FILENAME, auto.kma_cache_asset_paths(self.cache, {2026}))
        self.assertEqual(self.registry, identity.load_links(self.cache))
        auto.write_json(self.cache / identity.LINKS_FILENAME, {"version": 1, "links": ["bad", {**link(), "atcf_id": "wp962026"}]})
        self.assertEqual([], identity.load_links(self.cache)["links"])


if __name__ == "__main__":
    unittest.main()
