import contextlib
import io
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from urllib.error import HTTPError

import windborne_probe as wb


def deck_row(cycle="2026102700", model="WMSH", hour=0,
             lat="144N", lon="1622E", wind=42, pressure=994):
    return f"WP, 30, {cycle}, 03, {model}, {hour}, {lat}, {lon}, {wind}, {pressure}, XX,\n"


def metadata(cycle="2026102700"):
    timestamp = wb.parse_cycle(cycle).isoformat()
    return {"tropical_cyclone_id": "WP302026",
            "initialization_time": timestamp, "forecast_zero": timestamp}


class WindborneProbeTests(unittest.TestCase):
    def test_mean_summary_includes_native_zero_hour_pressure(self):
        text = (deck_row(pressure=980) + deck_row(hour=3, wind=44)
                + deck_row(hour=9, pressure=992)
                + deck_row(model="W000", hour=360, pressure=900))
        result = wb.summarize_deck(text, "WP302026", "2026102700")
        self.assertEqual(3, result["mean_points"])
        self.assertEqual(9, result["mean_last_hour"])
        self.assertEqual([3, 6], result["mean_step_hours"])
        self.assertEqual(980, result["mean_min_pressure_hpa"])
        self.assertEqual(44, result["mean_max_wind_kt"])
        self.assertEqual(1, result["member_count"])

    def test_signed_coordinates_and_dateline_are_preserved(self):
        self.assertEqual(-14.4, wb.parse_coord("144S", True))
        self.assertEqual(-178.5, wb.parse_coord("1785W", False))
        result = wb.summarize_deck(
            deck_row(lon="1799E") + deck_row(hour=3, lon="1785W"),
            "WP302026", "2026102700")
        self.assertEqual(2, result["mean_points"])

    def test_invalid_decks_do_not_pass_as_success(self):
        for text in ("", "<html>login</html>", deck_row(cycle="2026102618"),
                     deck_row().replace("WP, 30", "WP, 29"),
                     deck_row(lat="999N"), deck_row(lon="9999W"),
                     deck_row(model="OTHER"), deck_row(wind="nan"),
                     deck_row(pressure="Infinity"), deck_row(hour=-3)):
            with self.subTest(text=text):
                with self.assertRaises(wb.ProbeError):
                    wb.summarize_deck(text, "WP302026", "2026102700")

    def test_duplicate_radii_do_not_inflate_mean_count(self):
        result = wb.summarize_deck(deck_row() * 2, "WP302026", "2026102700")
        self.assertEqual(1, result["mean_points"])
        with self.assertRaises(wb.ProbeError):
            wb.summarize_deck(deck_row() + deck_row(pressure=990), "WP302026", "2026102700")

    def test_missing_intensity_is_not_used_as_minimum(self):
        result = wb.summarize_deck(deck_row(pressure=0, wind=-9), "WP302026", "2026102700")
        self.assertIsNone(result["mean_min_pressure_hpa"])
        self.assertIsNone(result["mean_max_wind_kt"])

    def test_wrong_json_cycle_or_zero_does_not_write_artifact(self):
        cases = [metadata("2026102618"),
                 {**metadata(), "forecast_zero": "2026-10-26T18:00:00Z"},
                 {**metadata(), "tropical_cyclone_id": "WP292026"}]
        with tempfile.TemporaryDirectory() as folder:
            for detail in cases:
                with self.subTest(detail=detail), patch.object(wb, "request_json", return_value=detail):
                    with self.assertRaises(wb.ProbeError):
                        wb.probe_cycle(None, "test-key", "WP302026", "2026102700", Path(folder))
            self.assertFalse(list(Path(folder).iterdir()))

    def test_exact_cycle_saves_validated_deck(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(wb, "request_json", return_value=metadata()), \
                patch.object(wb, "request_text", return_value=deck_row()):
            result = wb.probe_cycle(None, "test-key", "WP302026", "2026102700", Path(folder))
            self.assertEqual("ok", result["status"])
            self.assertEqual(deck_row(), (Path(folder) / result["file"]).read_text())

    def test_member_only_deck_is_reported_as_no_mean(self):
        with tempfile.TemporaryDirectory() as folder, \
                patch.object(wb, "request_json", return_value=metadata()), \
                patch.object(wb, "request_text", return_value=deck_row(model="W000")):
            with self.assertRaisesRegex(wb.ProbeError, "No WMSH"):
                wb.probe_cycle(None, "test-key", "WP302026", "2026102700", Path(folder))

    def test_auth_uses_header_not_query_and_redirect_is_refused(self):
        opener = MagicMock()
        response = opener.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b"{}"
        wb.request_json(opener, "test-key", "/WP302026", {"initialization_time": "2026102700"})
        request = opener.open.call_args.args[0]
        self.assertNotIn("test-key", request.full_url)
        self.assertEqual("Bearer test-key", request.get_header("Authorization"))
        self.assertIsNone(wb.NoRedirects().redirect_request(request, None, 302, "", {}, "https://example.org"))

    def test_http_error_body_and_credential_echo_are_not_exposed(self):
        opener = MagicMock()
        opener.open.side_effect = HTTPError("https://example.org", 403, "test-key", {}, io.BytesIO(b"test-key"))
        with self.assertRaises(wb.ProbeError) as error:
            wb.request_text(opener, "test-key", "/WP302026")
        self.assertEqual("HTTP 403", str(error.exception))
        opener.open.side_effect = None
        response = opener.open.return_value.__enter__.return_value
        response.status = 200
        response.read.return_value = b"test-key"
        with self.assertRaises(wb.ProbeError) as error:
            wb.request_text(opener, "test-key", "/WP302026")
        self.assertNotIn("test-key", str(error.exception))

    def test_missing_one_cycle_does_not_skip_other_cycles(self):
        results = [wb.ProbeError("HTTP 404"), {"status": "ok"}, {"status": "ok"}]
        with tempfile.TemporaryDirectory() as folder, \
                patch.dict(os.environ, {"WB_API_KEY": "test-key", "GITHUB_STEP_SUMMARY": ""}), \
                patch.object(wb, "request_json", side_effect=wb.ProbeError("HTTP 404")), \
                patch.object(wb, "probe_cycle", side_effect=results) as probe, \
                contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(1, wb.main(["--output-dir", folder]))
            self.assertEqual(3, probe.call_count)
            report = json.loads((Path(folder) / "report.json").read_text())
            self.assertEqual(["error", "ok", "ok"], [r["status"] for r in report["results"]])
            self.assertNotIn("test-key", json.dumps(report))

    def test_invalid_inputs_are_rejected_before_network(self):
        with contextlib.redirect_stderr(io.StringIO()):
            for args in (["--storm-id", "../../bad"], ["--cycles", "latest"],
                         ["--cycles", "2026102701"], ["--cycles", "2026023000"]):
                with self.subTest(args=args), self.assertRaises(SystemExit):
                    wb.main(["--output-dir", ".", *args])


if __name__ == "__main__":
    unittest.main()
