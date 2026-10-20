import io
import unittest
from contextlib import redirect_stdout
from dataclasses import replace
from unittest.mock import patch
from urllib.error import HTTPError

import pandas as pd

import VTG
import vtg_auto


CYCLE = "202610200600"
IDENTITY = "wp292026"
RAW_MODELS = {
    "CMC": "CMC", "AVNO": "GFS", "CTCX": "CTCX", "EGRR": "UKM",
    "HFSA": "HAFS", "NVGM": "NAVGEM", "HWRF": "HWRF",
}


def adeck(number=29, cycle=CYCLE[:10], models=RAW_MODELS):
    return "\n".join(
        f"WP,{number},{cycle},03,{model},{hour},160N,1500E,40,990,XX,34,NEQ,0,0,0,0"
        for model in models for hour in (0, 6, 12)
    )


def bdeck(cycle=CYCLE[:10]):
    return f"WP,29,{cycle},,BEST,0,160N,1500E,40,990,TS"


class EmcAtcfTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(
            typ_number=30, storm_year="2026", data_time=CYCLE,
            fcst_hours=240, atcf_id=IDENTITY,
        )

    def fetch(self, text):
        url = VTG.emc_adeck_url(IDENTITY)
        with patch.object(VTG, "atcf_urls", return_value=[("EMC.NCEP", url, 0)]), \
                patch.object(VTG, "fetch_text", return_value=text), \
                patch.object(VTG, "fetch_recent_atcf_cycle_text") as recent, \
                redirect_stdout(io.StringIO()):
            frame = VTG.fetch_atcf_data(object(), self.settings)
        recent.assert_not_called()
        return VTG.atcf_to_kma_schema(frame, self.settings)

    def test_urls_use_distinct_a_and_b_decks_for_each_identity(self):
        settings = replace(self.settings, extra_atcf_ids=("wp962026", IDENTITY))
        urls = [url for source, url, _ in VTG.atcf_urls(settings) if source == "EMC.NCEP"]
        base = "https://www.emc.ncep.noaa.gov/hurricane/DECKS_OPEN/"
        self.assertEqual([base + "awp292026.dat", base + "awp962026.dat"], urls)
        self.assertEqual(base + "bwp292026.dat", VTG.bdeck_url("WP292026"))
        self.assertEqual(base + "aep152026.dat", VTG.emc_adeck_url("EP152026"))
        self.assertEqual(base + "bcp012026.dat", VTG.bdeck_url("cp012026"))
        self.assertEqual("EMC.NCEP", vtg_auto.BDECK_SOURCE_URLS[0][0])
        self.assertEqual(VTG.bdeck_url(IDENTITY), vtg_auto.BDECK_SOURCE_URLS[0][1].format(atcf_id=IDENTITY))
        self.assertFalse(any("natyphoon" in url for _, url in vtg_auto.BDECK_SOURCE_URLS))

    def test_only_approved_models_pass_same_storm_cycle_and_lead_filters(self):
        text = "\n".join([
            adeck(models=(*RAW_MODELS, "COTC", "ECMF", "EEMN", "AFUM", "FGNE")),
            adeck(number=28), adeck(cycle="2026102000"),
            f"WP,29,{CYCLE[:10]},03,AVNO,246,160N,1500E,40,990",
        ])
        frame = self.fetch(text)
        self.assertEqual(21, len(frame))
        self.assertEqual(set(RAW_MODELS.values()), set(frame["SRC"]))
        self.assertEqual({"EMC.NCEP"}, set(frame[VTG.DATA_SOURCE_COLUMN]))
        for raw, model in RAW_MODELS.items():
            track = frame[frame["SRC"].eq(model)]
            self.assertEqual({raw}, set(track[VTG.RAW_MODEL_COLUMN]))
            self.assertEqual([0, 6, 12], track["TMD"].tolist())
            self.assertEqual(raw, VTG.expected_raw_model_id(model, "EMC.NCEP"))
        self.assertEqual(set(RAW_MODELS), VTG.SOURCE_MODEL_IDS["EMC.NCEP"])

    def test_emc_is_after_ral_but_before_knackwx_for_all_seven_models(self):
        emc = self.fetch(adeck())
        knackwx = emc.assign(**{VTG.DATA_SOURCE_COLUMN: "KNACKWX"})
        ral = emc.assign(**{VTG.DATA_SOURCE_COLUMN: "RAL.UCAR"})
        apihub = emc.assign(**{VTG.DATA_SOURCE_COLUMN: "APIHUB"})
        for frames, expected in (
            ([knackwx, emc], "EMC.NCEP"), ([knackwx, emc, ral], "RAL.UCAR"),
            ([knackwx, emc, ral, apihub], "APIHUB"), ([knackwx], "KNACKWX"),
        ):
            with self.subTest(expected=expected), redirect_stdout(io.StringIO()):
                selected = VTG.select_model_sources_by_priority(pd.concat(frames, ignore_index=True), self.settings)
            self.assertEqual(set(RAW_MODELS.values()), set(selected["SRC"]))
            self.assertEqual({expected}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_full_mutable_file_fetch_does_not_use_range_or_persistent_cache(self):
        url = VTG.emc_adeck_url(IDENTITY)
        with patch.object(VTG, "atcf_urls", return_value=[("EMC.NCEP", url, 0)]), \
                patch.object(VTG, "fetch_recent_atcf_cycle_text") as recent, \
                patch.object(VTG, "fetch_text", return_value=adeck()) as fetch, \
                redirect_stdout(io.StringIO()):
            VTG.fetch_atcf_data(object(), self.settings)
        recent.assert_not_called()
        self.assertIsNone(fetch.call_args.kwargs["cache_dir"])

    def test_missing_or_invalid_emc_data_leaves_knackwx_available(self):
        specs = [("EMC.NCEP", VTG.emc_adeck_url(IDENTITY), 0), ("KNACKWX", "knackwx", 0)]
        for missing in (None, "<!DOCTYPE html><html>Not found</html>", adeck(cycle="2026102000")):
            with self.subTest(missing=missing), \
                    patch.object(VTG, "atcf_urls", return_value=specs), \
                    patch.object(VTG, "fetch_text", side_effect=lambda session, url, **kwargs: missing if url == specs[0][1] else adeck()), \
                    redirect_stdout(io.StringIO()):
                raw = VTG.fetch_atcf_data(object(), self.settings)
                frame = VTG.atcf_to_kma_schema(raw, self.settings)
                selected = VTG.select_model_sources_by_priority(frame, self.settings)
            self.assertEqual({"KNACKWX"}, set(selected[VTG.DATA_SOURCE_COLUMN]))

    def test_emc_aliases_and_source_availability_use_new_source(self):
        for alias in ("EMC.NCEP", "EMC NCEP ATCF", "NOAA", "NCEP"):
            self.assertEqual("EMC.NCEP", VTG.normalize_source_name(alias))
        for model in RAW_MODELS.values():
            priority = VTG.source_priority_for_model(model, self.settings)
            self.assertLess(priority.index("RAL.UCAR"), priority.index("EMC.NCEP"))
            self.assertLess(priority.index("EMC.NCEP"), priority.index("KNACKWX"))
        frame = self.fetch(adeck())
        entries, selected = VTG.source_availability_entries(frame, frame, self.settings)
        self.assertEqual(7, len(entries))
        for entry in entries:
            self.assertEqual("EMC.NCEP", entry["source"])
            self.assertTrue(entry["selected"] and entry["has_pressure"] and entry["has_wind"])
        self.assertEqual({"EMC.NCEP"}, {item["selected_source"] for item in selected.values()})

    def test_renderer_prefers_emc_best_analysis_and_falls_back_to_ral(self):
        for emc_text, expected in ((bdeck(), "EMC.NCEP"), (None, "RAL.UCAR"), (bdeck("2026102000"), "RAL.UCAR")):
            with self.subTest(expected=expected), \
                    patch.object(VTG, "fetch_text", side_effect=lambda session, url, **kwargs: emc_text if "DECKS_OPEN" in url else bdeck()):
                row, source = VTG.select_bdeck_analysis_row(object(), self.settings, max_offset_hours=12)
            self.assertEqual(expected, source)
            self.assertEqual(0, row["_offset_hours"])
            self.assertEqual("BEST", row["MODEL"])

    def test_auto_bdeck_prefers_emc_and_handles_404_with_ral_fallback(self):
        for missing in (False, True):
            def fetch(url, **kwargs):
                if missing and "DECKS_OPEN" in url:
                    raise HTTPError(url, 404, "Not found", None, None)
                return bdeck()

            with self.subTest(missing=missing), \
                    patch.dict(vtg_auto.BDECK_TEXT_CACHE, {}, clear=True), \
                    patch.dict(vtg_auto.BDECK_SOURCE_TEXT_CACHE, {}, clear=True), \
                    patch.dict(vtg_auto.BDECK_FETCH_STATS, vtg_auto.BDECK_FETCH_STATS.copy(), clear=True), \
                    patch.object(vtg_auto, "HTTP_FETCH_CACHE_DIR", None), \
                    patch.object(vtg_auto, "fetch_text", side_effect=fetch) as fetcher, \
                    redirect_stdout(io.StringIO()):
                self.assertEqual(bdeck(), vtg_auto.fetch_bdeck_text(IDENTITY))
                calls = [call.args[0] for call in fetcher.call_args_list]
            self.assertEqual(VTG.bdeck_url(IDENTITY), calls[0])
            self.assertEqual(2 if missing else 1, len(calls))
            if missing:
                self.assertEqual(VTG.ral_ucar_bdeck_url(IDENTITY), calls[1])

    def test_auto_uses_exact_ral_analysis_if_emc_is_stale(self):
        with patch.dict(vtg_auto.BDECK_TEXT_CACHE, {}, clear=True), \
                patch.dict(vtg_auto.BDECK_SOURCE_TEXT_CACHE, {}, clear=True), \
                patch.dict(vtg_auto.BDECK_FETCH_STATS, vtg_auto.BDECK_FETCH_STATS.copy(), clear=True), \
                patch.object(vtg_auto, "HTTP_FETCH_CACHE_DIR", None), \
                patch.object(vtg_auto, "fetch_text", side_effect=lambda url, **kwargs: bdeck("2026102000") if "DECKS_OPEN" in url else bdeck()), \
                redirect_stdout(io.StringIO()):
            self.assertEqual(bdeck(), vtg_auto.fetch_bdeck_text_for_data_time(IDENTITY, data_time=CYCLE))


if __name__ == "__main__":
    unittest.main()
