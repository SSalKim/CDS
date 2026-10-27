import io
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

import pandas as pd

import VTG


CYCLE = "202610210000"


def track(source="APIHUB", model="GFS", hours=(0, 6, 12), pressures=(970, 980, 990)):
    cycle = datetime(2026, 10, 21)
    return pd.DataFrame([
        {
            "FT": int(hour > 0), "YY": 2026, "TYP": 30, "SEQ": 0,
            "TMD": hour, "TYP_TM(UTC)": CYCLE,
            "FT_TM(UTC)": (cycle + timedelta(hours=hour)).strftime("%Y%m%d%H%M"),
            "LAT": 16.1 + hour / 100, "LON": 150.1, "PS": pressure,
            "WS": 25, "SRC": model, VTG.DATA_SOURCE_COLUMN: source,
        }
        for hour, pressure in zip(hours, pressures, strict=True)
    ])


def official_point():
    frame = track(model="KMA", hours=(0,), pressures=(900,))
    frame.loc[:, "LAT"] = 16.0
    frame.loc[:, "LON"] = 150.0
    return frame


class ZeroHourPressureTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(
            typ_number=30, typ_name="CHAMPI", storm_year="2026",
            data_time=CYCLE, fcst_hours=240,
        )

    def normalize(self, *frames):
        with redirect_stdout(io.StringIO()):
            return VTG.normalize_guidance_frame(
                pd.concat([official_point(), *frames], ignore_index=True), self.settings,
            )

    def test_every_source_keeps_native_zero_hour_pressure_but_uses_official_position(self):
        for source in VTG.source_priority_for_model("GFS", self.settings):
            column = VTG.SOURCE_IDENTIFIER_COLUMNS[source]
            model = next(row["name"] for row in VTG.MODEL_SOURCES if row.get(column))
            with self.subTest(source=source, model=model):
                original = track(source, model)
                expected = original.copy(deep=True)
                normalized = self.normalize(original)
                model_track = normalized[normalized["SRC"].eq(model)]
                zero = model_track[model_track["TMD"].eq(0)].iloc[0]
                self.assertEqual((16.0, 150.0, 970), (zero["LAT"], zero["LON"], zero["PS"]))
                self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(model_track, model))
                pd.testing.assert_frame_equal(original, expected)

    def test_future_pressure_wins_if_lower_and_maximum_lead_is_unchanged(self):
        frame = track(pressures=(990, 970, 980))
        self.assertEqual(" 970hPa +006/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_equal_pressure_uses_earliest_lead_even_when_track_is_unsorted(self):
        frame = track(pressures=(970, 970, 980)).iloc[::-1]
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_missing_invalid_zero_hour_pressure_does_not_hide_valid_forecasts(self):
        for pressure in (None, float("nan"), -9, 0, "missing"):
            with self.subTest(pressure=pressure):
                frame = track(pressures=(pressure, 980, 990))
                self.assertEqual(" 980hPa +006/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_valid_zero_hour_pressure_is_usable_when_future_pressure_is_missing(self):
        frame = track(pressures=(970, None, -9))
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_missing_all_pressures_retains_placeholder(self):
        frame = track(pressures=(-9, None, 0))
        self.assertEqual("----hPa +----/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_synthetic_anchor_does_not_relabel_future_pressure_as_zero_hour(self):
        for source in VTG.source_priority_for_model("GFS", self.settings):
            with self.subTest(source=source):
                normalized = self.normalize(track(source, hours=(6, 12), pressures=(970, 980)))
                model_track = normalized[normalized["SRC"].eq("GFS")]
                zero = model_track[model_track["TMD"].eq(0)]
                if source == "KNACKWX":
                    self.assertTrue(zero.empty)
                else:
                    self.assertEqual(1, len(zero))
                    self.assertTrue(pd.isna(zero.iloc[0]["PS"]))
                    self.assertEqual((16.0, 150.0), (zero.iloc[0]["LAT"], zero.iloc[0]["LON"]))
                self.assertEqual(" 970hPa +006/012h", VTG.track_intensity_summary(model_track, "GFS"))

    def test_zero_hour_only_does_not_activate_a_model(self):
        frame = track(hours=(0,), pressures=(970,))
        self.assertFalse(VTG.has_forecast_points(frame))
        self.assertEqual("", VTG.track_intensity_summary(frame, "GFS"))

    def test_only_selected_source_pressure_is_included(self):
        selected = self.normalize(track(), track("EMC.NCEP", pressures=(850, 860, 870)))
        model_track = selected[selected["SRC"].eq("GFS")]
        self.assertEqual({"APIHUB"}, set(model_track[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(model_track, "GFS"))

    def test_negative_leads_are_excluded_and_numeric_strings_are_accepted(self):
        frame = track(hours=(-6, 0, 6, 12), pressures=(850, "970", "980", "990"))
        frame["TMD"] = frame["TMD"].astype(str)
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(frame, "GFS"))

    def test_pressure_after_forecast_limit_or_motion_qc_is_not_included(self):
        limited = VTG.limit_forecast_hours(
            track(hours=(0, 6, 12, 246), pressures=(970, 980, 990, 850)), self.settings,
        )
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(limited, "GFS"))
        bad_motion = track(hours=(0, 6, 12, 18), pressures=(970, 980, 990, 850))
        bad_motion.loc[bad_motion["TMD"].eq(18), "LAT"] = 40
        model_track = self.normalize(bad_motion).query("SRC == 'GFS'")
        self.assertEqual([0, 6, 12], sorted(model_track["TMD"].tolist()))
        self.assertEqual(" 970hPa +000/012h", VTG.track_intensity_summary(model_track, "GFS"))

    def test_legend_displays_zero_hour_minimum_with_unchanged_track_coordinates(self):
        normalized = self.normalize(track())
        normalized["FT_TIME"] = VTG.parse_ft_time(normalized["FT_TM(UTC)"])
        ax = Mock()
        with patch.object(VTG, "draw_model_legend_table") as legend, \
                patch.object(VTG, "draw_model_endpoint_labels"):
            VTG.draw_model_tracks(ax, normalized, self.settings)
        gfs = next(row for row in legend.call_args.args[1] if row["label"] == "GFS")
        self.assertEqual(" 970hPa +000/012h", gfs["metric"])
        plotted_lons, plotted_lats = ax.plot.call_args_list[0].args[:2]
        self.assertEqual((150.0, 16.0), (plotted_lons.iloc[0], plotted_lats.iloc[0]))


if __name__ == "__main__":
    unittest.main()
