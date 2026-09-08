import argparse
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import patch

import vtg_archive_state
import vtg_auto


class PrecheckChangedPathsTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.output_root = self.root / "data"
        self.cache_dir = self.output_root / "cache" / "kma_apihub"
        self.changed_file = self.root / "changed.txt"
        self.github_output = self.root / "github-output.txt"
        self.now = datetime(2026, 9, 8, 6, 49, tzinfo=timezone.utc)
        self.td_end = "202609080000"
        self.empty_lists = False
        for module in (vtg_auto, vtg_archive_state):
            self.enterContext(patch.object(module, "PROJECT_ROOT", self.root))
        self.enterContext(patch.object(vtg_auto, "utc_now", return_value=self.now))
        self.enterContext(patch.object(vtg_auto, "KMA_FALLBACK_AUTH_KEY", ""))
        self.enterContext(patch.object(vtg_auto, "HTTP_FETCH_CACHE_DIR", None))

    def list_text(self, endpoint, year, auth_key, *, cache_dir):
        if self.empty_lists:
            return "# no systems\n"
        if endpoint == vtg_auto.TD_LIST_ENDPOINT:
            return f"2026,51,24,202609070000,{self.td_end},weakened KROVANH\n"
        return "2026,24,2,0,202608280000,202609070000,KROVANH,KROVANH\n"

    def run_precheck(self):
        argv = [
            "vtg_auto.py", "--check-run-needed", "--auth-key", "test-key",
            "--fallback-auth-key", "", "--output-root", str(self.output_root),
            "--http-cache-dir", str(self.root / "http"),
            "--changed-paths-file", str(self.changed_file),
            "--github-output", str(self.github_output),
        ]
        with (
            patch("sys.argv", argv),
            patch.object(vtg_auto, "fetch_kma_list_text", side_effect=self.list_text),
            patch.object(vtg_auto, "ensure_kma_gts_now_cache") as forecast_fetch,
            redirect_stdout(io.StringIO()),
        ):
            self.assertEqual(vtg_auto.main(), 0)
            forecast_fetch.assert_not_called()
        self.assertFalse((self.output_root / "status.json").exists())
        self.assertFalse((self.output_root / "manifest.json").exists())

    def cache_paths(self):
        return {
            f"data/cache/kma_apihub/{endpoint}_2026.json"
            for endpoint in ("td_lst", "typ_lst")
        }

    def reported_paths(self):
        return set(self.changed_file.read_text(encoding="utf-8").splitlines())

    def test_ended_td_cache_is_reported_when_no_render_is_needed(self):
        self.td_end = "210012310000"
        with patch.object(vtg_auto, "fetch_kma_list_text", side_effect=self.list_text):
            vtg_auto.fetch_td_rows(2026, "test-key", cache_dir=self.cache_dir)
            vtg_auto.fetch_typ_rows(2026, "test-key", cache_dir=self.cache_dir)
        self.td_end = "202609080000"
        self.run_precheck()

        self.assertIn("run_step_needed=false", self.github_output.read_text())
        self.assertEqual(self.reported_paths(), self.cache_paths())
        td_cache = vtg_auto.load_json(self.cache_dir / "td_lst_2026.json", {})
        self.assertEqual(td_cache["rows"][0]["TM_ED"], self.td_end)

        system = self.output_root / "2026" / "TYP_2624_KROVANH"
        (system / "images").mkdir(parents=True)
        (system / "images" / "last.png").write_bytes(b"test image")
        targets_file = self.root / "targets.txt"
        with redirect_stdout(io.StringIO()):
            self.assertEqual(vtg_archive_state.command_scan(argparse.Namespace(
                now="202609080649", kma_cache_dir=self.cache_dir,
                output_root=self.output_root, stale_dispatch_hours=6,
                changed_paths_file=self.changed_file, targets_file=targets_file,
            )), 0)
        self.assertEqual(self.reported_paths(), self.cache_paths() | {
            "data/2026/TYP_2624_KROVANH/metadata/archive_status.json",
        })
        self.assertEqual(targets_file.read_text().strip(), "typ_2026_24")

    def test_active_td_still_requests_render_and_reports_cache(self):
        self.td_end = "210012310000"
        self.run_precheck()
        self.assertIn("run_step_needed=true", self.github_output.read_text())
        self.assertIn("planned_run_count=2", self.github_output.read_text())
        self.assertEqual(self.reported_paths(), self.cache_paths())

    def test_empty_lists_report_new_cache_files_and_replace_old_path_list(self):
        self.empty_lists = True
        self.changed_file.write_text("data/old-run.json\n", encoding="utf-8")
        self.run_precheck()
        self.assertIn("run_step_needed=false", self.github_output.read_text())
        self.assertEqual(self.reported_paths(), self.cache_paths())


if __name__ == "__main__":
    unittest.main()
