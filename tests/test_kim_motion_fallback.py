import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

import VTG


# TD 2653, 2026-09-14 00 UTC: APIHUB coordinates supplied for the regression.
KIM_POINTS = [
    (0, 12.3, 154.5), (3, 13.7, 152.6), (6, 13.6, 152.1),
    (9, 13.9, 152.2), (12, 15.6, 154.6), (15, 15.6, 153.3),
    (18, 15.6, 153.7), (21, 16.1, 153.8), (24, 16.3, 152.5),
    (27, 15.8, 151.4), (30, 15.1, 151.1), (33, 14.7, 151.3),
    (36, 14.7, 151.8), (39, 17.3, 152.2), (42, 15.7, 153.5),
    (45, 17.2, 153.6), (48, 18.1, 153.1), (51, 18.8, 152.8),
    (54, 19.2, 152.6), (57, 19.9, 152.8), (60, 19.9, 152.1),
    (63, 21.0, 150.8), (66, 21.2, 151.2), (69, 22.0, 150.0),
    (72, 21.9, 149.5), (75, 22.4, 149.2), (78, 22.6, 148.1),
    (81, 22.3, 147.9), (84, 23.2, 147.4), (90, 23.0, 145.7),
    (96, 22.9, 144.2), (102, 23.3, 142.7), (108, 23.4, 141.1),
    (114, 23.7, 139.5), (120, 24.1, 137.9), (126, 24.4, 136.5),
    (132, 24.7, 134.9), (138, 24.5, 133.9), (144, 24.7, 132.9),
    (150, 24.9, 131.7), (156, 24.8, 130.8), (162, 25.3, 129.8),
    (168, 25.2, 129.0), (174, 25.5, 128.7), (180, 26.2, 128.3),
    (186, 26.9, 127.8), (192, 27.5, 127.7), (198, 28.5, 128.1),
    (204, 29.5, 128.4), (210, 30.9, 129.5), (216, 33.2, 131.0),
    (222, 33.9, 131.8), (228, 33.2, 133.9), (234, 33.8, 136.6),
    (240, 34.7, 139.1),
]


def kim_frame(model="KIM_3h", points=None):
    points = KIM_POINTS if points is None else points
    if model == "KIM_6h":
        points = [point for point in points if point[0] % 6 == 0]
    frame = pd.DataFrame(points, columns=["TMD", "LAT", "LON"])
    frame["YY"] = 2026
    frame["TYP"] = 53
    frame["SEQ"] = 0
    frame["FT"] = frame["TMD"].gt(0).astype(int)
    frame["TYP_TM(UTC)"] = "202609140000"
    frame["FT_TM(UTC)"] = [
        (datetime(2026, 9, 14) + timedelta(hours=int(lead))).strftime("%Y%m%d%H%M")
        for lead in frame["TMD"]
    ]
    frame["PS"] = 1004
    frame["WS"] = 18
    frame["SRC"] = model
    frame[VTG.DATA_SOURCE_COLUMN] = "APIHUB"
    frame[VTG.RAW_MODEL_COLUMN] = model
    return frame


