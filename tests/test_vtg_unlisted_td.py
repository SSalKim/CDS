import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import timedelta
from pathlib import Path
from unittest.mock import patch

import vtg_auto


CYCLE = "202610111200"
REAL_TD57_ROWS = """
0 2026 57 0 0 202610111200 202610111200 16.3 151.0 - -9 1010 13 -9 -9 -9 - -9 CMC
1 2026 57 0 6 202610111200 202610111800 16.9 150.8 - -9 1009 10 -9 -9 -9 - -9 CMC
0 2026 57 0 0 202610111200 202610111200 16.5 150.6 - -9 1010 9 -9 -9 -9 - -9 GFS
1 2026 57 0 6 202610111200 202610111800 16.8 150.5 - -9 1009 9 -9 -9 -9 - -9 GFS
0 2026 57 0 0 202610111200 202610111200 15.4 151.1 - -9 1010 11 -9 -9 -9 - -9 KIM_3h
1 2026 57 0 3 202610111200 202610111500 16.5 151.1 - -9 1009 10 -9 -9 -9 - -9 KIM_3h
"""


def gts_text(rows=REAL_TD57_ROWS):
    # The live requests use disp=1 (CSV); supplied disp=0 rows have the same columns.
    return "#START7777\n#columns\n" + "\n".join(
        ",".join(line.split()) + "," for line in rows.strip().splitlines()
    ) + "\n#7777END\n"


def td_row(number=56, typ=0, end="210012310000"):
    return {"YY": "2026", "TD": str(number), "TYP": str(typ),
            "TM_ST": "202610031200", "TM_ED": end}


class UnlistedTdTests(unittest.TestCase):
    def setUp(self):
        self.td_rows = [td_row()]
        self.typ_rows = [{"YY": "2026", "SEQ": "29", "NOW": "2",
                          "TM_ST": "202610040000", "TM_ED": "202610110600",
                          "TYP_EN": "KOGUMA", "TYP_NAME": ""}]
        self.enterContext(patch.object(vtg_auto, "fetch_kma_text", side_effect=AssertionError("Unexpected network request")))

    def discover(self, text=None, cycle=CYCLE):
        with redirect_stdout(io.StringIO()):
            return vtg_auto.discover_unlisted_td_rows(
                data_time=cycle, td_rows=self.td_rows, typ_rows=self.typ_rows,
                kma_gts_now_text=gts_text() if text is None else text,
            )

    def build_jobs(self, resolve_atcf=False):
        with redirect_stdout(io.StringIO()):
            return vtg_auto.build_storm_jobs(
                now=vtg_auto.parse_utc_stamp(CYCLE) + timedelta(hours=4),
                data_time=CYCLE, td_rows=self.td_rows, typ_rows=self.typ_rows,
                manual_map={}, auth_key="test-key", resolve_atcf=resolve_atcf,
                atcf_search_positive_radius=10, atcf_search_negative_radius=5,
                atcf_position_max_distance_km=600, atcf_position_min_distance_gap_km=100,
                kma_gts_now_text=gts_text(),
            )

    def test_supplied_model_rows_discover_td57_without_official_td_forecast(self):
        rows = self.discover()
        self.assertEqual(1, len(rows))
        self.assertEqual(("2026", "57", "0", CYCLE), tuple(rows[0][key] for key in ("YY", "TD", "TYP", "TM_ST")))
        self.assertEqual("", rows[0]["TM_ED"])
        self.assertEqual([td_row()], self.td_rows)

    def test_precheck_job_preserves_td_identity_and_does_not_change_stale_td56(self):
        jobs = self.build_jobs()
        self.assertEqual({"td_2026_56", "td_2026_57"}, {job.storm_key for job in jobs})
        new_job = next(job for job in jobs if job.td_number == 57)
        self.assertEqual("TD", new_job.canonical_storm_stage)
        self.assertEqual("NONAME", new_job.typ_name)
        self.assertEqual(57, new_job.data_typ_number)
        self.assertIsNone(new_job.linked_typ_number)
        self.assertEqual([td_row()], self.td_rows)

    def test_generation_can_fall_back_to_apihub_only(self):
        self.td_rows[0]["TM_ED"] = "202610040000"
        with patch.object(vtg_auto, "fetch_atcf_sector_entries", return_value=[]), \
                patch.object(vtg_auto, "find_atcf_position_match", return_value=None):
            jobs = self.build_jobs(resolve_atcf=True)
        self.assertEqual(1, len(jobs))
        self.assertEqual("td_2026_57", jobs[0].storm_key)
        self.assertTrue(jobs[0].skip_atcf)

    def test_official_row_takes_over_without_duplicate_or_resurrection(self):
        for typ, end in [(0, "210012310000"), (0, "202610110600"), (30, "202610110600")]:
            with self.subTest(typ=typ, end=end):
                self.td_rows = [td_row(), td_row(57, typ=typ, end=end)]
                self.assertEqual([], self.discover())

    def test_known_named_typ_and_ambiguous_next_typ_are_not_inferred_as_td(self):
        for number in (29, 30):
            self.td_rows = [td_row(20)]
            self.assertEqual([], self.discover(gts_text(REAL_TD57_ROWS.replace("2026 57", f"2026 {number}"))))
        self.td_rows = [td_row(20, typ=57)]
        self.assertEqual([], self.discover())

    def test_stale_cycle_or_invalid_rows_do_not_trigger_discovery(self):
        invalid_texts = [
            "", "NODATA", "<html>login page</html>",
            gts_text(REAL_TD57_ROWS.replace("202610111200", "202610110600")),
            gts_text(REAL_TD57_ROWS.replace("202610111800", "202610120000").replace("202610111500", "202610120000")),
            gts_text(REAL_TD57_ROWS.replace("2026 57", "2025 57")),
            gts_text(REAL_TD57_ROWS.replace("CMC", "UNKNOWN").replace("GFS", "UNKNOWN").replace("KIM_3h", "UNKNOWN")),
            gts_text("\n".join(line for line in REAL_TD57_ROWS.strip().splitlines() if line.startswith("0 "))),
            gts_text("\n".join(line for line in REAL_TD57_ROWS.strip().splitlines() if line.startswith("1 "))),
        ]
        for text in invalid_texts:
            with self.subTest(text=text[:80]):
                self.assertEqual([], self.discover(text))
        self.assertEqual([], self.discover(cycle="202610111800"))

    def test_missing_historical_td_number_is_not_a_new_system(self):
        self.td_rows = [td_row(58)]
        self.assertEqual([], self.discover())
        self.td_rows = []
        self.assertEqual([], self.discover())


