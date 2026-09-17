import json
import tempfile
import unittest
from dataclasses import replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

import VTG
import pandas as pd
from polarwx_browser import matches_cycle_response, request_identity
from polarwx_cache import load_snapshot, queue_request, save_snapshot, snapshot_path, write_json
from polarwx_prefetch import collect_requests


def payload(cycle="2026091700"):
    return json.dumps({"icon": {
        "fhr": [0, 6], "time": [cycle, "2026091706"],
        "lat": [18.88, 21.62], "lon": [150.25, 149.88],
        "mslp": [996, 993], "vmax": [37, 36],
    }})


class PolarwxBrowserTests(unittest.TestCase):
    def settings(self, directory=None):
        return VTG.Settings(atcf_id="wp242026", data_time="202609170000", fcst_hours=240,
                            http_cache_dir=Path(directory) if directory else None)

    def test_response_identity_is_exact(self):
        expected = "https://polarwx.com/data/tropical/storms/wp242026/ensembles/2026091700.json"
        for url in (expected, expected + "?v=123"):
            self.assertTrue(matches_cycle_response(url, "wp242026", "2026091700"))
        for url in (expected.replace("wp24", "wp23"), expected.replace("1700", "1706"),
                    expected.replace(".com/", ".com.evil/"), expected.replace("https:", "http:")):
            self.assertFalse(matches_cycle_response(url, "wp242026", "2026091700"))

    def test_request_validation(self):
        self.assertEqual(("wp242026", "2026091700"), request_identity("WP242026", "202609170000"))
        for storm, cycle in (("../wp242026", "2026091700"), ("wp242026", "2026091701"),
                              ("wp242026", "202609170030"), ("wp242026", "2026131700")):
            with self.assertRaises(ValueError):
                request_identity(storm, cycle)

    def test_browser_response_is_cached_and_never_directly_requested(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(directory)
            root = Path(directory)
            save_snapshot(root, settings.atcf_id, settings.data_time, payload())
            with patch("polarwx_browser.capture_cycle", side_effect=AssertionError("Browser forbidden in renderer")), \
                    patch("VTG.fetch_text", side_effect=AssertionError("Direct request is forbidden")), \
                    patch("VTG.queue_request"):
                cold = VTG.fetch_polarwx_data(None, settings, cache_root=root)
                warm = VTG.fetch_polarwx_data(None, replace(settings, fcst_hours=120), cache_root=root)
            self.assertEqual([996.0, 993.0], cold["PS"].tolist())
            self.assertTrue(cold.equals(warm))

    def test_failure_does_not_abort_other_sources_or_create_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("VTG.queue_request") as queue:
                frame = VTG.fetch_polarwx_data(None, self.settings(directory), cache_root=Path(directory))
            queue.assert_called_once()
            self.assertTrue(frame.empty)
            self.assertEqual([], list(Path(directory).rglob("*.json")))

    def test_invalid_cached_page_is_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(directory)
            path = snapshot_path(Path(directory), settings.atcf_id, settings.data_time)
            VTG.write_cached_text(path, "<html>Forbidden</html>")
            with patch("VTG.queue_request"):
                frame = VTG.fetch_polarwx_data(None, settings, cache_root=Path(directory))
            self.assertTrue(frame.empty)

    def test_wrong_valid_time_is_rejected(self):
        frame = VTG.read_polarwx_json(payload("2026091618"), self.settings())
        self.assertEqual([6.0], frame["TMD"].tolist())

    def complete_other_sources(self):
        frame = VTG.read_polarwx_json(payload(), self.settings())
        frames = []
        for model in set(VTG.polarwx_keys().values()):
            track = frame.copy()
            track["SRC"] = model
            track[VTG.DATA_SOURCE_COLUMN] = "KNACKWX"
            frames.append(track)
        return pd.concat(frames, ignore_index=True)

    def test_complete_other_sources_never_open_polarwx(self):
        with patch("VTG.fetch_polarwx_data") as fetch:
            frame = VTG.fetch_needed_polarwx_data(None, self.settings(), self.complete_other_sources())
        fetch.assert_not_called()
        self.assertTrue(frame.empty)

    def test_missing_model_reads_polarwx_snapshot(self):
        available = self.complete_other_sources()
        available = available[available["SRC"].ne("ICON")]
        self.assertEqual({"ICON"}, VTG.missing_polarwx_models(available, self.settings()))
        with patch("VTG.fetch_polarwx_data", return_value=VTG.empty_polarwx_frame()) as fetch:
            VTG.fetch_needed_polarwx_data(None, self.settings(), available)
        fetch.assert_called_once()

    def test_analysis_only_is_not_a_usable_forecast(self):
        available = self.complete_other_sources()
        available = available[~(available["SRC"].eq("ECMWF") & available["TMD"].gt(0))]
        self.assertEqual({"ECMWF"}, VTG.missing_polarwx_models(available, self.settings()))

    def test_ukmo_eps_pressure_and_explicit_source_are_preserved(self):
        available = self.complete_other_sources()
        available.loc[available["SRC"].eq("UKMO_EPS"), "PS"] = float("nan")
        self.assertEqual({"UKMO_EPS"}, VTG.missing_polarwx_models(available, self.settings()))
        settings = replace(self.settings(), source_overrides=(("ECMWF", "POLARWX"),))
        self.assertEqual({"ECMWF", "UKMO_EPS"}, VTG.missing_polarwx_models(available, settings))

    def test_inactive_models_do_not_trigger_browser(self):
        available = self.complete_other_sources()
        available = available[~available["SRC"].isin(["ICON", "ICON_EPS"])]
        settings = replace(self.settings(), data_time="202607170000")
        self.assertEqual(set(), VTG.missing_polarwx_models(available, settings))

    def test_snapshot_identity_mismatch_is_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = save_snapshot(root, "wp242026", "2026091700", payload())
            snapshot = json.loads(path.read_text())
            snapshot["cycle"] = "2026091618"
            write_json(path, snapshot)
            self.assertIsNone(load_snapshot(root, "wp242026", "2026091700"))

    def test_request_queue_is_deduplicated_and_refresh_throttled(self):
        now = datetime(2026, 9, 17, 3, tzinfo=timezone.utc)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "cache"
            requests = Path(directory) / "requests"
            with patch.dict("os.environ", {"VTG_POLARWX_REQUEST_DIR": str(requests)}):
                self.assertTrue(queue_request(root, "wp242026", "2026091700", now=now))
                self.assertTrue(queue_request(root, "wp242026", "2026091700", now=now))
                self.assertEqual(1, len(list(requests.glob("*.json"))))
                save_snapshot(root, "wp242026", "2026091700", payload(), now=now)
                self.assertFalse(queue_request(root, "wp242026", "2026091700", now=now + timedelta(minutes=5)))
                self.assertTrue(queue_request(root, "wp242026", "2026091700", now=now + timedelta(minutes=16)))
                self.assertFalse(queue_request(root, "wp242026", "2026091400", now=now))

    def test_failed_prefetch_preserves_previous_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = save_snapshot(root, "wp242026", "2026091700", payload(),
                                 now=datetime(2020, 1, 1, tzinfo=timezone.utc))
            before = path.read_bytes()
            with patch("polarwx_prefetch.capture_cycle", side_effect=RuntimeError("HTTP 403")) as capture:
                result = collect_requests([("wp242026", "2026091700")], root)
            capture.assert_called_once()
            self.assertEqual(1, len(result["failed"]))
            self.assertEqual(before, path.read_bytes())

    def test_collector_saves_compact_raw_models_and_skips_fresh_snapshot(self):
        raw = json.loads(payload())
        raw["icon"]["interp"] = {"lat": [99]}
        raw["unused_member"] = {"lat": [88]}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with patch("polarwx_prefetch.capture_cycle", return_value=json.dumps(raw)) as capture:
                result = collect_requests([("wp242026", "2026091700")], root)
                second = collect_requests([("wp242026", "2026091700")], root)
            capture.assert_called_once()
            self.assertEqual(1, len(result["collected"]))
            self.assertEqual(1, len(second["skipped"]))
            snapshot = load_snapshot(root, "wp242026", "2026091700")
            self.assertEqual({"icon"}, set(snapshot["models"]))
            self.assertNotIn("interp", snapshot["models"]["icon"])

    def test_partial_response_retains_missing_empty_or_wrong_cycle_model(self):
        old_time = datetime(2020, 1, 1, tzinfo=timezone.utc)
        for incoming in (None, {"fhr": [], "lat": [], "lon": []},
                         {**json.loads(payload())["icon"], "time": ["2026091618", "2026091700"]}):
            with self.subTest(incoming=incoming), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                old = json.loads(payload())["icon"]
                save_snapshot(root, "wp242026", "2026091700", payload(), now=old_time)
                raw = {"gfs": old}
                if incoming is not None:
                    raw["icon"] = incoming
                with patch("polarwx_prefetch.capture_cycle", return_value=json.dumps(raw)):
                    result = collect_requests([("wp242026", "2026091700")], root)
                self.assertEqual([], result["failed"])
                saved = load_snapshot(root, "wp242026", "2026091700")
                self.assertEqual(old, saved["models"]["icon"])
                self.assertEqual(["icon"], saved["retained_models"])
                self.assertEqual(old_time.isoformat(), saved["model_fetched_at"]["icon"])
                self.assertIn("gfs", saved["models"])

    def test_valid_model_refresh_replaces_old_track_without_cross_cycle_merge(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            save_snapshot(root, "wp242026", "2026091700", payload(),
                          now=datetime(2020, 1, 1, tzinfo=timezone.utc))
            new = json.loads(payload())
            new["icon"]["mslp"] = [990, 987]
            with patch("polarwx_prefetch.capture_cycle", return_value=json.dumps(new)):
                collect_requests([("wp242026", "2026091700")], root)
            saved = load_snapshot(root, "wp242026", "2026091700")
            self.assertEqual([990, 987], saved["models"]["icon"]["mslp"])
            self.assertEqual([], saved["retained_models"])
            save_snapshot(root, "wp242026", "2026091706", json.dumps({"gfs": new["icon"]}))
            self.assertNotIn("icon", load_snapshot(root, "wp242026", "2026091706")["models"])

    def previous_render(self, root):
        settings = replace(self.settings(), output_root=Path(root), overwrite_output=True)
        target = VTG.output_path(settings)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(b"previous image")
        metadata = {"data_time": settings.data_time, "atcf_id": settings.atcf_id,
                    "fcst_hours": 240, "image_path": str(target), "models": ["ICON"]}
        write_json(VTG.metadata_path_for_settings(settings), metadata)
        write_json(VTG.source_availability_latest_path(settings), {
            "data_time": settings.data_time, "atcf_id": settings.atcf_id,
            "model_sources": [{"source": "POLARWX", "model_id": "ICON", "selected": True}],
        })
        return settings

    def test_missing_snapshot_holds_previous_render(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.previous_render(directory)
            empty = VTG.empty_polarwx_frame()
            self.assertEqual({240: ["ICON"]}, VTG.pending_polarwx_render_loss(empty, empty, settings, (240,)))
            self.assertEqual(b"previous image", VTG.output_path(settings).read_bytes())
            self.assertEqual({}, VTG.pending_polarwx_render_loss(empty, empty, replace(settings, skip_atcf=True), (240,)))
            VTG.output_path(settings).unlink()
            self.assertEqual({}, VTG.pending_polarwx_render_loss(empty, empty, settings, (240,)))

    def test_existing_snapshot_or_other_source_does_not_hold_render(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.previous_render(directory)
            empty = VTG.empty_polarwx_frame()
            frame = VTG.read_polarwx_json(payload(), settings)
            # A present Raw track rejected by later QC must not resurrect an old image.
            self.assertEqual({}, VTG.pending_polarwx_render_loss(empty, frame, settings, (240,)))
            self.assertEqual({}, VTG.pending_polarwx_render_loss(frame, empty, settings, (240,)))
            other_cycle = replace(settings, data_time="202609170600")
            self.assertEqual({}, VTG.pending_polarwx_render_loss(empty, empty, other_cycle, (240,)))


if __name__ == "__main__":
    unittest.main()