class KimMotionFallbackTests(unittest.TestCase):
    def apply_qc(self, fine=None, coarse=None):
        fine = kim_frame() if fine is None else fine
        coarse = kim_frame("KIM_6h") if coarse is None else coarse
        with redirect_stdout(io.StringIO()):
            result = VTG.trim_excessive_motion_tracks(pd.concat([fine, coarse], ignore_index=True))
        return result[result["SRC"].eq("KIM_3h")].sort_values("TMD").reset_index(drop=True)

    def test_real_case_recovers_240h_and_preserves_other_3h_points(self):
        fine = kim_frame()
        cutoff, speed = VTG.excessive_motion_cutoff(fine)
        self.assertEqual(12, cutoff)
        self.assertAlmostEqual(106.62928, speed, places=4)
        coarse = kim_frame("KIM_6h")
        coarse.loc[coarse["TMD"].eq(12), ["PS", "WS"]] = [1001, 20]
        result = self.apply_qc(fine, coarse)
        self.assertEqual([lead for lead, _, _ in KIM_POINTS if lead != 9], result["TMD"].tolist())
        self.assertIsNone(VTG.excessive_motion_cutoff(result))
        endpoint = result[result["TMD"].eq(12)].iloc[0]
        self.assertEqual((1001, 20, "KIM_6h"), (endpoint["PS"], endpoint["WS"], endpoint[VTG.RAW_MODEL_COLUMN]))
        self.assertEqual(6, endpoint[VTG.KIM_6H_FALLBACK_START_COLUMN])
        unchanged = result[~result["TMD"].isin([6, 12])][fine.columns].reset_index(drop=True)
        expected = fine[~fine["TMD"].isin([6, 9, 12])].reset_index(drop=True)
        pd.testing.assert_frame_equal(expected, unchanged)

    def test_first_half_of_6h_interval_can_also_be_replaced(self):
        fine = kim_frame()
        fine.loc[fine["TMD"].eq(9), ["LAT", "LON"]] = [16.8, 154.6]
        result = self.apply_qc(fine)
        self.assertNotIn(9, result["TMD"].tolist())
        self.assertEqual(240, result["TMD"].max())

    def test_normal_track_is_unchanged(self):
        fine = kim_frame()
        fine.loc[fine["TMD"].eq(9), ["LAT", "LON"]] = [14.6, 153.35]
        pd.testing.assert_frame_equal(fine, self.apply_qc(fine))

    def test_no_backup_keeps_original_truncation(self):
        result = self.apply_qc(coarse=kim_frame("KIM_6h").iloc[:0])
        self.assertEqual([0, 3, 6, 9], result["TMD"].tolist())

    def test_mismatched_identity_or_source_is_not_used(self):
        for column, value in [
            ("YY", 2025), ("TYP", 54), ("TYP_TM(UTC)", "202609131800"),
            (VTG.DATA_SOURCE_COLUMN, "DMDW"), ("TYP_TM(UTC)", None),
        ]:
            with self.subTest(column=column, value=value):
                coarse = kim_frame("KIM_6h")
                coarse[column] = value
                self.assertEqual(9, self.apply_qc(coarse=coarse)["TMD"].max())

    def test_invalid_or_mismatched_endpoint_is_not_used(self):
        for column, value in [("LAT", float("nan")), ("LON", 999), ("FT_TM(UTC)", "202609141800")]:
            with self.subTest(column=column):
                coarse = kim_frame("KIM_6h")
                coarse.loc[coarse["TMD"].eq(12), column] = value
                self.assertEqual(9, self.apply_qc(coarse=coarse)["TMD"].max())

    def test_missing_endpoint_does_not_expand_to_12h_bridge(self):
        coarse = kim_frame("KIM_6h")
        coarse = coarse[coarse["TMD"].ne(12)]
        self.assertEqual(9, self.apply_qc(coarse=coarse)["TMD"].max())

    def test_missing_fine_endpoint_cannot_restore_a_previously_trimmed_tail(self):
        fine = kim_frame().query("TMD <= 9").copy()
        fine.loc[fine["TMD"].eq(9), ["LAT", "LON"]] = [16.8, 154.6]
        self.assertEqual(6, self.apply_qc(fine)["TMD"].max())

    def test_already_6h_motion_failure_does_not_get_another_fallback(self):
        fine = kim_frame("KIM_6h")
        fine["SRC"] = "KIM_3h"
        fine.loc[fine["TMD"].eq(12), ["LAT", "LON"]] = [20.0, 155.0]
        self.assertEqual(6, self.apply_qc(fine)["TMD"].max())

    def test_later_unrepairable_failure_still_trims_tail(self):
        fine = kim_frame()
        fine.loc[fine["TMD"].eq(90), ["LAT", "LON"]] = [40.0, 140.0]
        result = self.apply_qc(fine)
        self.assertEqual(84, result["TMD"].max())
        self.assertNotIn(9, result["TMD"].tolist())
        self.assertEqual(6, result.loc[result["TMD"].eq(12), VTG.KIM_6H_FALLBACK_START_COLUMN].iloc[0])

    def test_backup_failing_speed_qc_is_not_used(self):
        coarse = kim_frame("KIM_6h")
        coarse.loc[coarse["TMD"].eq(12), ["LAT", "LON"]] = [20.0, 155.0]
        self.assertIsNotNone(VTG.excessive_motion_cutoff(coarse))
        self.assertEqual(9, self.apply_qc(coarse=coarse)["TMD"].max())

    def test_both_splice_boundaries_must_pass(self):
        for lead, lat, lon in [(6, 12.3, 156.0), (12, 15.6, 156.6)]:
            with self.subTest(boundary_lead=lead):
                coarse = kim_frame("KIM_6h")
                coarse.loc[coarse["TMD"].eq(lead), ["LAT", "LON"]] = [lat, lon]
                self.assertIsNone(VTG.excessive_motion_cutoff(coarse))
                self.assertEqual(9, self.apply_qc(coarse=coarse)["TMD"].max())

    def test_adjacent_replacements_keep_both_audit_records(self):
        points = [*KIM_POINTS[:6], (18, 17.8, 155.4), (21, 17.8, 155.5), (24, 18.0, 155.5)]
        result = self.apply_qc(kim_frame(points=points), kim_frame("KIM_6h", points))
        self.assertEqual([0, 3, 6, 12, 18, 21, 24], result["TMD"].tolist())
        audits = result.dropna(subset=[VTG.KIM_6H_FALLBACK_START_COLUMN])
        self.assertEqual([[6, 12], [12, 18]], audits[[VTG.KIM_6H_FALLBACK_START_COLUMN, "TMD"]].values.tolist())

    def test_cannot_repair_two_windows_by_skipping_failing_boundary(self):
        fine = kim_frame()
        fine.loc[fine["TMD"].eq(15), ["LAT", "LON"]] = [12.0, 151.0]
        self.assertEqual(9, self.apply_qc(fine)["TMD"].max())

    def test_other_models_keep_existing_speed_qc(self):
        frame = kim_frame()
        frame["SRC"] = "GFS"
        with redirect_stdout(io.StringIO()):
            result = VTG.trim_excessive_motion_tracks(pd.concat([frame, kim_frame("KIM_6h")]))
        self.assertEqual(9, result.loc[result["SRC"].eq("GFS"), "TMD"].max())

    def test_normalization_and_metadata_include_fallback(self):
        with tempfile.TemporaryDirectory() as directory, redirect_stdout(io.StringIO()):
            root = Path(directory)
            settings = VTG.Settings(
                typ_number=53, storm_stage="TD", storm_year="2026",
                data_time="202609140000", fcst_hours=240, output_root=root,
            )
            raw = pd.concat([kim_frame(), kim_frame("KIM_6h")], ignore_index=True)
            empty = pd.DataFrame()
            result = VTG.normalize_track_data(raw, empty, empty, empty, empty, settings)
            self.assertEqual(240, result.loc[result["SRC"].eq("KIM_3h"), "TMD"].max())
            self.assertIn("KIM_6h", VTG.excluded_models_for(result))
            path = root / "run.json"
            VTG.write_run_metadata(path, target=root / "sample.png", df=result, settings=settings, intensity="TD")
            metadata = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual([{
                "model": "KIM_3h", "fallback_model": "KIM_6h", "source": "APIHUB",
                "start_lead_hour": 6.0, "end_lead_hour": 12.0,
            }], metadata["motion_qc_fallbacks"])


if __name__ == "__main__":
    unittest.main()
