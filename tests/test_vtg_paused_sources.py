import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import VTG
import vtg_source_backup as backup
import vtg_sources


def track(model, source):
    initial = datetime(2026, 10, 27, 12)
    return pd.DataFrame([
        {
            "FT": int(lead > 0), "YY": 2026, "TYP": 31, "SEQ": 0, "TMD": lead,
            "TYP_TM(UTC)": "202610271200",
            "FT_TM(UTC)": (initial + timedelta(hours=lead)).strftime("%Y%m%d%H%M"),
            "LAT": 16.0 + lead / 60, "LON": 140.0, "WS": 20, "PS": 990,
            "SRC": model, VTG.DATA_SOURCE_COLUMN: source, VTG.RAW_MODEL_COLUMN: model,
        }
        for lead in (0, 6, 12)
    ])


class PausedSourceTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(
            typ_number=31, typ_name="IN-FA", storm_year="2026", atcf_id="wp302026",
            data_time="202610271200", fcst_hours=240,
        )

    def test_only_requested_sources_are_paused_and_registry_is_preserved(self):
        self.assertEqual({"DMDW", "RAW.GITHUB"}, VTG.PAUSED_SOURCE_IDS)
        self.assertIs(VTG.PAUSED_SOURCE_IDS, vtg_sources.PAUSED_SOURCE_IDS)
        self.assertTrue(VTG.DMDW_ENABLED_MODEL_IDS)
        self.assertEqual(("GENC", "FNV3", "WNV3"), VTG.RAW_GITHUB_MODELS)
        self.assertEqual(
            ("APIHUB", "POLARWX", "SMCA.FUN", "RAL.UCAR", "EMC.NCEP", "KNACKWX", "WINDBORNE"),
            VTG.source_priority_for_model("GFS", self.settings),
        )

    def test_dmdw_does_not_even_search_for_existing_files(self):
        with patch.object(VTG, "dmdw_candidate_paths") as paths, patch.object(VTG, "read_dmdw_json") as read:
            self.assertTrue(VTG.read_dmdw_data(self.settings).empty)
        paths.assert_not_called()
        read.assert_not_called()

    def test_raw_github_is_not_requested_directly_or_in_atcf_batch(self):
        with patch.object(VTG, "fetch_text") as fetch:
            for model in VTG.RAW_GITHUB_MODELS:
                self.assertIsNone(VTG.fetch_raw_github_text(object(), self.settings, model))
        fetch.assert_not_called()
        with patch.dict("os.environ", {"WB_API_KEY": "test-key"}):
            specs = VTG.atcf_urls(self.settings)
        self.assertEqual({"RAL.UCAR", "EMC.NCEP", "KNACKWX", "WINDBORNE"}, {s[0] for s in specs})
        self.assertFalse(any("raw.githubusercontent.com" in url for _, url, _ in specs))

    def test_old_data_and_explicit_override_cannot_reactivate_paused_sources(self):
        for model, paused_source, fallback in (
            ("GFS", "DMDW", "KNACKWX"),
            ("GENC", "RAW.GITHUB", "POLARWX"),
            ("WNC", "RAW.GITHUB", "SMCA.FUN"),
            ("WNV3", "RAW.GITHUB", "SMCA.FUN"),
        ):
            with self.subTest(model=model):
                settings = replace(self.settings, source_overrides=((model, paused_source),))
                raw = pd.concat([track(model, paused_source), track(model, fallback)], ignore_index=True)
                selected = VTG.select_model_sources_by_priority(raw, settings)
                self.assertEqual({fallback}, set(selected[VTG.DATA_SOURCE_COLUMN]))
                self.assertNotIn(paused_source, VTG.source_priority_for_model(model, settings))
                self.assertEqual([0, 6, 12], selected.TMD.tolist())

    def test_all_paused_data_produces_empty_normalized_guidance(self):
        raw = pd.concat([track("GFS", "DMDW"), track("WNC", "RAW.GITHUB")], ignore_index=True)
        self.assertTrue(VTG.normalize_guidance_frame(raw, self.settings).empty)

    def test_availability_records_exclude_paused_sources(self):
        raw = pd.concat([track("GFS", "APIHUB"), track("GFS", "DMDW"), track("WNC", "RAW.GITHUB")])
        empty = raw.iloc[:0]
        availability = VTG.source_availability_frame(raw, empty, empty, empty, VTG.empty_atcf_frame(), self.settings)
        self.assertEqual({"APIHUB"}, set(availability[VTG.DATA_SOURCE_COLUMN]))

    def test_backup_neither_restores_nor_saves_paused_provider_tracks(self):
        raw = pd.concat([track("GFS", "DMDW"), track("WNC", "RAW.GITHUB"), track("ICON", "POLARWX")], ignore_index=True)
        with tempfile.TemporaryDirectory() as directory:
            settings = replace(self.settings, source_backup_dir=Path(directory))
            keys = VTG.storm_history_keys(settings)
            backup.write_snapshot(settings.source_backup_dir, {
                "version": 1, "storm_key": keys[0], "storm_keys": keys,
                "cycle": settings.data_time, "rows": raw.to_dict("records"),
            })
            with patch.object(VTG, "recent_cycle", return_value=True):
                restored = VTG.merge_source_backups(raw.iloc[:0], settings)
            self.assertEqual({"POLARWX"}, set(restored[VTG.DATA_SOURCE_COLUMN]))
            saved = backup.read_snapshot(settings.source_backup_dir, keys[0], settings.data_time)
            self.assertEqual({"POLARWX"}, {row[VTG.DATA_SOURCE_COLUMN] for row in saved["rows"]})
            with patch.object(VTG, "recent_cycle", return_value=True):
                merged = VTG.merge_source_backups(raw, settings)
            self.assertEqual({"POLARWX"}, set(merged[VTG.DATA_SOURCE_COLUMN]))

    def test_removing_pause_restores_existing_dmdw_loader_and_raw_url_plan(self):
        original = track("GFS", "DMDW")
        with patch.object(VTG, "PAUSED_SOURCE_IDS", frozenset()):
            with patch.object(VTG, "dmdw_candidate_paths", return_value=[Path("preserved.json")]), \
                    patch.object(VTG, "read_dmdw_json", return_value=original):
                loaded = VTG.read_dmdw_data(self.settings)
            self.assertEqual(3, len(loaded))
            self.assertIn("RAW.GITHUB", {s[0] for s in VTG.atcf_urls(self.settings)})
            self.assertEqual(VTG.SOURCE_ORDER, VTG.source_priority_for_model("GFS", self.settings))


if __name__ == "__main__":
    unittest.main()
