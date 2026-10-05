import io
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import pandas as pd

import VTG
import vtg_auto


CYCLE = "202610050000"
SECTOR_TEXT = "15E NOLO 261004 1800 24.0N 179.2W EPAC 100 959"
OLD_BDECK = "EP,15,2026100418,,BEST,0,240N,1792W,100,959,HU"
CURRENT_BDECK = "EP,15,2026100500,,BEST,0,248N,1794E,90,965,HU"


def kma_text(number=28):
    row = [0, 2026, number, 0, 0, CYCLE, CYCLE, 24.8, 179.4,
           "-", -9, 965, 46, -9, -9, -9, "-", -9, "KMA", ""]
    return "#START7777\n#columns\n" + ",".join(map(str, row))


class SectorDatelineTests(unittest.TestCase):
    def setUp(self):
        self.entries = vtg_auto.parse_atcf_sector_file(SECTOR_TEXT)
        self.reference = vtg_auto.TrackPoint(CYCLE, 24.8, 179.4)

    def name_match(self, entries=None, reference=None):
        with redirect_stdout(io.StringIO()):
            return vtg_auto.find_atcf_sector_name_match(
                self.entries if entries is None else entries,
                typ_en="NOLO", year=2026, data_time=CYCLE,
                kma_point=reference or self.reference,
            )

    def test_six_hour_old_name_matches_identity_without_analysis_values(self):
        match = self.name_match()
        self.assertEqual("ep152026", match.atcf_id)
        self.assertEqual("sector_name_recent", match.method)
        self.assertIsNone(match.point)
        self.assertIsNone(match.reference_point)
        self.assertIsNone(match.distance_km)
        self.assertFalse(hasattr(match, "wind_kt"))
        self.assertFalse(hasattr(match, "pressure_hpa"))

    def test_name_match_rejects_older_future_and_different_name_entries(self):
        for stamp in ("202610041759", "202610041200", "202610050600"):
            with self.subTest(stamp=stamp):
                entry = replace(self.entries[0], point=replace(self.entries[0].point, time_utc=stamp))
                self.assertIsNone(self.name_match([entry]))
        self.assertIsNone(self.name_match([replace(self.entries[0], storm_name="RACHEL")]))

    def test_cross_basin_matches_require_dateline_reference(self):
        self.assertIsNone(self.name_match(reference=replace(self.reference, lon=130.0)))
        central = replace(self.entries[0], atcf_id="cp012026", basin="CPAC")
        self.assertEqual("cp012026", self.name_match([central]).atcf_id)

    def test_same_cycle_name_takes_priority_over_preferred_older_id(self):
        current = replace(self.entries[0], atcf_id="cp012026", point=self.reference)
        with redirect_stdout(io.StringIO()):
            match = vtg_auto.find_atcf_sector_name_match(
                [self.entries[0], current], typ_en="NOLO", year=2026,
                data_time=CYCLE, kma_point=self.reference, preferred_atcf_id="ep152026",
            )
        self.assertEqual("cp012026", match.atcf_id)
        self.assertEqual("sector_name", match.method)

    def test_position_match_uses_only_same_cycle_even_across_dateline(self):
        with redirect_stdout(io.StringIO()):
            stale = vtg_auto.find_atcf_sector_position_match(
                self.entries, year=2026, data_time=CYCLE, kma_point=self.reference,
            )
            fresh = vtg_auto.find_atcf_sector_position_match(
                [replace(self.entries[0], point=replace(self.entries[0].point, time_utc=CYCLE))],
                year=2026, data_time=CYCLE, kma_point=self.reference,
            )
        self.assertIsNone(stale)
        self.assertEqual("ep152026", fresh.atcf_id)
        self.assertLess(fresh.distance_km, 200)

    def test_bdeck_search_includes_ep_cp_near_dateline_and_preserves_typ_filter(self):
        original = ["wp282026", "wp902026"]
        with redirect_stdout(io.StringIO()):
            near = vtg_auto.extend_atcf_ids_for_dateline(
                original, year=2026, kma_point=self.reference, sector_entries=self.entries,
            )
            regular = vtg_auto.extend_atcf_ids_for_dateline(
                original, year=2026, kma_point=self.reference, sector_entries=self.entries,
                regular_only=True,
            )
            far = vtg_auto.extend_atcf_ids_for_dateline(
                original, year=2026, kma_point=replace(self.reference, lon=130),
                sector_entries=self.entries,
            )
        self.assertEqual("ep152026", near[0])
        self.assertIn("cp012026", near)
        self.assertIn("ep892026", near)
        self.assertIn("ep902026", near)
        self.assertEqual(len(near), len(set(near)))
        self.assertFalse(any(vtg_auto.is_invest_atcf_id(value) for value in regular))
        self.assertEqual(original, far)


