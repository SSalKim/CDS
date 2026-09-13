import json
import tempfile
import unittest
from pathlib import Path

import VTG
from DMDW_VTG import query_models


SOURCE_COLUMNS = {
    "APIHUB": "apihub",
    "RAW.GITHUB": "raw_github",
    "POLARWX": "polarwx",
    "SMCA.FUN": "smca",
    "RAL.UCAR": "ral_ucar",
    "KNACKWX": "knackwx",
}

EXPECTED_SOURCE_MODELS = {
    "APIHUB": {
        "ECMWF", "ECMWF_EPS", "KIM_3h", "KIM_6h", "KIM_GFDL_6h", "KIM_EPS",
        "UM", "UM_GFDL_6h", "UM_KEPS", "UKM", "UKMO_EPS", "GFS", "GFS_EPS",
        "CMC", "CMC_EPS", "JGSM", "TEPS", "NAVGEM", "FNMOC_EPS", "HWRF", "HAFS",
        "ECMWF_AIFS", "IFEC_AI", "IFKM_AI", "FNEC_AI", "FNKM_AI", "FNUM_AI",
        "PGEC_AI", "PGKM_AI", "PGUM_AI", "GCEC_AI", "GCKM_AI", "GCUM_AI",
        "HKO_AREC", "HKO_FXEC", "HKO_FWEC",
    },
    "DMDW": {
        "ECMWF", "ECMWF_EPS", "KIM_3h", "KIM_6h", "KIM_EPS", "UKM", "GFS",
        "GFS_EPS", "CMC", "CMC_EPS", "JGSM", "TEPS", "NAVGEM", "FNMOC_EPS",
        "HWRF", "HAFS", "ECMWF_AIFS", "ECMWF_AIFS_EPS",
    },
    "RAW.GITHUB": {"GENC", "WNC", "WNV3"},
    "POLARWX": {
        "ECMWF", "ECMWF_EPS", "UKM", "UKMO_EPS", "GFS", "GFS_EPS", "CMC",
        "CMC_EPS", "ICON", "ICON_EPS", "HWRF", "HAFS", "ECMWF_AIFS",
        "ECMWF_AIFS_EPS", "AGFS", "GENC", "WNC",
    },
    "SMCA.FUN": {
        "ECMWF", "ECMWF_EPS", "GFS", "GFS_EPS", "ECMWF_AIFS",
        "ECMWF_AIFS_EPS", "AGFS", "AIGEFS", "AICON", "WNC", "WNV3",
    },
    "RAL.UCAR": {
        "UKM", "UKMO_EPS", "GFS", "GFS_EPS", "CMC", "CMC_EPS", "JGSM", "TEPS",
        "NAVGEM", "FNMOC_EPS", "CTCX", "COAMPS_EPS", "HWRF", "HAFS",
    },
    "KNACKWX": {
        "ECMWF", "ECMWF_EPS", "UKM", "UKMO_EPS", "GFS", "GFS_EPS", "CMC",
        "CMC_EPS", "JGSM", "TEPS", "NAVGEM", "FNMOC_EPS", "CTCX", "COAMPS_EPS",
        "HWRF", "HAFS", "ECMWF_AIFS", "ECMWF_AIFS_EPS", "AGFS", "AIGEFS",
        "GENC", "WNC", "WNV3",
    },
}


class VtgSourceMatrixTests(unittest.TestCase):
    def test_configured_sources_match_the_approved_matrix(self):
        for source, expected in EXPECTED_SOURCE_MODELS.items():
            if source == "DMDW":
                actual = set(VTG.DMDW_ENABLED_MODEL_IDS)
            else:
                column = SOURCE_COLUMNS[source]
                actual = {row["name"] for row in VTG.MODEL_SOURCES if row.get(column)}
            self.assertEqual(expected, actual, source)

        self.assertEqual(VTG.DMDW_ENABLED_MODEL_IDS, query_models.DMDW_ENABLED_MODEL_IDS)

    def test_smca_raw_model_ids_map_to_expected_models(self):
        raw_to_model = {
            "ECMWF": "ECMWF",
            "ECMWFM": "ECMWF_EPS",
            "GFS": "GFS",
            "GEFSM": "GFS_EPS",
            "AIFS": "ECMWF_AIFS",
            "AIFSM": "ECMWF_AIFS_EPS",
            "AIGFS": "AGFS",
            "AIGEFSM": "AIGEFS",
            "AICON": "AICON",
            "WN2C": "WNC",
            "WN3C": "WNV3",
        }
        forecasts = []
        for index, raw_model in enumerate(raw_to_model):
            forecasts.append({
                "sets": raw_model,
                "init_time_utc": "2026-09-07T18:00:00Z",
                "points": [
                    {
                        "forecastTime": 0,
                        "lat": 10.0 + index,
                        "lng": 130.0 + index,
                        "pressure": 990 - index,
                        "speed": 20 + index,
                    },
                ],
            })
        payload = json.dumps({
            "code": 200,
            "data": {
                "ident": "202624",
                "points": [{"forecast": forecasts}],
            },
        })
        settings = VTG.Settings(
            typ_number=24,
            typ_name="KROVANH",
            storm_year="2026",
            data_time="202609071800",
            fcst_hours=240,
        )

        frame = VTG.read_smca_json(payload, settings, typhoon_id="202624")

        actual = dict(zip(frame[VTG.RAW_MODEL_COLUMN], frame["SRC"]))
        self.assertEqual(raw_to_model, actual)

    def test_disabled_dmdw_models_are_rejected_from_existing_files(self):
        model_ids = ["ECMWF", "AFUM", "AGFS", "AIGEFS", "WNC"]
        payload = {
            "schema_version": 2,
            "source": "DMDW",
            "cycle_utc": "202609071800",
            "models": [
                {"model_id": model_id, "raw_model_id": model_id}
                for model_id in model_ids
            ],
            "point_columns": [
                "model_index", "lead_hour", "valid_time", "lat", "lon",
                "pressure_hpa", "wind",
            ],
            "points": [
                [index, 0, "202609071800", 15.0 + index, 135.0, 990, 20]
                for index in range(len(model_ids))
            ],
        }
        settings = VTG.Settings(data_time="202609071800", fcst_hours=240)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "dmdw.json"
            path.write_text(json.dumps(payload), encoding="utf-8")
            frame = VTG.read_dmdw_json(path, settings)

        self.assertEqual(["ECMWF"], frame["SRC"].tolist())

    def test_knackwx_maps_wnv3_separately_from_wnc(self):
        self.assertEqual("WNC", VTG.MODEL_SOURCE_ALIASES["FNV3"])
        self.assertEqual("WNV3", VTG.MODEL_SOURCE_ALIASES["WNV3"])


if __name__ == "__main__":
    unittest.main()
