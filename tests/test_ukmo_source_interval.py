import io
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from datetime import datetime, timedelta

import pandas as pd

import VTG


def track(source, hours, model="UKM"):
    cycle = datetime(2026, 10, 21)
    return pd.DataFrame([
        {
            "SRC": model, VTG.DATA_SOURCE_COLUMN: source, "TMD": hour,
            "FT_TM(UTC)": (cycle + timedelta(hours=hour)).strftime("%Y%m%d%H%M"),
            "SEQ": 0, "LAT": 16.0 + hour / 100, "LON": 150.0,
            "PS": 990.0, "WS": 20.0,
        }
        for hour in hours
    ])


class UkmoSourceIntervalTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(data_time="202610210000", fcst_hours=240)

    def select(self, *frames, settings=None):
        with redirect_stdout(io.StringIO()) as log:
            selected = VTG.select_model_sources_by_priority(
                pd.concat(frames, ignore_index=True), settings or self.settings,
            )
        return selected, log.getvalue()

    def test_six_hour_source_beats_every_higher_priority_twelve_hour_source(self):
        priorities = VTG.source_priority_for_model("UKM", self.settings)
        for fine_index in range(1, len(priorities)):
            for coarse_source in priorities[:fine_index]:
                with self.subTest(fine=priorities[fine_index], coarse=coarse_source):
                    fine = track(priorities[fine_index], [0, 6, 12, 18, 24])
                    selected, log = self.select(track(coarse_source, [0, 12, 24, 36]), fine)
                    self.assertEqual({priorities[fine_index]}, set(selected[VTG.DATA_SOURCE_COLUMN]))
                    self.assertEqual(fine["TMD"].tolist(), selected["TMD"].tolist())
                    self.assertIn("6h forecast interval, then source priority", log)

    def test_equal_intervals_keep_existing_source_priority(self):
        for hours in ([0, 6, 12, 18], [0, 12, 24, 36]):
            selected, _ = self.select(track("EMC.NCEP", hours), track("APIHUB", hours), track("KNACKWX", hours))
            self.assertEqual({"APIHUB"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_multiple_six_hour_sources_use_priority_and_do_not_splice_tracks(self):
        selected, _ = self.select(
            track("APIHUB", [0, 12, 24, 36, 48]),
            track("EMC.NCEP", [0, 6, 12, 18]),
            track("KNACKWX", [0, 6, 12, 18, 24, 30]),
        )
        self.assertEqual({"EMC.NCEP"}, set(selected[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual([0, 6, 12, 18], selected["TMD"].tolist())

    def test_repeated_unsorted_string_leads_do_not_change_cadence(self):
        fine = track("KNACKWX", [0, 6, 12, 18])
        fine["TMD"] = fine["TMD"].astype(str)
        fine = pd.concat([fine.iloc[::-1], fine.iloc[[1, 2]]], ignore_index=True)
        self.assertEqual(6.0, VTG.forecast_step_hours(fine))
        selected, _ = self.select(track("APIHUB", [0, 12, 24, 36]), fine)
        self.assertEqual({"KNACKWX"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_zero_hour_analysis_does_not_make_twelve_hour_forecast_look_six_hour(self):
        coarse = track("KNACKWX", [0, 6, 18, 30, 42])
        self.assertEqual(12.0, VTG.forecast_step_hours(coarse))
        selected, _ = self.select(track("APIHUB", [0, 12, 24, 36]), coarse)
        self.assertEqual({"APIHUB"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_six_hour_track_with_twelve_hour_tail_is_still_preferred(self):
        fine = track("KNACKWX", [0, 6, 12, 24, 36, 48])
        selected, _ = self.select(track("APIHUB", [0, 12, 24, 36, 48]), fine)
        self.assertEqual({"KNACKWX"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_too_few_forecasts_do_not_claim_six_hour_cadence(self):
        for hours in ([0], [0, 6]):
            self.assertIsNone(VTG.forecast_step_hours(track("KNACKWX", hours)))
            selected, _ = self.select(track("APIHUB", [0, 12, 24, 36]), track("KNACKWX", hours))
            self.assertEqual({"APIHUB"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_qc_rejected_fine_source_does_not_displace_valid_coarse_source(self):
        selected, _ = self.select(
            track("KNACKWX", [18, 24, 30]),
            track("EMC.NCEP", [0, 12, 24, 36]),
        )
        self.assertEqual({"EMC.NCEP"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_cadence_is_checked_after_gap_qc(self):
        selected, _ = self.select(
            track("APIHUB", [0, 12, 24, 36]),
            track("KNACKWX", [0, 12, 36, 42, 48]),
        )
        self.assertEqual({"APIHUB"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_other_models_and_ukmo_eps_keep_existing_rules(self):
        for model in ("GFS", "CMC", "UKMO_EPS"):
            selected, log = self.select(
                track("APIHUB", [0, 12, 24, 36], model),
                track("KNACKWX", [0, 6, 12, 18], model),
            )
            self.assertEqual({"APIHUB"}, set(selected[VTG.DATA_SOURCE_COLUMN]))
            self.assertNotIn("6h forecast interval", log)

    def test_six_hour_rule_precedes_an_explicit_coarse_source_preference(self):
        settings = replace(self.settings, source_overrides=(("UKM", "APIHUB"),))
        selected, _ = self.select(
            track("APIHUB", [0, 12, 24, 36]),
            track("KNACKWX", [0, 6, 12, 18]), settings=settings,
        )
        self.assertEqual({"KNACKWX"}, set(selected[VTG.DATA_SOURCE_COLUMN]))


if __name__ == "__main__":
    unittest.main()