class NoloAnalysisTests(unittest.TestCase):
    def build_job(self, linked_td=False):
        typ_row = {"YY": "2026", "SEQ": "28", "NOW": "1", "TYP_EN": "NOLO",
                   "TYP_NAME": "", "TM_ST": CYCLE, "TM_ED": "210012310000"}
        td_rows = []
        number = 28
        if linked_td:
            typ_row["TM_ST"] = "202610050600"
            number = 58
            td_rows = [{"YY": "2026", "TD": "58", "TYP": "28", "NOW": "1",
                        "TM_ST": "202610041200", "TM_ED": "210012310000"}]
        with patch.object(vtg_auto, "fetch_atcf_sector_entries", return_value=vtg_auto.parse_atcf_sector_file(SECTOR_TEXT)), \
                patch.object(vtg_auto, "fetch_bdeck_text_for_data_time", return_value=OLD_BDECK), \
                patch.object(vtg_auto, "find_atcf_match") as bdeck_name, \
                redirect_stdout(io.StringIO()):
            jobs = vtg_auto.build_storm_jobs(
                now=vtg_auto.parse_utc_stamp(CYCLE), data_time=CYCLE, td_rows=td_rows,
                typ_rows=[typ_row], manual_map={}, auth_key="",
                atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
                kma_gts_now_text=kma_text(number),
            )
        bdeck_name.assert_not_called()
        self.assertEqual(1, len(jobs))
        return jobs[0]

    def test_typ_and_linked_td_use_recent_name_without_old_bdeck_override(self):
        for linked_td in (False, True):
            with self.subTest(linked_td=linked_td):
                job = self.build_job(linked_td)
                self.assertEqual("ep152026", job.atcf_id)
                self.assertEqual("sector_name_recent", job.atcf_match_method)
                self.assertFalse(job.skip_atcf)
                self.assertTrue(job.require_exact_analysis)
                self.assertIsNone(job.analysis_point)

    def test_exact_analysis_requirement_reaches_renderer_and_kma_values_survive(self):
        command, _ = vtg_auto.vtg_command(
            job=self.build_job(), output_root=Path("data"), auth_key="", fallback_auth_key="",
            python="python", fcst_hours_list=[240], auto_fcst_hours=False, source_overrides=[],
        )
        with patch("sys.argv", command[1:]):
            settings = VTG.parse_args()
        self.assertTrue(settings.require_exact_analysis)
        self.assertEqual("ep152026", settings.atcf_id)
        frame = VTG.read_kma_csv(kma_text(), settings, forecast_only=True)
        with patch.object(VTG, "fetch_bdeck_analysis_point") as bdeck, redirect_stdout(io.StringIO()):
            resolved = VTG.settings_with_bdeck_analysis_if_needed(object(), settings, frame)
            result = VTG.apply_common_kma_start(frame, resolved)
        bdeck.assert_not_called()
        start = result[result["SRC"].eq("KMA")].iloc[0]
        self.assertEqual((24.8, 179.4, 965, 46), (start["LAT"], start["LON"], start["PS"], start["WS"]))

    def test_renderer_rejects_old_analysis_but_accepts_independent_same_cycle_bdeck(self):
        settings = VTG.Settings(data_time=CYCLE, atcf_id="ep152026", require_exact_analysis=True)
        for bdeck_text, expected_lat in ((OLD_BDECK, None), (CURRENT_BDECK, 24.8)):
            with self.subTest(expected_lat=expected_lat), \
                    patch.object(VTG, "fetch_kma_now_analysis_point", return_value=None), \
                    patch.object(VTG, "fetch_text", return_value=bdeck_text), \
                    redirect_stdout(io.StringIO()):
                resolved = VTG.settings_with_bdeck_analysis_if_needed(object(), settings, pd.DataFrame())
            self.assertEqual(expected_lat, resolved.analysis_lat)
            if expected_lat is not None:
                self.assertEqual(CYCLE, resolved.analysis_time)


if __name__ == "__main__":
    unittest.main()
