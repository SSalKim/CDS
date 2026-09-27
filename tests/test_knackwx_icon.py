import io
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

import pandas as pd

import VTG


KNACKWX_TEXT = "\n".join([
    f"WP,25,2026092618,03,{model},{hour},139N,1520E,35,999,XX,34,NEQ,0,0,0,0"
    for model in ("DWIC", "ICMN") for hour in (0, 6, 12)
] + [
    "WP,25,2026092612,03,DWIC,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,26,2026092618,03,ICMN,6,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
    "WP,25,2026092618,03,DWIC,246,139N,1520E,35,999,XX,34,NEQ,0,0,0,0",
])


class KnackwxIconTests(unittest.TestCase):
    def setUp(self):
        self.settings = VTG.Settings(
            typ_number=25, storm_stage="TYP", storm_year="2026",
            data_time="202609261800", fcst_hours=240, atcf_id="wp252026",
        )

    def fetch_tracks(self):
        url = VTG.knackwx_url(self.settings.atcf_id, self.settings.data_time)
        with patch("VTG.atcf_urls", return_value=[("KNACKWX", url, 0)]), \
                patch("VTG.fetch_text", return_value=KNACKWX_TEXT), \
                redirect_stdout(io.StringIO()):
            raw = VTG.fetch_atcf_data(object(), self.settings)
        return VTG.atcf_to_kma_schema(raw, self.settings)

    def test_icon_codes_pass_fetch_filters_and_keep_separate_models(self):
        frame = self.fetch_tracks()
        self.assertEqual(6, len(frame))
        self.assertEqual({"ICON", "ICON_EPS"}, set(frame["SRC"]))
        for model, raw_id in (("ICON", "DWIC"), ("ICON_EPS", "ICMN")):
            with self.subTest(model=model):
                track = frame[frame["SRC"].eq(model)]
                self.assertEqual([0, 6, 12], track["TMD"].tolist())
                self.assertEqual({raw_id}, set(track[VTG.RAW_MODEL_COLUMN]))
                self.assertEqual({"KNACKWX"}, set(track[VTG.DATA_SOURCE_COLUMN]))
                self.assertEqual(raw_id, VTG.expected_raw_model_id(model, "KNACKWX"))

    def test_polarwx_remains_preferred_with_knackwx_as_fallback(self):
        knackwx = self.fetch_tracks()
        polarwx = knackwx.copy()
        polarwx[VTG.DATA_SOURCE_COLUMN] = "POLARWX"
        polarwx[VTG.RAW_MODEL_COLUMN] = polarwx["SRC"].map({
            "ICON": "icon", "ICON_EPS": "icon_ens_mean",
        })
        with redirect_stdout(io.StringIO()):
            selected = VTG.select_model_sources_by_priority(
                pd.concat([knackwx, polarwx]), self.settings,
            )
            fallback = VTG.select_model_sources_by_priority(knackwx, self.settings)
        self.assertEqual({"POLARWX"}, set(selected[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual({"KNACKWX"}, set(fallback[VTG.DATA_SOURCE_COLUMN]))
        self.assertEqual({"ICON", "ICON_EPS"}, set(fallback["SRC"]))


if __name__ == "__main__":
    unittest.main()
