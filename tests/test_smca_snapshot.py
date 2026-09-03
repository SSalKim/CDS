import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import VTG
import vtg_auto


def smca_text(
    *,
    cycle: str,
    pressure: int = 990,
    typhoon_id: str = "202618",
    model_id: str = "AICON",
) -> str:
    return json.dumps({
        "code": 200,
        "data": {
            "ident": typhoon_id,
            "points": [{
                "forecast": [{
                    "sets": model_id,
                    "init_time_utc": cycle,
                    "points": [
                        {"forecastTime": 0, "lat": 15.0, "lng": 145.0, "pressure": pressure, "speed": 20.0},
                        {"forecastTime": 6, "lat": 15.5, "lng": 144.5, "pressure": pressure - 2, "speed": 22.0},
                        {"forecastTime": 12, "lat": 16.0, "lng": 144.0, "pressure": pressure - 4, "speed": 24.0},
                    ],
                }],
            }],
        },
    })


class SmcaSnapshotTests(unittest.TestCase):
    def settings(self, output_root: Path) -> VTG.Settings:
        return VTG.Settings(
            typ_number=18,
            typ_name="SAUDEL",
            storm_stage="TYP",
            storm_year="2026",
            data_time="202608210000",
            fcst_hours=240,
            output_root=output_root,
        )

    def test_live_aicon_is_saved_and_restored_after_live_cycle_advances(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(Path(directory))
            live_text = smca_text(cycle="2026-08-21T00:00:00Z")

            with patch("VTG.fetch_text", return_value=live_text) as fetch:
                live_frame = VTG.fetch_smca_data(object(), settings)

            self.assertEqual(3, len(live_frame[live_frame["SRC"].eq("AICON")]))
            self.assertIsNone(fetch.call_args.kwargs["cache_dir"])
            snapshot_path = VTG.smca_snapshot_path(settings, "AICON")
            self.assertTrue(snapshot_path.exists())

            advanced_text = smca_text(cycle="2026-08-21T06:00:00Z")
            with patch("VTG.fetch_text", return_value=advanced_text):
                restored_frame = VTG.fetch_smca_data(object(), settings)

            restored = restored_frame[restored_frame["SRC"].eq("AICON")]
            self.assertEqual(3, len(restored))
            self.assertEqual([0.0, 6.0, 12.0], restored["TMD"].tolist())

    def test_aifsm_maps_to_aifs_eps_and_is_saved_for_cycle_restore(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(Path(directory))
            live_text = smca_text(cycle="2026-08-21T00:00:00Z", model_id="AIFSM")

            with patch("VTG.fetch_text", return_value=live_text):
                live_frame = VTG.fetch_smca_data(object(), settings)

            aifs_eps = live_frame[live_frame["SRC"].eq("ECMWF_AIFS_EPS")]
            self.assertEqual(3, len(aifs_eps))
            self.assertEqual(["AIFSM"], aifs_eps[VTG.RAW_MODEL_COLUMN].unique().tolist())
            self.assertTrue(VTG.smca_snapshot_path(settings, "AIFSM").exists())

            advanced_text = smca_text(cycle="2026-08-21T06:00:00Z", model_id="AIFSM")
            with patch("VTG.fetch_text", return_value=advanced_text):
                restored_frame = VTG.fetch_smca_data(object(), settings)

            restored = restored_frame[restored_frame["SRC"].eq("ECMWF_AIFS_EPS")]
            self.assertEqual([0.0, 6.0, 12.0], restored["TMD"].tolist())

    def test_aifsm_priority_is_after_polarwx_and_before_ral_and_knackwx(self):
        settings = self.settings(Path("."))
        smca = VTG.read_smca_json(
            smca_text(cycle="2026-08-21T00:00:00Z", model_id="AIFSM"),
            settings,
            typhoon_id="202618",
        )
        polarwx = smca.copy()
        polarwx[VTG.DATA_SOURCE_COLUMN] = "POLARWX"
        ral = smca.copy()
        ral[VTG.DATA_SOURCE_COLUMN] = "RAL.UCAR"
        knackwx = smca.copy()
        knackwx[VTG.DATA_SOURCE_COLUMN] = "KNACKWX"

        selected = VTG.select_model_sources_by_priority(
            pd.concat([knackwx, ral, smca, polarwx], ignore_index=True),
            settings,
        )
        self.assertEqual(["POLARWX"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

        selected = VTG.select_model_sources_by_priority(
            pd.concat([knackwx, ral, smca], ignore_index=True),
            settings,
        )
        self.assertEqual(["SMCA.FUN"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

    def test_snapshot_skips_identical_content_and_refreshes_changed_content(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(Path(directory))
            typhoon_id = "202618"
            initial_text = smca_text(cycle="2026-08-21T00:00:00Z")

            path, updated = VTG.update_smca_cycle_snapshot(
                initial_text,
                settings,
                typhoon_id=typhoon_id,
                raw_model="AICON",
            )
            self.assertTrue(updated)
            self.assertIsNotNone(path)
            initial_bytes = path.read_bytes()

            same_path, updated = VTG.update_smca_cycle_snapshot(
                initial_text,
                settings,
                typhoon_id=typhoon_id,
                raw_model="AICON",
            )
            self.assertFalse(updated)
            self.assertEqual(path, same_path)
            self.assertEqual(initial_bytes, path.read_bytes())

            changed_text = smca_text(cycle="2026-08-21T00:00:00Z", pressure=985)
            _, updated = VTG.update_smca_cycle_snapshot(
                changed_text,
                settings,
                typhoon_id=typhoon_id,
                raw_model="AICON",
            )
            self.assertTrue(updated)
            self.assertNotEqual(initial_bytes, path.read_bytes())

            rejected_path, updated = VTG.update_smca_cycle_snapshot(
                smca_text(cycle="2026-08-21T00:00:00Z", typhoon_id="202619"),
                settings,
                typhoon_id=typhoon_id,
                raw_model="AICON",
            )
            self.assertIsNone(rejected_path)
            self.assertFalse(updated)

    def test_changed_paths_include_smca_snapshots(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            aicon_path = root / "AICON" / "202608210000.json"
            aifsm_path = root / "AIFSM" / "202608210000.json"
            aicon_path.parent.mkdir(parents=True)
            aifsm_path.parent.mkdir(parents=True)
            aicon_path.write_text("{}\n", encoding="utf-8")
            aifsm_path.write_text("{}\n", encoding="utf-8")

            paths = vtg_auto.collect_changed_asset_paths(
                run_entries=[{
                    "result": {
                        "metadata": {
                            "smca_aicon_snapshot_path": str(aicon_path),
                            "smca_aifsm_snapshot_path": str(aifsm_path),
                        },
                    },
                }],
                manifest_path=root / "manifest.json",
                status_path=root / "status.json",
                split_manifest_paths=[],
            )

            self.assertIn(vtg_auto.relative_asset_path(aicon_path), paths)
            self.assertIn(vtg_auto.relative_asset_path(aifsm_path), paths)
            compact = vtg_auto.compact_metadata({
                "smca_aicon_snapshot_path": str(aicon_path),
                "smca_aifsm_snapshot_path": str(aifsm_path),
            })
            self.assertEqual(str(aicon_path), compact["smca_aicon_snapshot_path"])
            self.assertEqual(str(aifsm_path), compact["smca_aifsm_snapshot_path"])


if __name__ == "__main__":
    unittest.main()
