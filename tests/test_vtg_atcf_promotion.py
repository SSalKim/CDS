import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd
import requests

import VTG
import vtg_auto
from polarwx_cache import save_snapshot


OLD_ID = "wp962026"
NEW_ID = "wp292026"
CYCLE = "202610140600"
PROMOTED = "202610141200"
STORM = "td_2026_57"
OLD_BDECK = "WP,96,2026101400,,BEST,0,162N,1510E,20,1008,DB\nWP,96,2026101406,,BEST,0,165N,1508E,25,1006,DB"
NEW_BDECK = "WP,29,2026101406,,BEST,0,165N,1508E,25,1006,DB\nWP,29,2026101412,,BEST,0,170N,1505E,30,1004,TD"
SECTOR = "29W INVEST 261014 1200 17.0N 150.5E WPAC 30 1004"


def status():
    return {"cycles": {
        "202610140000": {STORM + "_240h": {"atcf_id": OLD_ID}},
        CYCLE: {STORM + "_240h": {"atcf_id": OLD_ID}},
    }}


def adeck(number, model, leads, *, cycle=CYCLE[:10], latitude=16.5):
    return "\n".join(
        f"WP,{number},{cycle},03,{model},{lead},{int(latitude * 10 + lead / 6)}N,1508E,25,1006"
        for lead in leads
    )


