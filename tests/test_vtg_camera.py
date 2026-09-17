import math
import random
import unittest
from dataclasses import replace

import pandas as pd

import VTG


def track(model="GFS", step=6, start=0, end=120, lat=20, lon=150, dx=-0.15, dy=0.15):
    return pd.DataFrame([
        {"SRC": model, "TMD": hour, "LAT": lat + dy * hour, "LON": lon + dx * hour}
        for hour in range(start, end + 1, step)
    ])


def speed_track(speeds, model="GFS", lat=10, lon=135):
    rows = [{"SRC": model, "TMD": 0, "LAT": lat, "LON": lon}]
    for index, speed in enumerate(speeds, 1):
        lat += speed * 6 / 111.195
        rows.append({"SRC": model, "TMD": index * 6, "LAT": lat, "LON": lon})
    return pd.DataFrame(rows)


class CameraTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(data_time="202609170600", fcst_hours=120)
        self.projection = VTG.ccrs.Mercator()
        self.data_crs = VTG.ccrs.PlateCarree()

    def projected(self, extent):
        x0, y0 = self.projection.transform_point(extent[0], extent[2], self.data_crs)
        x1, y1 = self.projection.transform_point(extent[1], extent[3], self.data_crs)
        return x0, x1, y0, y1

    def anchor_fraction(self, extent, anchor):
        x0, x1, y0, y1 = self.projected(extent)
        x, y = self.projection.transform_point(*anchor, self.data_crs)
        return (x - x0) / (x1 - x0), (y - y0) / (y1 - y0)

    def finalize(self, extent, anchor=None, settings=None, width=16, height=12):
        return VTG.finalize_map_extent(settings or self.settings, extent,
                                       fig_width=width, fig_height=height, start_point=anchor)

    def assert_domain_aspect(self, extent, aspect=4 / 3):
        self.assertTrue(all(math.isfinite(value) for value in extent))
        self.assertGreaterEqual(extent[0], VTG.DISPLAY_120_LON_MIN - 1e-8)
        self.assertLessEqual(extent[1], VTG.DISPLAY_120_LON_MAX + 1e-8)
        self.assertGreaterEqual(extent[2], VTG.DISPLAY_120_LAT_MIN - 1e-8)
        self.assertLessEqual(extent[3], VTG.DISPLAY_120_LAT_MAX + 1e-8)
        x0, x1, y0, y1 = self.projected(extent)
        self.assertGreater(x1, x0)
        self.assertGreater(y1, y0)
        self.assertAlmostEqual((x1 - x0) / (y1 - y0), aspect, places=7)

    def test_dujuan_start_outside_otherwise_valid_legacy_view(self):
        # Frozen 2026-09-17 06UTC reproduction: the old camera placed 0h at -1.13%.
        legacy = [126.12090177385456, 169.7587087305591, 21.94564, 48.34404]
        anchor = (150.1, 21.6)
        self.assertLess(self.anchor_fraction(legacy, anchor)[1], 0)
        extent = self.finalize(legacy, anchor)
        self.assert_domain_aspect(extent)
        self.assertGreaterEqual(self.anchor_fraction(extent, anchor)[1], 0.08 - 1e-8)
        self.assertGreaterEqual(extent[3], legacy[3] - 1e-8)
        self.assertLessEqual(extent[0], legacy[0])
        self.assertGreaterEqual(extent[1], legacy[1])

    def test_start_safety_applies_in_all_directions(self):
        for anchor in [(117, 25), (162, 25), (140, 8), (140, 42)]:
            with self.subTest(anchor=anchor):
                extent = self.finalize([125, 155, 15, 35], anchor)
                self.assert_domain_aspect(extent)
                x, y = self.anchor_fraction(extent, anchor)
                self.assertGreaterEqual(x, 0.08 - 1e-8)
                self.assertLessEqual(x, 0.92 + 1e-8)
                self.assertGreaterEqual(y, 0.08 - 1e-8)
                self.assertLessEqual(y, 0.84 + 1e-8)

    def test_header_does_not_cover_current_marker(self):
        extent = self.finalize([125, 155, 12, 36], (140, 35))
        self.assertLessEqual(self.anchor_fraction(extent, (140, 35))[1], 0.84 + 1e-8)

    def test_safe_legacy_composition_is_unchanged(self):
        initial = [120, 155, 10, 40]
        legacy = VTG.aspect_match_and_clamp_extent(initial, self.settings, fig_width=16, fig_height=12)
        extent = self.finalize(legacy, (140, 25))
        for actual, expected in zip(extent, legacy):
            self.assertAlmostEqual(actual, expected, places=8)

    def test_hard_edges_preserve_point_even_when_full_padding_is_impossible(self):
        for anchor in [(100, 20), (179.9, 20), (140, 0), (140, 50), (100, 50), (179.9, 0)]:
            with self.subTest(anchor=anchor):
                extent = self.finalize([125, 155, 10, 40], anchor)
                self.assert_domain_aspect(extent)
                for fraction in self.anchor_fraction(extent, anchor):
                    self.assertGreaterEqual(fraction, -1e-8)
                    self.assertLessEqual(fraction, 1 + 1e-8)

    def test_invalid_or_outside_anchor_does_not_break_domain(self):
        for anchor in [None, (float("nan"), 20), (140, float("inf")), (190, 20), (140, 60)]:
            with self.subTest(anchor=anchor):
                self.assert_domain_aspect(self.finalize([80, 210, -10, 65], anchor))

    def test_degenerate_or_nonoverlapping_extent_still_has_area(self):
        for initial in [[130, 130, 20, 20], [110, 120, 60, 65], [110, 120, -30, -20]]:
            with self.subTest(initial=initial):
                self.assert_domain_aspect(self.finalize(initial, (140, 20)))

    def test_randomized_hard_domain_and_anchor_invariants(self):
        rng = random.Random(2625)
        for _ in range(100):
            lon, lat = rng.uniform(70, 175), rng.uniform(-15, 55)
            initial = [lon, lon + rng.uniform(5, 95), lat, lat + rng.uniform(5, 50)]
            anchor = (rng.uniform(100, 179.9), rng.uniform(0, 50))
            width, height = rng.choice([(16, 12), (12, 16), (20, 9)])
            extent = self.finalize(initial, anchor, width=width, height=height)
            self.assert_domain_aspect(extent, width / height)
            for fraction in self.anchor_fraction(extent, anchor):
                self.assertGreaterEqual(fraction, -1e-8)
                self.assertLessEqual(fraction, 1 + 1e-8)

    def test_240h_stays_fixed(self):
        for hours in [240, 360]:
            extent = self.finalize([110, 140, 5, 25], (179, 49), replace(self.settings, fcst_hours=hours))
            self.assertEqual(extent, VTG.FIXED_240_MAP_EXTENT)

    def test_manual_view_is_unchanged(self):
        settings = replace(self.settings, auto_extent=False)
        initial = [120, 155, -5, 40]
        expected = VTG.aspect_match_and_clamp_extent(initial, settings, fig_width=16, fig_height=12)
        self.assertEqual(self.finalize(initial, (179, 49), settings), expected)

    def test_sampling_density_does_not_bias_camera(self):
        other = track("ECMWF", dx=0.1, dy=0.2)
        sparse = pd.concat([track(step=6), other], ignore_index=True)
        expected = VTG.auto_120_map_extent(sparse, self.settings)
        for step in [1, 3]:
            dense = pd.concat([track(step=step), other], ignore_index=True)
            actual = VTG.auto_120_map_extent(dense, self.settings)
            for left, right in zip(actual, expected):
                self.assertAlmostEqual(left, right, places=8)

    def test_sampling_never_extrapolates_and_retains_native_endpoints(self):
        data = track(start=3, end=99)
        sampled = VTG.camera_120_points(data, self.settings)
        self.assertAlmostEqual(sampled["LAT"].min(), data["LAT"].min())
        self.assertAlmostEqual(sampled["LAT"].max(), data["LAT"].max())
        self.assertEqual(len(sampled), 18)

    def test_hidden_variants_inactive_models_and_past_track_do_not_move_camera(self):
        visible = pd.concat([track("KIM_3h"), track("GFS")], ignore_index=True)
        hidden = pd.concat([
            track("KIM_6h", lat=48, lon=105, dx=0, dy=0),
            track("UM", lat=48, lon=105, dx=0, dy=0),
            track("KMA", start=-120, end=-6, lat=40, lon=110, dx=0, dy=0),
        ], ignore_index=True)
        self.assertEqual(VTG.auto_120_map_extent(visible, self.settings),
                         VTG.auto_120_map_extent(pd.concat([visible, hidden]), self.settings))

    def test_camera_calculation_does_not_modify_forecast_values(self):
        data = track(step=3)
        original = data.copy(deep=True)
        VTG.auto_120_map_extent(data, self.settings)
        pd.testing.assert_frame_equal(data, original)

    def test_anchor_priority_is_kma_then_analysis_then_model_zero_hour(self):
        models = pd.concat([track("GFS"), track("ECMWF", lat=22, lon=152)], ignore_index=True)
        self.assertEqual(VTG.current_camera_anchor(models, self.settings), (151, 21))
        settings = replace(self.settings, analysis_lat=19, analysis_lon=149)
        self.assertEqual(VTG.current_camera_anchor(models, settings), (149, 19))
        kma = track("KMA", end=0, lat=21.6, lon=150.1)
        self.assertEqual(VTG.current_camera_anchor(pd.concat([models, kma]), settings), (150.1, 21.6))

    def test_only_current_point_and_empty_frames(self):
        data = track("KMA", end=0, lat=21.6, lon=150.1)
        initial = VTG.auto_120_map_extent(data, self.settings)
        extent = self.finalize(initial, (150.1, 21.6))
        self.assert_domain_aspect(extent)
        self.assertIsNone(VTG.auto_120_map_extent(pd.DataFrame(), self.settings))
        self.assertIsNone(VTG.current_camera_anchor(pd.DataFrame(), self.settings))

    def test_nonfinite_points_cannot_poison_camera(self):
        valid = track()
        invalid = track("ECMWF", lat=float("inf"))
        self.assertEqual(VTG.auto_120_map_extent(valid, self.settings),
                         VTG.auto_120_map_extent(pd.concat([valid, invalid]), self.settings))

    def test_native_early_turn_between_six_hour_samples_is_kept(self):
        data = track(step=3, dx=0, dy=0)
        data.loc[data["TMD"].eq(3), "LAT"] = 12
        # The bend is intentionally absent from the cadence-normalized points.
        self.assertEqual(VTG.camera_120_points(data, self.settings)["LAT"].min(), 20)
        extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (150, 20))
        self.assert_domain_aspect(extent)
        x, y = self.anchor_fraction(extent, (150, 12))
        self.assertGreaterEqual(y, 0.08 - 1e-8)
        self.assertLessEqual(y, 0.84 + 1e-8)

    def test_unconfirmed_terminal_jump_is_not_automatically_discarded(self):
        data = pd.concat([track("GFS", dy=0), track("ECMWF", dy=0)], ignore_index=True)
        data.loc[data["TMD"].eq(120), "LAT"] = 40
        extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (150, 20))
        self.assert_domain_aspect(extent)
        self.assertTrue(VTG.camera_120_weights(VTG.camera_120_points(data, self.settings)).eq(1).all())
        for row in data[data["TMD"].eq(120)].itertuples():
            x, y = self.anchor_fraction(extent, (row.LON, row.LAT))
            self.assertGreaterEqual(x, 0.08 - 1e-8)
            self.assertLessEqual(x, 0.92 + 1e-8)
            self.assertGreaterEqual(y, 0.08 - 1e-8)
            self.assertLessEqual(y, 0.84 + 1e-8)

    def test_one_outlying_terminal_does_not_drive_zoom(self):
        names = sorted(VTG.active_model_names(self.settings) - {"UM", "UM_GFDL_6h", "UKM", "KIM_6h", "KIM_GFDL_6h"})[:20]
        data = pd.concat([track(name, dx=-0.05, dy=0.05) for name in names], ignore_index=True)
        reference = VTG.auto_120_map_extent(data, self.settings)
        data.loc[data["SRC"].eq(names[0]) & data["TMD"].eq(120), ["LAT", "LON"]] = [50, 179]
        actual = VTG.auto_120_map_extent(data, self.settings)
        self.assertAlmostEqual(actual[1] - actual[0], reference[1] - reference[0], places=7)

    def test_auto_view_near_dateline_west_edge_and_equator(self):
        for lon, lat, dx, dy in [(175, 20, 0.04, 0.1), (105, 20, -0.04, 0.1), (140, 3, -0.1, 0.1)]:
            with self.subTest(lon=lon, lat=lat):
                data = track(lon=lon, lat=lat, dx=dx, dy=dy)
                extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (lon, lat))
                self.assert_domain_aspect(extent)
                for fraction in self.anchor_fraction(extent, (lon, lat)):
                    self.assertGreaterEqual(fraction, -1e-8)
                    self.assertLessEqual(fraction, 1 + 1e-8)

    def test_input_order_does_not_move_camera(self):
        data = pd.concat([track("GFS"), track("ECMWF", dx=0.05)], ignore_index=True)
        expected = VTG.auto_120_map_extent(data, self.settings)
        self.assertEqual(expected, VTG.auto_120_map_extent(data.sample(frac=1, random_state=25), self.settings))

    def test_few_available_models_keep_distinct_regular_terminal_tracks(self):
        data = pd.concat([track("GFS", dy=0.1), track("ECMWF", dy=0.2)], ignore_index=True)
        extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (150, 20))
        for row in data[data["TMD"].eq(120)].itertuples():
            x, y = self.anchor_fraction(extent, (row.LON, row.LAT))
            self.assertGreaterEqual(x, 0.08 - 1e-8)
            self.assertLessEqual(x, 0.92 + 1e-8)
            self.assertGreaterEqual(y, 0.08 - 1e-8)
            self.assertLessEqual(y, 0.84 + 1e-8)

    def test_only_abrupt_acceleration_activates_tail_zoom_budget(self):
        data = speed_track([10] * 8 + [60] * 12)
        self.assertEqual(VTG.camera_120_acceleration_start(data), 48)
        weights = VTG.camera_120_weights(VTG.camera_120_points(data, self.settings))
        self.assertTrue(weights.le(1).all())
        self.assertTrue(weights.eq(VTG.CAMERA_120_ACCELERATED_TAIL_WEIGHT).any())
        core = data[data["TMD"].le(48)].copy()
        base = self.finalize(VTG.auto_120_map_extent(core, self.settings), (135, 10))
        full = self.finalize(VTG.auto_120_map_extent(data, self.settings), (135, 10))
        self.assertLessEqual(full[1] - full[0], (base[1] - base[0]) * VTG.CAMERA_120_ACCELERATED_TAIL_SCALE + 1e-8)
        self.assertLess(full[3], 45)
        for row in core.itertuples():
            x, y = self.anchor_fraction(full, (row.LON, row.LAT))
            self.assertGreaterEqual(x, 0.08 - 1e-8)
            self.assertLessEqual(x, 0.92 + 1e-8)
            self.assertGreaterEqual(y, 0.08 - 1e-8)
            self.assertLessEqual(y, 0.84 + 1e-8)

    def test_gradual_acceleration_keeps_late_points_without_48h_zoom_cap(self):
        data = speed_track([12 + 2 * index for index in range(20)], lat=5)
        self.assertIsNone(VTG.camera_120_acceleration_start(data))
        self.assertTrue(VTG.camera_120_weights(VTG.camera_120_points(data, self.settings)).eq(1).all())
        core = data[data["TMD"].le(48)]
        base = self.finalize(VTG.auto_120_map_extent(core, self.settings), (135, 5))
        extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (135, 5))
        self.assert_domain_aspect(extent)
        self.assertGreater(extent[1] - extent[0], (base[1] - base[0]) * 1.5)
        last = data.iloc[-1]
        x, y = self.anchor_fraction(extent, (last.LON, last.LAT))
        self.assertGreaterEqual(x, 0.08 - 1e-8)
        self.assertLessEqual(x, 0.92 + 1e-8)
        self.assertLessEqual(y, 0.84 + 1e-8)

    def test_fast_constant_motion_and_smooth_exponential_increase_are_not_steps(self):
        for speeds in [[60] * 20, [10 * 1.12 ** index for index in range(20)]]:
            with self.subTest(speeds=speeds):
                data = speed_track(speeds, lat=5)
                self.assertIsNone(VTG.camera_120_acceleration_start(data))
                self.assertTrue(VTG.camera_120_weights(VTG.camera_120_points(data, self.settings)).eq(1).all())

    def test_high_latitude_alone_does_not_reduce_weights(self):
        data = speed_track([8] * 20, lat=40)
        self.assertGreater(data.LAT.max(), 46)
        self.assertTrue(VTG.camera_120_weights(VTG.camera_120_points(data, self.settings)).eq(1).all())

    def test_step_detection_is_independent_of_latitude(self):
        for lat in [5, 35]:
            self.assertEqual(VTG.camera_120_acceleration_start(speed_track([10] * 8 + [60] * 12, lat=lat)), 48)

    def test_normalized_cadence_does_not_create_or_hide_acceleration(self):
        for speeds, expected in [([30] * 20, None), ([10] * 8 + [60] * 12, 48)]:
            native = speed_track(speeds)
            for step in [3, 6, 12]:
                data = native.set_index("TMD")[["LAT", "LON"]]
                hours = range(0, 121, step)
                data = data.reindex(data.index.union(hours)).interpolate(method="index").loc[hours].reset_index()
                data["SRC"] = "GFS"
                samples = VTG.camera_120_points(data, self.settings)
                self.assertEqual(VTG.camera_120_acceleration_start(samples[samples.SRC.eq("GFS")]), expected)

    def test_short_surge_or_return_to_normal_motion_is_not_a_fast_tail(self):
        cases = [[10] * 8 + [60] + [10] * 11,
                 [10] * 8 + [60] * 3 + [10] * 9,
                 [10] * 18 + [60] * 2]
        for speeds in cases:
            self.assertIsNone(VTG.camera_120_acceleration_start(speed_track(speeds)))

    def test_near_stationary_relative_speed_change_is_not_enough(self):
        self.assertIsNone(VTG.camera_120_acceleration_start(speed_track([1] * 8 + [8] * 12)))

    def test_one_accelerating_model_does_not_crop_a_regular_models_terminal(self):
        normal = speed_track([25] * 20, model="ECMWF")
        data = pd.concat([normal, speed_track([10] * 8 + [60] * 12)], ignore_index=True)
        extent = self.finalize(VTG.auto_120_map_extent(data, self.settings), (135, 10))
        last = normal.iloc[-1]
        x, y = self.anchor_fraction(extent, (last.LON, last.LAT))
        self.assertGreaterEqual(x, 0.08 - 1e-8)
        self.assertLessEqual(x, 0.92 + 1e-8)
        self.assertLessEqual(y, 0.84 + 1e-8)

    def test_dateline_clamp_does_not_enlarge_an_already_fitted_view(self):
        data = track(lat=20, lon=179.5, dx=-0.05, dy=0.03)
        initial = VTG.auto_120_map_extent(data, self.settings)
        extent = self.finalize(initial, (179.5, 20))
        self.assert_domain_aspect(extent)
        self.assertAlmostEqual(extent[1] - extent[0], initial[1] - initial[0], places=7)

    def test_negligible_weight_cannot_bridge_a_large_gap(self):
        points = pd.DataFrame({"LAT": [20, 20, 46], "CAMERA_WEIGHT": [1, 1, 0.0001]})
        self.assertEqual(VTG.weighted_camera_bounds(points, "LAT"), (20, 20))

    def test_duplicate_coordinates_have_order_independent_weighted_bounds(self):
        points = pd.DataFrame({"LAT": [20, 20, 25, 25, 40], "CAMERA_WEIGHT": [1, 0.1, 0.8, 0.4, 0.05]})
        expected = VTG.weighted_camera_bounds(points, "LAT")
        for seed in range(5):
            self.assertEqual(expected, VTG.weighted_camera_bounds(points.sample(frac=1, random_state=seed), "LAT"))


if __name__ == "__main__":
    unittest.main()
