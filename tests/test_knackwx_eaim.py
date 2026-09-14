import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import pandas as pd

import VTG


KNACKWX_TEXT = "\n".join([
    "WP,90,2026091400,03,EAIM,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,90,2026091400,03,EAIM,12,136N,1509E,36,998,XX,34,NEQ,0,0,0,0",
    "WP,90,2026091400,03,EAMN,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,90,2026091400,03,EEMN,6,134N,1527E,38,998,XX,34,NEQ,0,0,0,0",
    "WP,90,2026091318,03,EAIM,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,91,2026091400,03,EAIM,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,90,2026091400,03,EAIM,246,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
])


class KnackwxEaimTests(unittest.TestCase):
    def settings(self):
        return VTG.Settings(
            typ_number=53, storm_stage="TD", storm_year="2026",
            data_time="202609140000", fcst_hours=240, atcf_id="wp902026",
        )

    def test_eaim_passes_fetch_filter_and_maps_to_aifs_eps(self):
        settings = self.settings()
        url = VTG.knackwx_url(settings.atcf_id, settings.data_time)
        with patch("VTG.atcf_urls", return_value=[("KNACKWX", url, 0)]), \
                patch("VTG.fetch_text", return_value=KNACKWX_TEXT), \
                redirect_stdout(io.StringIO()):
            raw = VTG.fetch_atcf_data(object(), settings)

        self.assertEqual(["EAIM", "EAIM", "EEMN"], raw["MODEL"].tolist())
        self.assertEqual({2026091400}, set(raw["TM10"]))
        self.assertEqual({90}, set(raw["ATCF_NUMBER"]))
        self.assertEqual("EAIM", VTG.expected_raw_model_id("ECMWF_AIFS_EPS", "KNACKWX"))
        self.assertNotIn("EAMN", VTG.SOURCE_MODEL_IDS["KNACKWX"])

        frame = VTG.atcf_to_kma_schema(raw, settings)
        aifs_eps = frame[frame["SRC"].eq("ECMWF_AIFS_EPS")]
        self.assertEqual([6, 12], aifs_eps["TMD"].tolist())
        self.assertEqual({"EAIM"}, set(aifs_eps[VTG.RAW_MODEL_COLUMN]))
        self.assertEqual({"EEMN"}, set(frame.loc[frame["SRC"].eq("ECMWF_EPS"), VTG.RAW_MODEL_COLUMN]))

    def test_eaim_does_not_override_higher_priority_sources(self):
        settings = self.settings()
        raw = VTG.read_atcf_csv(KNACKWX_TEXT, source="KNACKWX")
        raw = raw[raw["MODEL"].eq("EAIM") & raw["TM10"].eq(2026091400) & raw["ATCF_NUMBER"].eq(90) & raw["FTM"].le(240)]
        knackwx = VTG.atcf_to_kma_schema(raw, settings)
        smca = knackwx.copy()
        smca[VTG.DATA_SOURCE_COLUMN] = "SMCA.FUN"
        smca[VTG.RAW_MODEL_COLUMN] = "AIFSM"

        with redirect_stdout(io.StringIO()):
            selected = VTG.select_model_sources_by_priority(pd.concat([knackwx, smca]), settings)
            fallback = VTG.select_model_sources_by_priority(knackwx, settings)
        self.assertEqual({"SMCA.FUN"}, set(selected[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual({"KNACKWX"}, set(fallback[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual({"ECMWF_AIFS_EPS"}, set(fallback["SRC"]))


if __name__ == "__main__":
    unittest.main()