class UnlistedTdPrecheckTests(unittest.TestCase):
    def test_main_plans_both_forecast_ranges_without_persisting_provisional_list_row(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            output_root = root / "data"
            forecast_path = root / "forecast.txt"
            forecast_path.write_text(gts_text(), encoding="utf-8")
            github_output = root / "github-output.txt"
            argv = ["vtg_auto.py", "--check-run-needed", "--now", "2026101112",
                    "--auth-key", "test-key", "--fallback-auth-key", "",
                    "--output-root", str(output_root), "--http-cache-dir", str(root / "http"),
                    "--github-output", str(github_output)]

            def list_text(endpoint, year, auth_key, *, cache_dir):
                if endpoint == vtg_auto.TD_LIST_ENDPOINT:
                    return "2026,56,0,202610031200,202610040000,\n"
                return "2026,29,2,0,202610040000,202610110600,KOGUMA,KOGUMA\n"

            output = io.StringIO()
            with patch("sys.argv", argv), \
                    patch.object(vtg_auto, "PROJECT_ROOT", root), \
                    patch.object(vtg_auto, "HTTP_FETCH_CACHE_DIR", None), \
                    patch.object(vtg_auto, "KMA_FALLBACK_AUTH_KEY", ""), \
                    patch.object(vtg_auto, "fetch_kma_list_text", side_effect=list_text), \
                    patch.object(vtg_auto, "ensure_kma_gts_now_cache", return_value=forecast_path), \
                    patch.object(vtg_auto, "run_vtg_batch") as render, \
                    redirect_stdout(output):
                self.assertEqual(0, vtg_auto.main())
                render.assert_not_called()
            self.assertIn("run_step_needed=true", github_output.read_text())
            self.assertIn("planned_run_count=2", github_output.read_text())
            self.assertIn('"storm_key": "td_2026_57"', output.getvalue())
            self.assertIn('"data_typ_number": 57', output.getvalue())
            cached = vtg_auto.load_json(output_root / "cache" / "kma_apihub" / "td_lst_2026.json", {})
            self.assertEqual(["56"], [row["TD"] for row in cached["rows"]])
            self.assertFalse((output_root / "status.json").exists())
            self.assertFalse((output_root / "manifest.json").exists())

    def test_discovery_refresh_replaces_empty_same_cycle_cache(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = vtg_auto.kma_gts_now_cache_path(root, CYCLE, "2")
            path.parent.mkdir(parents=True)
            path.write_text("NODATA", encoding="utf-8")
            with patch.object(vtg_auto, "fetch_kma_text", return_value=gts_text()) as fetch, \
                    redirect_stdout(io.StringIO()):
                result = vtg_auto.ensure_kma_gts_now_cache(
                    data_time=CYCLE, auth_key="test-key", cache_dir=root, mode="2", refresh=True,
                )
            self.assertEqual(path, result)
            self.assertEqual(gts_text(), path.read_text(encoding="utf-8"))
            self.assertFalse(fetch.call_args.kwargs["use_cache"])

    def test_failed_refresh_does_not_use_stale_forecast_for_discovery(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            path = vtg_auto.kma_gts_now_cache_path(root, CYCLE, "2")
            path.parent.mkdir(parents=True)
            path.write_text(gts_text(), encoding="utf-8")
            with patch.object(vtg_auto, "fetch_kma_text", side_effect=TimeoutError("offline")), \
                    redirect_stdout(io.StringIO()):
                result = vtg_auto.ensure_kma_gts_now_cache(
                    data_time=CYCLE, auth_key="test-key", cache_dir=root, mode="2", refresh=True,
                )
            self.assertIsNone(result)


if __name__ == "__main__":
    unittest.main()