class PromotionCycleTests(unittest.TestCase):
    def resolve(self, *, cycle=CYCLE, history=None, new_bdeck=NEW_BDECK, old_bdeck=OLD_BDECK, sectors=SECTOR, current=None):
        with patch.object(vtg_auto, "fetch_bdeck_text_for_data_time", side_effect=lambda identity, **kwargs: {
                OLD_ID: old_bdeck, NEW_ID: new_bdeck,
        }.get(identity)), redirect_stdout(io.StringIO()):
            return vtg_auto.resolve_atcf_promotion_for_cycle(
                current or vtg_auto.AtcfMatch(NEW_ID, "name", point=vtg_auto.TrackPoint(PROMOTED, 17, 150.5)),
                status() if history is None else history,
                storm_keys=[STORM], data_time=cycle,
                sector_entries=vtg_auto.parse_atcf_sector_file(sectors),
            )

    def test_previous_cycle_keeps_invest_even_when_new_bdeck_is_backfilled(self):
        match = self.resolve()
        self.assertEqual(OLD_ID, match.atcf_id)
        self.assertEqual((NEW_ID,), match.extra_atcf_ids)
        self.assertEqual(PROMOTED, match.atcf_transition["effective_time_utc"])
        self.assertIsNone(match.point, "The future 12UTC analysis must not leak into the 06UTC cycle.")

    def test_promoted_cycle_uses_regular_id_with_old_id_as_backup(self):
        match = self.resolve(cycle=PROMOTED)
        self.assertEqual(NEW_ID, match.atcf_id)
        self.assertEqual((OLD_ID,), match.extra_atcf_ids)
        self.assertEqual(PROMOTED, match.point.time_utc)

    def test_already_saved_wrong_regular_id_is_corrected_before_promotion(self):
        history = status()
        history["cycles"][CYCLE][STORM + "_240h"] = {"atcf_id": NEW_ID}
        history["cycles"][CYCLE][STORM + "_120h"] = {"atcf_id": NEW_ID}
        for method in ("position", "previous_status", "previous_regular_name"):
            with self.subTest(method=method):
                match = self.resolve(history=history, current=vtg_auto.AtcfMatch(NEW_ID, method))
                self.assertEqual(OLD_ID, match.atcf_id)
                self.assertEqual((NEW_ID,), match.extra_atcf_ids)
                self.assertEqual(PROMOTED, match.atcf_transition["effective_time_utc"])

    def test_stored_transition_controls_backfill_and_stops_invest_alias_after_promotion(self):
        transition = self.resolve().atcf_transition
        history = status()
        history["cycles"][PROMOTED] = {STORM + "_240h": {
            "atcf_id": NEW_ID, "metadata": {"atcf_transition": transition},
        }}
        old = self.resolve(history=history, sectors="")
        self.assertEqual((OLD_ID, (NEW_ID,)), (old.atcf_id, old.extra_atcf_ids))
        later = self.resolve(cycle="202610141800", history=history, sectors="")
        self.assertEqual(NEW_ID, later.atcf_id)
        self.assertEqual((), later.extra_atcf_ids)

    def test_close_adjacent_six_hour_points_can_confirm_transition(self):
        new_only_after_promotion = NEW_BDECK.splitlines()[-1]
        self.assertEqual(OLD_ID, self.resolve(new_bdeck=new_only_after_promotion).atcf_id)

    def test_different_systems_or_missing_evidence_do_not_create_aliases(self):
        for changes in (
            {"new_bdeck": NEW_BDECK.replace("165N,1508E", "350N,1200E").replace("170N,1505E", "355N,1200E")},
            {"old_bdeck": ""}, {"sectors": ""},
            {"new_bdeck": NEW_BDECK.replace("WP,29,", "WP,28,")},
        ):
            with self.subTest(changes=changes):
                match = self.resolve(**changes)
                self.assertEqual(OLD_ID, match.atcf_id)
                self.assertEqual((), match.extra_atcf_ids)
                self.assertIsNone(match.atcf_transition)

    def test_no_cross_storm_status_reuse_or_manual_override(self):
        history = {"cycles": {CYCLE: {"td_2026_58_240h": {"atcf_id": OLD_ID}}}}
        self.assertEqual(NEW_ID, self.resolve(history=history).atcf_id)
        manual = vtg_auto.AtcfMatch(NEW_ID, "manual")
        self.assertIs(manual, self.resolve(current=manual))
        other_year = SECTOR.replace("261014", "251014")
        self.assertIsNone(self.resolve(sectors=other_year).atcf_transition)

    def test_erroneous_later_invest_record_does_not_undo_established_regular_id(self):
        history = status()
        history["cycles"]["202610140000"][STORM + "_240h"]["atcf_id"] = NEW_ID
        for method in ("sector_position", "previous_regular_name"):
            current = vtg_auto.AtcfMatch(NEW_ID, method)
            match = self.resolve(history=history, current=current)
            self.assertIs(current, match)
            self.assertEqual(NEW_ID, match.atcf_id)
            self.assertEqual((), match.extra_atcf_ids)

    def test_recorded_transition_survives_status_compaction(self):
        transition = self.resolve().atcf_transition
        record = {"atcf_id": OLD_ID, "atcf_transition": transition, "metadata": {"atcf_transition": transition}}
        compact = vtg_auto.compact_status_record(record)
        self.assertEqual(transition, compact["atcf_transition"])
        self.assertEqual(transition, compact["metadata"]["atcf_transition"])

    def test_transition_is_saved_into_generated_metadata_and_status(self):
        match = self.resolve()
        job = vtg_auto.StormJob(
            storm_key=STORM, stage="TD_POSITION_ATCF", year=2026, data_time=CYCLE,
            td_number=57, linked_td_number=None, linked_typ_number=None,
            canonical_storm_stage="TD", canonical_typ_number=57,
            canonical_typ_name="NONAME", canonical_typ_name_ko="",
            typ_number=57, data_typ_number=57, typ_name_ko="", typ_name="NONAME", typ_en="",
            atcf_id=match.atcf_id, skip_atcf=False, extra_atcf_ids=match.extra_atcf_ids,
            atcf_transition=match.atcf_transition,
        )
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            metadata_path = vtg_auto.metadata_path_for(root, job, 120)

            def generate(*args, **kwargs):
                vtg_auto.write_json(metadata_path, {"data_time": CYCLE, "fcst_hours": 120, "no_output": True})
                return SimpleNamespace(returncode=0, stdout="", stderr="")

            with patch.object(vtg_auto, "run_command_with_network_retry", side_effect=generate), redirect_stdout(io.StringIO()):
                results = vtg_auto.run_vtg_batch(
                    job=job, output_root=root, auth_key="test-key", fallback_auth_key="", python="python",
                    fcst_hours_list=[120], auto_fcst_hours=False, source_overrides=[], dry_run=False,
                )
            self.assertEqual(match.atcf_transition, json.loads(metadata_path.read_text())["atcf_transition"])
            cycle_status = {}
            vtg_auto.record_batch_results(
                job=job, window=vtg_auto.CycleWindow(CYCLE, CYCLE, CYCLE, PROMOTED), due_hours=[120],
                batch_results=results, output_root=root, cycle_status=cycle_status, run_entries=[],
                complete_model_count=40, final_check_window=False, now=vtg_auto.parse_utc_stamp(PROMOTED),
            )
            compacted = vtg_auto.prune_status_for_persistence(
                {"cycles": {CYCLE: cycle_status}}, active_data_times={CYCLE}, retention_days=30,
                reference_time=vtg_auto.parse_utc_stamp(PROMOTED),
            )
            self.assertEqual(match.atcf_transition, compacted["cycles"][CYCLE][STORM + "_120h"]["atcf_transition"])

    def test_job_and_renderer_command_use_cycle_identity_backups_and_exact_analysis(self):
        td_rows = [{"YY": "2026", "TD": "57", "TYP": "0", "TM_ST": "202610111200", "TM_ED": "210012310000"}]
        current = vtg_auto.AtcfMatch(NEW_ID, "position", point=vtg_auto.TrackPoint(CYCLE, 16.5, 150.8), distance_km=0)
        with patch.object(vtg_auto, "fetch_atcf_sector_entries", return_value=vtg_auto.parse_atcf_sector_file(SECTOR)), \
                patch.object(vtg_auto, "fetch_kma_reference_point", return_value=vtg_auto.TrackPoint(CYCLE, 16.5, 150.8)), \
                patch.object(vtg_auto, "find_atcf_sector_position_match", return_value=None), \
                patch.object(vtg_auto, "find_atcf_position_match", return_value=current), \
                patch.object(vtg_auto, "fetch_bdeck_text_for_data_time", side_effect=lambda identity, **kwargs: OLD_BDECK if identity == OLD_ID else NEW_BDECK), \
                patch.object(vtg_auto, "fetch_bdeck_analysis_point", return_value=None) as analysis, \
                redirect_stdout(io.StringIO()):
            jobs = vtg_auto.build_storm_jobs(
                now=vtg_auto.parse_utc_stamp("202610141500"), data_time=CYCLE,
                td_rows=td_rows, typ_rows=[], manual_map={}, auth_key="test-key", status=status(),
                atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
            )
        self.assertEqual(1, len(jobs))
        job = jobs[0]
        self.assertEqual((OLD_ID, (NEW_ID,)), (job.atcf_id, job.extra_atcf_ids))
        self.assertTrue(job.require_exact_analysis)
        analysis.assert_called_once_with(OLD_ID, data_time=CYCLE, max_offset_hours=0)
        command, _ = vtg_auto.vtg_command(
            job=job, output_root=Path("data"), auth_key="test-key", fallback_auth_key="", python="python",
            fcst_hours_list=[120, 240], auto_fcst_hours=False, source_overrides=[],
        )
        self.assertEqual(NEW_ID, command[command.index("--extra-atcf-ids") + 1])
        self.assertIn("--require-exact-analysis", command)

    def test_named_typ_job_uses_explicit_td_link_to_find_transition_history(self):
        td_rows = [{"YY": "2026", "TD": "57", "TYP": "30", "TM_ST": "202610111200", "TM_ED": "202610140000"}]
        typ_rows = [{"YY": "2026", "SEQ": "30", "NOW": "1", "TYP_EN": "TEST",
                     "TYP_NAME": "", "TM_ST": CYCLE, "TM_ED": "210012310000"}]
        with patch.object(vtg_auto, "fetch_atcf_sector_entries", return_value=vtg_auto.parse_atcf_sector_file(SECTOR)), \
                patch.object(vtg_auto, "find_atcf_sector_name_match", return_value=vtg_auto.AtcfMatch(NEW_ID, "name")), \
                patch.object(vtg_auto, "fetch_bdeck_text_for_data_time", side_effect=lambda identity, **kwargs: OLD_BDECK if identity == OLD_ID else NEW_BDECK), \
                patch.object(vtg_auto, "fetch_bdeck_analysis_point", return_value=None), redirect_stdout(io.StringIO()):
            jobs = vtg_auto.build_storm_jobs(
                now=vtg_auto.parse_utc_stamp("202610141500"), data_time=CYCLE,
                td_rows=td_rows, typ_rows=typ_rows, manual_map={}, auth_key="test-key", status=status(),
                atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
            )
        self.assertEqual(1, len(jobs))
        self.assertEqual("typ_2026_30", jobs[0].storm_key)
        self.assertEqual(OLD_ID, jobs[0].atcf_id)
        self.assertEqual((NEW_ID,), jobs[0].extra_atcf_ids)
        self.assertTrue(jobs[0].require_exact_analysis)


