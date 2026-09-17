import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import VTG
from polarwx_browser import matches_cycle_response, request_identity


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
            with patch("VTG.capture_polarwx_cycle", return_value=payload()) as capture, \
                    patch("VTG.fetch_text", side_effect=AssertionError("Direct request is forbidden")):
                cold = VTG.fetch_polarwx_data(None, settings)
                warm = VTG.fetch_polarwx_data(None, replace(settings, fcst_hours=120))
            capture.assert_called_once_with("wp242026", "202609170000")
            self.assertEqual([996.0, 993.0], cold["PS"].tolist())
            self.assertTrue(cold.equals(warm))

    def test_failure_does_not_abort_other_sources_or_create_cache(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("VTG.capture_polarwx_cycle", side_effect=RuntimeError("HTTP 403")):
                frame = VTG.fetch_polarwx_data(None, self.settings(directory))
            self.assertTrue(frame.empty)
            self.assertEqual([], list(Path(directory).rglob("*.txt")))

    def test_invalid_cached_page_is_not_reused(self):
        with tempfile.TemporaryDirectory() as directory:
            settings = self.settings(directory)
            path = VTG.http_cache_path(settings.http_cache_dir, VTG.polarwx_url(settings.atcf_id, settings.data_time))
            VTG.write_cached_text(path, "<html>Forbidden</html>")
            with patch("VTG.capture_polarwx_cycle", return_value=payload()) as capture:
                frame = VTG.fetch_polarwx_data(None, settings)
            self.assertEqual(2, len(frame))
            capture.assert_called_once()

    def test_wrong_valid_time_is_rejected(self):
        frame = VTG.read_polarwx_json(payload("2026091618"), self.settings())
        self.assertEqual([6.0], frame["TMD"].tolist())


if __name__ == "__main__":
    unittest.main()
