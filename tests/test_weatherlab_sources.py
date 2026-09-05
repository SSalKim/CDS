import unittest
from unittest.mock import patch

import pandas as pd

import VTG


def atcf(aid="WNV3", cycle="2026090412", basin="WP", number=22):
    return (
        "# Variable-length source header\n# Terms\n# BEGIN DATA\n"
        f"{basin}, {number:02d}, {cycle}, 03, {aid}, 0, 250N, 1300E, 40, 990, XX, 34, NEQ,\n"
        f"{basin}, {number:02d}, {cycle}, 03, {aid}, 6, 260N, 1310E, 45, 985, XX, 34, NEQ,\n"
    )


class WeatherLabSourceTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(data_time="202609041200", atcf_id="wp222026", fcst_hours=240)

    def test_new_paths_and_historical_fallback(self):
        for model in VTG.RAW_GITHUB_MODELS:
            urls = VTG.raw_github_candidate_urls(self.settings, model)
            self.assertTrue(urls[0].endswith(f"forecast_files/2026/09/04/{model}_2026_09_04T12_00_atcf_a_deck.txt"))
            self.assertEqual(1 if model == "WNV3" else 2, len(urls))
        self.assertIn("forecast_files/2026_09_04/FNV3_2026_09_04T12_00_atcf_a_deck.txt",
                      VTG.raw_github_candidate_urls(self.settings, "FNV3")[1])

    def test_raw_headers_are_not_assumed_to_have_six_lines(self):
        for header in ["", "# one line\n", "# a\n" * 12]:
            text = header + "\n".join(atcf().splitlines()[3:])
            frame = VTG.read_atcf_csv(text, source="RAW.GITHUB")
            self.assertEqual([0, 6], frame["FTM"].tolist())

    def test_missing_or_wrong_cycle_new_path_falls_back_without_disk_cache(self):
        for primary in [None, atcf("FNV3", cycle="2026090406"), "<html>error</html>"]:
            with self.subTest(primary=primary):
                with patch("VTG.fetch_text", side_effect=[primary, atcf("FNV3")]) as fetch:
                    result = VTG.fetch_raw_github_text(object(), self.settings, "FNV3")
                self.assertEqual(atcf("FNV3"), result)
                self.assertEqual(2, fetch.call_count)
                self.assertTrue(all(call.kwargs["cache_dir"] is None for call in fetch.call_args_list))

    def test_current_new_path_does_not_mix_legacy_checkpoint(self):
        with patch("VTG.fetch_text", return_value=atcf("FNV3")) as fetch:
            self.assertEqual(atcf("FNV3"), VTG.fetch_raw_github_text(object(), self.settings, "FNV3"))
        self.assertEqual(1, fetch.call_count)

    def test_wn3_never_falls_back_to_wn2(self):
        with patch("VTG.fetch_text", return_value=atcf("FNV3")) as fetch:
            self.assertIsNone(VTG.fetch_raw_github_text(object(), self.settings, "WNV3"))
        self.assertEqual(1, fetch.call_count)

    def test_global_file_filters_storm_basin_as_well_as_number(self):
        url = VTG.raw_github_url(self.settings, "WNV3")
        body = atcf() + atcf(basin="IO") + atcf(number=23)
        with patch("VTG.atcf_urls", return_value=[("RAW.GITHUB", url, 0)]):
            with patch("VTG.fetch_text", return_value=body):
                frame = VTG.fetch_atcf_data(object(), self.settings)
        self.assertEqual(2, len(frame))
        self.assertEqual(["WP"], frame["ATCF_BASIN"].unique().tolist())
        self.assertEqual([22], frame["ATCF_NUMBER"].unique().tolist())

    def test_both_generations_remain_separate_through_source_selection(self):
        raw = pd.concat([
            VTG.read_atcf_csv(atcf("FNV3"), source="RAW.GITHUB"),
            VTG.read_atcf_csv(atcf("WNV3"), source="RAW.GITHUB"),
        ], ignore_index=True)
        converted = VTG.atcf_to_kma_schema(raw, self.settings)
        selected = VTG.select_model_sources_by_priority(converted, self.settings)
        self.assertEqual({"WNC", "WNV3"}, set(selected["SRC"]))
        self.assertEqual({"FNV3", "WNV3"}, set(selected[VTG.RAW_MODEL_COLUMN]))
        self.assertEqual(["RAW.GITHUB"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())
        self.assertEqual("WNC", VTG.MODEL_SOURCE_ALIASES["FGNE"])
        self.assertEqual("WNV3", VTG.MODEL_SOURCE_ALIASES["WNV3"])

    def test_catalog_order_categories_and_distinct_colors(self):
        names = [model["name"] for model in VTG.MODEL_INFO]
        self.assertEqual(["GENC", "WNC", "WNV3", "HKO_AREC"],
                         names[names.index("GENC"):names.index("GENC") + 4])
        models = {model["name"]: model for model in VTG.MODEL_INFO}
        self.assertEqual("WeatherNext2 Cyclones", models["WNC"]["label"])
        self.assertEqual("WeatherNext3 Cyclones", models["WNV3"]["label"])
        self.assertNotEqual(models["WNC"]["color"], models["WNV3"]["color"])
        self.assertEqual(("AI", "ENSEMBLE"), VTG.MODEL_CATEGORIES["WNV3"])


if __name__ == "__main__":
    unittest.main()