class PromotionTrackSelectionTests(unittest.TestCase):
    def settings(self, cycle=CYCLE):
        return VTG.Settings(
            typ_number=57, storm_stage="TD", typ_name="NONAME", data_time=cycle,
            atcf_id=OLD_ID, extra_atcf_ids=(NEW_ID,), fcst_hours=240,
        )

    def fetch(self, texts, *, settings=None, reverse=False):
        specs = [(source, url, 0) for (source, url), _ in texts.items()]
        if reverse:
            specs.reverse()
        with patch.object(VTG, "atcf_urls", return_value=specs), \
                patch.object(VTG, "fetch_text", side_effect=lambda session, url, **kwargs: next(value for (source, key), value in texts.items() if key == url)), \
                redirect_stdout(io.StringIO()):
            return VTG.fetch_atcf_data(requests.Session(), settings or self.settings())

    def test_primary_track_is_whole_and_does_not_get_alternate_longer_tail(self):
        texts = {("KNACKWX", "old"): adeck(96, "AVNO", [0, 6, 12]),
                 ("KNACKWX", "new"): adeck(29, "AVNO", [0, 6, 12, 18, 24], latitude=17)}
        for reverse in (False, True):
            frame = self.fetch(texts, reverse=reverse)
            self.assertEqual({96}, set(frame["ATCF_NUMBER"]))
            self.assertEqual([0, 6, 12], sorted(frame["FTM"].tolist()))

    def test_missing_model_uses_alternate_same_cycle_not_future_initialization(self):
        texts = {("KNACKWX", "old"): adeck(96, "AVNO", [0, 6]),
                 ("KNACKWX", "new"): "\n".join([
                     adeck(29, "DWIC", [0, 6, 12]),
                     adeck(29, "AIMN", [0, 6], cycle=PROMOTED[:10]),
                     adeck(28, "ICMN", [0, 6]),
                 ])}
        frame = self.fetch(texts)
        self.assertEqual({"AVNO", "DWIC"}, set(frame["MODEL"]))
        self.assertEqual({int(CYCLE[:10])}, set(frame["TM10"]))

    def test_zero_hour_only_primary_does_not_hide_forecast_on_alternate(self):
        frame = self.fetch({("KNACKWX", "old"): adeck(96, "AVNO", [0]),
                            ("KNACKWX", "new"): adeck(29, "AVNO", [0, 6])})
        self.assertEqual({29}, set(frame["ATCF_NUMBER"]))

    def test_invalid_knackwx_primary_does_not_hide_usable_alternate(self):
        for leads in ([132, 138], [0, 24]):
            frame = self.fetch({("KNACKWX", "old"): adeck(96, "AVNO", leads),
                                ("KNACKWX", "new"): adeck(29, "AVNO", [0, 6])})
            self.assertEqual({29}, set(frame["ATCF_NUMBER"]))

    def test_each_source_remains_independent_for_source_priority(self):
        frame = self.fetch({("KNACKWX", "old"): adeck(96, "AVNO", [0, 6]),
                            ("KNACKWX", "new"): adeck(29, "AVNO", [0, 6])})
        extra = VTG.read_atcf_csv(adeck(29, "AVNO", [0, 6], latitude=16.7), source="RAL.UCAR")
        extra["_ATCF_ID"] = NEW_ID
        combined = pd.concat([frame, extra], ignore_index=True)
        chosen = VTG.select_atcf_identity_tracks(combined, self.settings(), model_column="MODEL", lead_column="FTM")
        self.assertEqual({"KNACKWX", "RAL.UCAR"}, set(chosen[VTG.DATA_SOURCE_COLUMN]))
        converted = VTG.atcf_to_kma_schema(chosen, self.settings())
        selected = VTG.select_model_sources_by_priority(converted, self.settings())
        self.assertEqual({"RAL.UCAR"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_cycle_and_storm_guard_also_applies_when_converting_raw_data(self):
        raw = VTG.read_atcf_csv("\n".join([
            adeck(96, "AVNO", [0, 6]), adeck(29, "AVNO", [0, 6], cycle=PROMOTED[:10]), adeck(28, "AVNO", [0, 6]),
        ]), source="KNACKWX")
        frame = VTG.atcf_to_kma_schema(raw, self.settings())
        self.assertEqual(2, len(frame))
        self.assertEqual({CYCLE}, set(frame["TYP_TM(UTC)"]))

    def test_polarwx_models_also_use_whole_identity_tracks(self):
        def model(leads, latitude):
            return {"fhr": leads, "lat": [latitude] * len(leads), "lon": [150.8] * len(leads)}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_snapshot(root, OLD_ID, CYCLE, json.dumps({"gfs": model([0, 6], 16.5)}))
            save_snapshot(root, NEW_ID, CYCLE, json.dumps({"gfs": model([0, 6, 12], 17), "icon": model([0, 6], 16.5)}))
            with patch.object(VTG, "queue_request"), redirect_stdout(io.StringIO()):
                frame = VTG.fetch_polarwx_data(requests.Session(), self.settings(), cache_root=root)
        self.assertEqual({"GFS", "ICON"}, set(frame["SRC"]))
        self.assertEqual([0, 6], frame.loc[frame["SRC"].eq("GFS"), "TMD"].tolist())
        self.assertEqual({16.5}, set(frame["LAT"]))


if __name__ == "__main__":
    unittest.main()
