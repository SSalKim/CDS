import contextlib
import io
import os
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import Mock, patch

import pandas as pd
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import VTG
import windborne as wb
from test_windborne_probe import deck_row, metadata
from test_smca_snapshot import smca_text


class WindborneIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(
            atcf_id="wp302026", storm_year="2026", typ_number=31, typ_name="IN-FA",
            data_time="202610270000", fcst_hours=240,
        )

    def test_exact_metadata_and_deck_are_required_and_only_mean_is_returned(self):
        deck = deck_row() + deck_row(hour=3) + deck_row(model="W000", pressure=900)
        with patch.object(wb, "request_json", return_value=metadata()) as request_json, \
                patch.object(wb, "request_text", return_value=deck) as request_text:
            mean = wb.fetch_mean_deck("wp302026", "2026102700", "test-key")
        self.assertNotIn("W000", mean)
        self.assertEqual(2, len(mean.splitlines()))
        self.assertEqual("/WP302026", request_json.call_args.args[2])
        self.assertEqual("2026102700", request_text.call_args.args[3]["initialization_time"])
        self.assertEqual(20, request_json.call_args.kwargs["timeout"])
        self.assertEqual(20, request_text.call_args.kwargs["timeout"])

    def test_no_latest_fallback_for_wrong_initialization_zero_or_identity(self):
        for detail in (metadata("2026102618"),
                       {**metadata(), "forecast_zero": "2026-10-26T18:00:00Z"},
                       {**metadata(), "tropical_cyclone_id": "WP292026"}):
            with self.subTest(detail=detail), \
                    patch.object(wb, "request_json", return_value=detail), \
                    patch.object(wb, "request_text") as request_text:
                with self.assertRaises(wb.WindborneError):
                    wb.fetch_mean_deck("WP302026", "2026102700", "test-key")
                request_text.assert_not_called()

    def test_invalid_or_member_only_deck_is_not_accepted(self):
        for deck in (deck_row(model="W000"), deck_row(cycle="2026102618"),
                     deck_row().replace("WP, 30", "WP, 29"), "<html>login</html>"):
            with self.subTest(deck=deck), patch.object(wb, "request_json", return_value=metadata()), \
                    patch.object(wb, "request_text", return_value=deck):
                with self.assertRaises(wb.WindborneError):
                    wb.fetch_mean_deck("WP302026", "2026102700", "test-key")

    def test_invalid_inputs_never_send_credentials(self):
        with patch.object(wb, "request_json") as request:
            for identity, cycle, key in (("../../bad", "2026102700", "key"),
                                         ("WP302026", "latest", "key"),
                                         ("WP302026", "2026102701", "key"),
                                         ("WP302026", "2026102700", "")):
                with self.assertRaises(wb.WindborneError):
                    wb.fetch_mean_deck(identity, cycle, key)
            request.assert_not_called()

    def test_urls_are_exact_cycle_per_identity_and_missing_key_skips_provider(self):
        settings = replace(self.settings, extra_atcf_ids=("wp962026",))
        with patch.dict(os.environ, {"WB_API_KEY": ""}):
            self.assertFalse(any(source == "WINDBORNE" for source, _, _ in VTG.atcf_urls(settings)))
        with patch.dict(os.environ, {"WB_API_KEY": "test-key"}):
            urls = [url for source, url, _ in VTG.atcf_urls(settings) if source == "WINDBORNE"]
        self.assertEqual([
            wb.BASE_URL + "/WP302026?initialization_time=2026102700&format=deck",
            wb.BASE_URL + "/WP962026?initialization_time=2026102700&format=deck",
        ], urls)
        self.assertTrue(all("test-key" not in url and "latest" not in url for url in urls))

    def fetch_with_mock(self, result):
        specs = [("WINDBORNE", wb.BASE_URL + "/WP302026?initialization_time=2026102700&format=deck", 0),
                 ("EMC.NCEP", "https://example.org/atcf", 0)]
        session = Mock()
        with patch.dict(os.environ, {"WB_API_KEY": "test-key"}), \
                patch.object(VTG, "atcf_urls", return_value=specs), \
                patch.object(VTG, "fetch_windborne_mean_deck", side_effect=result) as fetch, \
                patch.object(VTG, "fetch_text", return_value=deck_row(model="AVNO") + deck_row(model="AVNO", hour=6)), \
                contextlib.redirect_stdout(io.StringIO()):
            frame = VTG.fetch_atcf_data(session, self.settings)
        session.headers.update.assert_not_called()
        fetch.assert_called_once_with("WP302026", "2026102700", "test-key")
        return frame

    def test_atcf_pipeline_maps_mean_only_and_preserves_knots_conversion(self):
        raw = self.fetch_with_mock([deck_row() + deck_row(hour=3) + deck_row(model="W000")])
        self.assertEqual({"WMSH", "AVNO"}, set(raw["MODEL"]))
        frame = VTG.atcf_to_kma_schema(raw, self.settings)
        mean = frame[frame["SRC"].eq("WMSH")]
        self.assertEqual({"WINDBORNE"}, set(mean[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual([0, 3], mean["TMD"].tolist())
        self.assertEqual([994, 994], mean["PS"].tolist())
        self.assertTrue(mean["WS"].eq(round(42 * VTG.MS_PER_KT)).all())

    def test_provider_failure_does_not_drop_other_sources(self):
        for message in ("HTTP 403", "HTTP 404", "Network or TLS request failed"):
            with self.subTest(message=message):
                frame = self.fetch_with_mock(wb.WindborneError(message))
                self.assertEqual({"AVNO"}, set(frame["MODEL"]))

    def test_signed_coordinates_and_dateline_tail_are_handled(self):
        raw = VTG.read_atcf_csv(deck_row(lat="144S", lon="1790W"), source="WINDBORNE")
        self.assertEqual((-14.4, -179.0), (raw.iloc[0]["LATI"], raw.iloc[0]["LONG"]))
        text = (deck_row(lon="1790E") + deck_row(hour=3, lon="1795E")
                + deck_row(hour=6, lon="1799W") + deck_row(hour=9, lon="1795E"))
        frame = VTG.atcf_to_kma_schema(VTG.read_atcf_csv(text, source="WINDBORNE"), self.settings)
        with contextlib.redirect_stdout(io.StringIO()):
            checked = VTG.trim_dateline_reflected_tracks(frame)
        self.assertEqual([0, 3], checked["TMD"].tolist())

    def test_inactive_models_are_not_collected_restored_or_plotted(self):
        self.assertTrue(VTG.INACTIVE_MODEL_IDS.isdisjoint(VTG.active_model_names(self.settings)))
        self.assertEqual(40, VTG.active_model_target_count(self.settings))
        for source in VTG.SOURCE_MODEL_IDS.values():
            self.assertNotIn("CTMN", source)
            self.assertNotIn("AFUM", source)
        raw = VTG.atcf_to_kma_schema(VTG.read_atcf_csv(
            deck_row() + deck_row(hour=3), source="WINDBORNE"), self.settings)
        raw["SRC"] = "COAMPS_EPS"
        raw[VTG.DATA_SOURCE_COLUMN] = "RAL.UCAR"
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertTrue(VTG.normalize_guidance_frame(raw, self.settings).empty)
            self.assertTrue(VTG.source_backup_tracks(raw, self.settings).empty)

    def test_geml_uses_smca_and_exact_cycle_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            settings = replace(self.settings, output_root=Path(folder))
            live = smca_text(cycle="2026-10-27T00:00:00Z", typhoon_id="202631", model_id="GEML")
            later = smca_text(cycle="2026-10-27T06:00:00Z", typhoon_id="202631", model_id="GEML")
            with patch.object(VTG, "fetch_text", return_value=live):
                frame = VTG.fetch_smca_data(object(), settings)
            self.assertEqual({"GEML"}, set(frame["SRC"]))
            self.assertEqual({"SMCA.FUN"}, set(frame[VTG.DATA_SOURCE_COLUMN]))
            self.assertEqual([20, 22, 24], frame["WS"].tolist())
            self.assertTrue(VTG.smca_snapshot_path(settings, "GEML").exists())
            with patch.object(VTG, "fetch_text", return_value=later):
                restored = VTG.fetch_smca_data(object(), settings)
            pd.testing.assert_frame_equal(frame, restored, check_dtype=False)

    def test_new_models_are_in_requested_legend_order(self):
        names = [m["name"] for m in VTG.MODEL_INFO if m["name"] in VTG.active_model_names(self.settings)]
        for before, added, after in (("AIGEFS", "GEML", "AICON"), ("WNV3", "WMSH", "HKO_AREC")):
            self.assertEqual([before, added, after], names[names.index(before):names.index(before) + 3])
        self.assertEqual(("AI", "DETERMINISTIC"), VTG.MODEL_CATEGORIES["GEML"])
        self.assertEqual(("AI", "ENSEMBLE"), VTG.MODEL_CATEGORIES["WMSH"])

    def test_weathermesh_legend_compresses_width_without_reducing_height(self):
        VTG.configure_plot_fonts()
        model = next(model for model in VTG.MODEL_INFO if model["name"] == "WMSH")
        for pressure, dpi in ((974, 100), (1009, 100), (1009, 150), (None, 100)):
            with self.subTest(pressure=pressure, dpi=dpi):
                figure = Figure(figsize=(5.2, 12), dpi=dpi)
                canvas = FigureCanvasAgg(figure)
                ax = figure.add_axes([0, 0, 1, 1])
                VTG.draw_model_legend_table(ax, [{
                    "label": model["label"], "metric": f"{pressure}hPa +000/240h" if pressure else "",
                    "label_width_scale": model["legend_width_scale"],
                    "color": "#FF4D17", "text_color": "black", "linestyle": "--",
                    "marker": "o", "markersize": 3, "markeredgewidth": 0,
                }], side="panel")
                label, value, _ = ax.texts
                renderer = canvas.get_renderer()
                patch, = [p for p in ax.patches if p.get_gid() == "compressed-legend-label"]
                rendered = patch.get_window_extent(renderer)
                native = patch.get_path().get_extents()
                self.assertFalse(label.get_visible())
                self.assertEqual(14.2, label.get_fontsize())
                self.assertAlmostEqual(native.height * dpi / 72, rendered.height)
                self.assertAlmostEqual(native.width * dpi / 72 * .94, rendered.width)
                if pressure:
                    self.assertLessEqual(rendered.x1 + 3, value.get_window_extent(renderer).x0)


if __name__ == "__main__":
    unittest.main()
