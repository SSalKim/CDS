import unittest
import math
from unittest.mock import patch

import cartopy.crs as ccrs
import pandas as pd
from matplotlib.colors import to_rgba
from matplotlib.transforms import Bbox

import VTG
from test_vtg_zero_hour_pressure import official_point, track


class EndpointLabelTests(unittest.TestCase):
    def setUp(self):
        self.figure = VTG.plt.figure(figsize=(16, 12), dpi=100)
        self.ax = self.figure.add_axes([0, 0, 1, 1], projection=ccrs.Mercator())
        self.ax.set_extent([100, 179.9, 0, 51.45], crs=ccrs.PlateCarree())
        self.models = {model["name"]: model for model in VTG.MODEL_INFO}

    def tearDown(self):
        VTG.plt.close(self.figure)

    def labels(self):
        return [text for text in self.ax.texts if text.get_text()]

    def draw(self, frames):
        data = pd.concat(frames, ignore_index=True)
        data["FT_TIME"] = VTG.parse_ft_time(data["FT_TM(UTC)"])
        with patch.object(VTG, "draw_model_legend_table"):
            VTG.draw_model_tracks(self.ax, data, VTG.Settings(fcst_hours=240))

    def test_requested_abbreviations(self):
        expected = {
            "ECMWF": "ECMWF", "ECMWF_EPS": "ECME", "KIM_3h": "KIM", "KIM_EPS": "KIME",
            "UKM": "UKMO", "UKMO_EPS": "UKME", "GFS": "GFS", "GFS_EPS": "GFSE",
            "CMC": "CMC", "CMC_EPS": "CMCE", "NAVGEM": "NVGM", "FNMOC_EPS": "NVGME",
            "ICON": "ICON", "ICON_EPS": "ICONE", "JGSM": "JGSM", "TEPS": "JGSME",
            "CTCX": "CTCX", "HAFS": "HAFS", "HWRF": "HWRF", "ECMWF_AIFS": "AIFS",
            "ECMWF_AIFS_EPS": "AIFSE", "IFEC_AI": "IFEC", "IFKM_AI": "IFKM",
            "AGFS": "AGFS", "AIGEFS": "AGFSE", "GEML": "GEML", "AICON": "AICON",
            "FNEC_AI": "FNEC", "FNKM_AI": "FNKM", "PGEC_AI": "PGEC", "PGKM_AI": "PGKM",
            "GCEC_AI": "GCEC", "GCKM_AI": "GCKM", "GENC": "GENC", "WNC": "FNV3",
            "WNV3": "WNV3", "WMSH": "WMSH", "HKO_AREC": "AREC",
            "HKO_FXEC": "FXEC", "HKO_FWEC": "FWEC",
        }
        self.assertEqual(expected, {name: VTG.MODEL_ENDPOINT_LABELS[name] for name in expected})
        for name in ("KIM_6h", "KIM_GFDL_6h"):
            self.assertEqual("KIM", VTG.MODEL_ENDPOINT_LABELS[name])

    def test_last_actual_point_not_last_24_hour_marker(self):
        forecast = track(model="WNC", hours=(0, 24, 30))
        original = forecast.copy(deep=True)
        self.draw([forecast.iloc[::-1]])
        label, = self.labels()
        self.assertEqual("FNV3", label.get_text())
        self.assertAlmostEqual(150.1, label.xy[0])
        self.assertAlmostEqual(16.4, label.xy[1])
        self.assertAlmostEqual(0, label.get_position()[0])
        self.assertGreater(label.get_position()[1], 0)
        self.assertEqual("#F7F7F7", label.get_color())
        self.assertEqual(to_rgba(self.models["WNC"]["color"]), label.get_bbox_patch().get_edgecolor())
        self.assertLess(label.get_zorder(), 101)
        self.assertGreater(label.get_zorder(), 100)
        self.assertEqual(to_rgba("#171717", 0.5), label.get_bbox_patch().get_facecolor())
        self.assertFalse(label.get_path_effects())
        pd.testing.assert_frame_equal(forecast, original)

    def test_official_zero_only_and_disabled_models_have_no_labels(self):
        self.draw([official_point(), track(model="GFS", hours=(0,), pressures=(970,)),
                   track(model="COAMPS_EPS"), track(model="AFUM")])
        self.assertEqual([], self.labels())

    def test_kim_aliases_only_label_the_selected_track(self):
        self.draw([track(model="KIM_3h"), track(model="KIM_6h")])
        self.assertEqual(["KIM"], [label.get_text() for label in self.labels()])

    def test_wholly_off_map_or_invalid_track_has_no_label(self):
        for lon, lat in ((185, 20), (150, 70), (float("nan"), 20)):
            with self.subTest(lon=lon, lat=lat):
                VTG.draw_model_endpoint_labels(self.ax, [
                    (self.models["GFS"], pd.DataFrame([{"LON": lon, "LAT": lat, "TMD": 240}])),
                ])
        self.assertEqual([], self.labels())

    def test_coincident_ends_allow_overlap_instead_of_long_leaders(self):
        point = pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])
        VTG.draw_model_endpoint_labels(self.ax, [(self.models[name], point) for name in ("GFS", "WMSH", "WNC")])
        renderer = self.figure.canvas.get_renderer()
        boxes = [label.get_window_extent(renderer).padded(2) for label in self.labels()]
        self.assertTrue(any(box.overlaps(other) for index, box in enumerate(boxes) for other in boxes[index + 1:]))
        self.assertTrue(any(text.get_gid().startswith("model-endpoint-leader-") for text in self.ax.texts))
        for label in self.labels():
            dx, dy = label.get_position()
            height = label.get_window_extent(renderer).height / (self.figure.dpi / 72)
            base_dy = height / 2 + 3 + 6
            self.assertLessEqual(math.hypot(dx, dy - base_dy), height + 1e-6)
            self.assertLessEqual(abs(math.degrees(math.atan2(dx, dy))), 25 + 1e-6)
            self.assertGreater(dy, 0)

    def test_candidates_stay_close_and_forward_for_all_headings(self):
        for width in (15, 25):
            for degrees in range(0, 360, 45):
                heading = math.radians(degrees)
                direction = (math.cos(heading), math.sin(heading))
                offsets = VTG.endpoint_label_offsets(width, 8, direction, max_shift=10)
                base_dx, base_dy, _ = offsets[0]
                for dx, dy, turn in offsets:
                    with self.subTest(width=width, heading=degrees, turn=turn):
                        delta = math.atan2(dy, dx) - heading
                        delta = math.atan2(math.sin(delta), math.cos(delta))
                        self.assertLessEqual(abs(math.degrees(delta)), 25 + 1e-6)
                        self.assertLessEqual(math.hypot(dx - base_dx, dy - base_dy), 10 + 1e-6)

    def test_tiny_text_overlap_is_preferred_to_distant_clear_placement(self):
        box = Bbox.from_bounds(0, 0, 40, 10)
        occupied = [Bbox.from_bounds(39.8, 0, 40, 10)]
        near = VTG.endpoint_label_placement_score(box, occupied, 0, 10, 0)
        far = VTG.endpoint_label_placement_score(box.translated(0, 10), occupied, 10, 10, 0)
        self.assertGreater(near, 0)
        self.assertLess(near, far)
        substantial_overlap = [Bbox.from_bounds(30, 0, 40, 10)]
        self.assertGreater(VTG.endpoint_label_placement_score(box, substantial_overlap, 0, 10, 0), far)

    def test_backing_only_overlap_does_not_move_labels(self):
        self.ax.apply_aspect()
        transform = ccrs.PlateCarree()._as_mpl_transform(self.ax)
        first = pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])
        VTG.draw_model_endpoint_labels(self.ax, [(self.models["WMSH"], first)])
        expected = self.labels()[0].get_position()
        height = self.labels()[0].get_window_extent(self.figure.canvas.get_renderer()).height
        px, py = transform.transform((150, 25))
        lon, lat = transform.inverted().transform((px, py + height + 1))
        second = pd.DataFrame([{"LON": lon, "LAT": lat, "TMD": 240}])
        for label in list(self.ax.texts):
            label.remove()
        VTG.draw_model_endpoint_labels(self.ax, [(self.models["WMSH"], first), (self.models["WNC"], second)])
        for label in self.labels():
            for wanted, actual in zip(expected, label.get_position()):
                self.assertAlmostEqual(wanted, actual)
        a, b = [label.get_window_extent(self.figure.canvas.get_renderer()) for label in self.labels()]
        self.assertFalse(a.overlaps(b))
        self.assertTrue(a.padded(3).overlaps(b.padded(3)))

    def test_small_text_collision_is_relieved_without_a_long_move(self):
        self.ax.apply_aspect()
        transform = ccrs.PlateCarree()._as_mpl_transform(self.ax)
        point = pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])
        endpoints = [(self.models[name], point) for name in ("WMSH", "WNC")]
        VTG.draw_model_endpoint_labels(self.ax, endpoints)
        renderer = self.figure.canvas.get_renderer()
        boxes = [label.get_window_extent(renderer) for label in self.labels()]
        px, py = transform.transform((150, 25))
        lon, lat = transform.inverted().transform((px + sum(box.width for box in boxes) / 2 - 2, py))
        second = pd.DataFrame([{"LON": lon, "LAT": lat, "TMD": 240}])
        for label in list(self.ax.texts):
            label.remove()
        VTG.draw_model_endpoint_labels(self.ax, [(self.models["WMSH"], point), (self.models["WNC"], second)])
        a, b = [label.get_window_extent(renderer) for label in self.labels()]
        self.assertFalse(a.overlaps(b))

    def test_placement_scoring_is_dpi_independent(self):
        box = Bbox.from_bounds(0, 0, 40, 10)
        other = Bbox.from_bounds(38, 0, 40, 10)
        score = VTG.endpoint_label_placement_score(box, [other], 3, 10, 12.5)
        scaled = VTG.endpoint_label_placement_score(
            Bbox.from_extents(*(box.extents * 2)), [Bbox.from_extents(*(other.extents * 2))], 3, 10, 12.5,
        )
        self.assertAlmostEqual(score, scaled)

    def test_endpoint_label_does_not_add_marker_between_24_hour_points(self):
        forecast = track(model="WMSH", hours=(0, 24, 30))
        original = forecast.copy(deep=True)
        self.draw([forecast])
        marker, = [line for line in self.ax.lines if line.get_linestyle() == "None"]
        label, = self.labels()
        self.assertEqual(forecast.loc[forecast.TMD.isin([0, 24]), "LAT"].tolist(), list(marker.get_ydata()))
        self.assertEqual(tuple(label.xy), (forecast.iloc[-1].LON, forecast.iloc[-1].LAT))
        self.assertNotIn(label.xy[1], marker.get_ydata())
        self.assertEqual(self.models["WMSH"]["color"], marker.get_markerfacecolor())
        self.assertLess(marker.get_zorder(), 100)
        self.assertFalse(any((line.get_gid() or "").startswith("model-endpoint-marker-") for line in self.ax.lines))
        pd.testing.assert_frame_equal(original, forecast)

    def test_endpoint_at_24_hour_step_keeps_only_the_existing_marker(self):
        forecast = track(model="WMSH", hours=(0, 24, 48))
        self.draw([forecast])
        marker, = [line for line in self.ax.lines if line.get_linestyle() == "None"]
        self.assertEqual(forecast.LAT.tolist(), list(marker.get_ydata()))
        self.assertFalse(any((line.get_gid() or "").startswith("model-endpoint-marker-") for line in self.ax.lines))

    def test_leaders_touch_label_border_and_exact_track_anchor(self):
        point = pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])
        VTG.draw_model_endpoint_labels(self.ax, [(self.models[name], point) for name in ("WMSH", "WNC", "GFS")])
        self.figure.canvas.draw()
        labels = {label.get_gid(): label for label in self.labels()}
        leaders = [text for text in self.ax.texts if (text.get_gid() or "").startswith("model-endpoint-leader-")]
        self.assertTrue(leaders)
        for leader in leaders:
            label = labels[leader.get_gid().replace("model-endpoint-leader-", "model-endpoint-")]
            arrow = leader.arrow_patch
            self.assertIs(label.get_bbox_patch(), arrow.patchA)
            self.assertEqual(0, arrow.shrinkA)
            self.assertEqual(0, arrow.shrinkB)
            path = arrow.get_path().transformed(arrow.get_transform())
            start, end = path.vertices[0], path.vertices[-1]
            anchor = ccrs.PlateCarree()._as_mpl_transform(self.ax).transform(label.xy)
            self.assertAlmostEqual(anchor[0], end[0], places=5)
            self.assertAlmostEqual(anchor[1], end[1], places=5)
            border = label.get_bbox_patch().get_path().transformed(label.get_bbox_patch().get_transform())
            self.assertTrue(border.contains_point(start, radius=1))
            self.assertFalse(border.contains_point(start, radius=-1))

    def test_labels_stay_inside_map_and_below_header_at_edges(self):
        self.ax.apply_aspect()
        inverse = ccrs.PlateCarree()._as_mpl_transform(self.ax).inverted()
        for x in (self.ax.bbox.x0 + 6, self.ax.bbox.x1 - 6):
            lon, lat = inverse.transform((x, self.figure.bbox.height * 0.885 - 6))
            VTG.draw_model_endpoint_labels(self.ax, [(self.models["ECMWF"], pd.DataFrame([{"LON": lon, "LAT": lat, "TMD": 240}]))])
        self.assertEqual(2, len(self.labels()))
        for label in self.labels():
            box = label.get_window_extent(self.figure.canvas.get_renderer()).padded(2)
            self.assertGreaterEqual(box.x0, self.ax.bbox.x0 + 3.99)
            self.assertLessEqual(box.x1, self.ax.bbox.x1 - 3.99)
            self.assertLessEqual(box.y1, self.figure.bbox.height * 0.885 - 3.99)

    def test_dense_cluster_keeps_all_labels_bounded_and_deterministic(self):
        names = [name for name in VTG.MODEL_ENDPOINT_LABELS if name in VTG.active_model_names(VTG.Settings())]
        endpoints = [(self.models[name], pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])) for name in names]
        VTG.draw_model_endpoint_labels(self.ax, endpoints)
        first = [(label.get_text(), label.get_position()) for label in self.labels()]
        self.assertEqual(len(names), len(first))
        renderer = self.figure.canvas.get_renderer()
        for label in self.labels():
            dx, dy = label.get_position()
            height = label.get_window_extent(renderer).height / (self.figure.dpi / 72)
            base_dy = height / 2 + 3 + 6
            self.assertLessEqual(math.hypot(dx, dy - base_dy), height + 1e-6)
            self.assertLessEqual(abs(math.degrees(math.atan2(dx, dy))), 25 + 1e-6)
            self.assertGreater(dy, 0)
        for text in list(self.ax.texts):
            text.remove()
        VTG.draw_model_endpoint_labels(self.ax, endpoints)
        self.assertEqual(first, [(label.get_text(), label.get_position()) for label in self.labels()])

    def test_label_and_leader_stacking_follow_model_priority(self):
        point = pd.DataFrame([{"LON": 150, "LAT": 25, "TMD": 240}])
        names = [name for name in VTG.MODEL_ENDPOINT_LABELS if name in self.models]
        VTG.draw_model_endpoint_labels(self.ax, [(self.models[name], point) for name in reversed(names)])
        labels = {label.get_gid().removeprefix("model-endpoint-"): label for label in self.labels()}
        leaders = {text.get_gid().removeprefix("model-endpoint-leader-"): text for text in self.ax.texts
                   if (text.get_gid() or "").startswith("model-endpoint-leader-")}
        self.assertEqual(set(names), set(labels))
        self.assertTrue(leaders)
        for name, label in labels.items():
            self.assertGreater(label.get_zorder(), 100)
            self.assertLess(label.get_zorder(), 101)
            self.assertEqual(to_rgba("#171717", 0.5), label.get_bbox_patch().get_facecolor())
            for other_name, other in labels.items():
                difference = self.models[name]["zorder"] - self.models[other_name]["zorder"]
                expected = (difference > 0) - (difference < 0)
                actual = label.get_zorder() - other.get_zorder()
                self.assertEqual(expected, (actual > 0) - (actual < 0))
        for name, leader in leaders.items():
            self.assertAlmostEqual(99 + self.models[name]["zorder"] / 1000, leader.get_zorder())
            self.assertLess(leader.get_zorder(), min(label.get_zorder() for label in labels.values()))

    def test_off_map_endpoint_labels_the_exit_line_not_the_previous_point(self):
        forecast = track(hours=(0, 6, 12))
        forecast.loc[:, "LON"] = [150.0, 160.0, 179.99]
        forecast.loc[:, "LAT"] = 20.0
        self.draw([forecast])
        label, = self.labels()
        self.assertGreater(label.xy[0], 179.0)
        self.assertLess(label.xy[0], 179.9)
        self.assertAlmostEqual(20.0, label.xy[1])
        self.assertFalse(any((line.get_gid() or "").startswith("model-endpoint-marker-") for line in self.ax.lines))

    def test_dateline_crossing_label_stays_at_eastern_exit(self):
        forecast = track(hours=(0, 6, 12))
        forecast.loc[:, "LON"] = [170.0, 178.0, -178.0]
        forecast.loc[:, "LAT"] = 25.0
        self.draw([forecast])
        label, = self.labels()
        self.assertGreater(label.xy[0], 179.0)

    def test_returning_track_uses_final_visible_endpoint(self):
        forecast = track(hours=(0, 6, 12))
        forecast.loc[:, "LON"] = [175.0, 179.99, 170.0]
        self.draw([forecast])
        label, = self.labels()
        self.assertAlmostEqual(170.0, label.xy[0])
        self.assertLess(label.get_position()[0], 0)

    def test_labels_follow_all_eight_final_headings(self):
        for east, north in ((-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1), (-1, 0)):
            with self.subTest(east=east, north=north):
                for label in list(self.ax.texts):
                    label.remove()
                forecast = track(hours=(0, 6, 12))
                # The initial heading differs; only the final segment should determine placement.
                forecast.loc[:, "LON"] = [148, 150, 150 + east]
                forecast.loc[:, "LAT"] = [23, 25, 25 + north]
                self.draw([forecast])
                label, = self.labels()
                dx, dy = label.get_position()
                for actual, sign in ((dx, east), (dy, north)):
                    if sign:
                        self.assertGreater(actual * sign, 0)
                    else:
                        self.assertAlmostEqual(actual, 0, places=5)
                transform = ccrs.PlateCarree()._as_mpl_transform(self.ax)
                start = transform.transform((150, 25))
                end = transform.transform((150 + east, 25 + north))
                self.assertAlmostEqual(math.atan2(dy, dx), math.atan2(end[1] - start[1], end[0] - start[0]), places=3)

    def test_stationary_tail_uses_last_nonzero_motion(self):
        forecast = track(hours=(0, 6, 12))
        forecast.loc[:, "LON"] = [150, 149, 149]
        forecast.loc[:, "LAT"] = [25, 26, 26]
        self.draw([forecast])
        label, = self.labels()
        self.assertLess(label.get_position()[0], 0)
        self.assertGreater(label.get_position()[1], 0)

    def test_only_backing_is_translucent_for_all_model_colors_and_map_backgrounds(self):
        for background in ("#262626", "#656565", "#ED2939"):
            self.ax.set_facecolor(background)
            for name in ("IFEC_AI", "UKM", "FNEC_AI", "WMSH"):
                for label in list(self.ax.texts):
                    label.remove()
                self.draw([track(model=name)])
                label, = self.labels()
                self.assertIsNone(label.get_alpha())
                self.assertIsNone(label.get_bbox_patch().get_alpha())
                self.assertEqual("#F7F7F7", label.get_color())
                self.assertEqual(to_rgba("#171717", 0.5), label.get_bbox_patch().get_facecolor())
                self.assertEqual(to_rgba(self.models[name]["color"]), label.get_bbox_patch().get_edgecolor())


if __name__ == "__main__":
    unittest.main()
