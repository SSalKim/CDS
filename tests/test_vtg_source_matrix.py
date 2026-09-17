import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import VTG
import vtg_auto
import vtg_sources
from DMDW_VTG import query_models


SOURCE_COLUMNS = {
    "APIHUB": "apihub",
    "DMDW": "dmdw",
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
            column = SOURCE_COLUMNS[source]
            actual = {row["name"] for row in VTG.MODEL_SOURCES if row.get(column)}
            self.assertEqual(expected, actual, source)

        self.assertEqual(EXPECTED_SOURCE_MODELS["DMDW"], VTG.DMDW_ENABLED_MODEL_IDS)
        self.assertIs(VTG.MODEL_SOURCES, vtg_sources.MODEL_SOURCES)
        self.assertIs(VTG.DMDW_ENABLED_MODEL_IDS, query_models.DMDW_ENABLED_MODEL_IDS)

    def test_registry_rows_and_snapshot_policy_are_consistent(self):
        names = [row["name"] for row in VTG.MODEL_SOURCES]
        self.assertEqual(len(names), len(set(names)))
        self.assertEqual(VTG.MODEL_NAMES - {"KMA"}, set(names))
        for row in VTG.MODEL_SOURCES:
            self.assertIsInstance(row["dmdw"], bool)
            for column in (*SOURCE_COLUMNS.values(), "noaa"):
                if column != "dmdw":
                    self.assertTrue(row[column] is None or isinstance(row[column], str))
        self.assertTrue(set(VTG.SMCA_PERSISTED_MODEL_IDS) <= VTG.smca_keys().keys())
        self.assertEqual(
            ("smca_aicon_snapshot_path", "smca_aifsm_snapshot_path", "smca_aigfs_snapshot_path"),
            tuple(vtg_sources.SMCA_SNAPSHOT_KEYS.values()),
        )
        self.assertTrue(set(vtg_sources.SMCA_SNAPSHOT_KEYS.values()) <= set(vtg_auto.MANIFEST_METADATA_KEYS))

    def test_alias_preferences_remain_stable(self):
        expected = {
            "ECMWF_TIGGE": ("ECMWF", 1), "ECM_SPR_D": ("ECMWF", 2),
            "ECM_SPR_E": ("ECMWF_EPS", 1), "KEPS": ("UM_KEPS", 1),
            "GFS_TIGGE": ("GFS", 1), "NCEP_TIGGE": ("GFS", 2),
            "CMSC": ("CMC", 1), "CMSC_EPS": ("CMC_EPS", 1),
            "NOGAPS": ("NAVGEM", 1), "ECMF_AIFS": ("ECMWF_AIFS", 1),
            "GPEC": ("GCEC_AI", 2), "GPKM": ("GCKM_AI", 2), "GPUM": ("GCUM_AI", 2),
        }
        expected.update({name[:-3]: (name, 1) for name in VTG.MODEL_NAMES if name.endswith("_AI")})
        for raw_id, (model, priority) in expected.items():
            with self.subTest(raw_id=raw_id):
                self.assertEqual(model, VTG.MODEL_SOURCE_ALIASES[raw_id])
                self.assertEqual(priority, VTG.MODEL_ALIAS_PRIORITIES[raw_id])
                self.assertIn(raw_id, VTG.SOURCE_MODEL_IDS["APIHUB"])
        self.assertEqual("UKM", VTG.MODEL_SOURCE_ALIASES["EGRR"])
        self.assertNotIn("NOAA", VTG.SOURCE_ORDER)
        self.assertEqual(set(), VTG.SOURCE_MODEL_IDS["DMDW"])

    def test_dmdw_layer_names_and_ensemble_members(self):
        expected = {
            "ecmwf hres": "ECMWF", "ec_aifs_single": "ECMWF_AIFS",
            "gefs": "GFS_EPS", "hafs-b": "HAFS", "kim": "KIM_6h",
            "kim 3h": "KIM_3h", "jens": "TEPS", "ukmo": "UKM",
        }
        prefixes = {
            "EC_AIFS": "ECMWF_AIFS_EPS", "ECMWF": "ECMWF_EPS",
            "CMC": "CMC_EPS", "GFS": "GFS_EPS", "KIM": "KIM_EPS", "FNMOC": "FNMOC_EPS",
        }
        expected.update({prefix + suffix: model for prefix, model in prefixes.items()
                         for suffix in ("_MEM001", "_MEM_50")})
        for raw_id, model in expected.items():
            self.assertEqual(model, query_models.mapped_model_id(f"  {raw_id}  "), raw_id)
        for raw_id in ("UNKNOWN_MEM001", "CMC_MEM_", "GFS_MEM_01x", "AFUM"):
            self.assertEqual(raw_id.upper(), query_models.mapped_model_id(raw_id))

    def test_lookup_results_are_independent_and_preserve_missing_ids(self):
        for lookup, raw_id, model in (
            (VTG.polarwx_keys, "aigfs", "AGFS"), (VTG.smca_keys, "WN3C", "WNV3"),
        ):
            self.assertEqual(model, lookup().pop(raw_id))
            self.assertEqual(model, lookup()[raw_id])
        self.assertEqual("FNV3", VTG.expected_raw_model_id("WNC", "RAW.GITHUB"))
        self.assertEqual("WN3C", VTG.expected_raw_model_id("WNV3", "SMCA.FUN"))
        for model, source in (("ECMWF", "DMDW"), ("ECMWF", "RAL.UCAR"),
                              ("UNKNOWN", "APIHUB"), ("ECMWF", "UNKNOWN")):
            self.assertEqual("", VTG.expected_raw_model_id(model, source))

    def test_render_signature_tracks_both_renderer_and_source_registry(self):
        self.assertTrue(VTG.render_signature())
        self.assertEqual(VTG.render_signature(), vtg_auto.current_render_signature())
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual("", vtg_sources.render_code_signature(root))
            renderer = root / "VTG.py"
            registry = root / "vtg_sources.py"
            renderer.write_text("renderer-v1", encoding="utf-8")
            registry.write_text("sources-v1", encoding="utf-8")
            with patch.object(VTG, "PROJECT_ROOT", root), patch.object(vtg_auto, "PROJECT_ROOT", root):
                previous = {"metadata": {"render_signature": VTG.render_signature()}}
                initial = vtg_auto.current_render_signature()
                self.assertTrue(vtg_auto.previous_render_signature_matches(previous, initial))
                for file in (registry, renderer):
                    with self.subTest(file=file.name):
                        before = VTG.render_signature()
                        file.write_text("changed-v2", encoding="utf-8")
                        after = VTG.render_signature()
                        self.assertNotEqual(before, after)
                        self.assertEqual(after, vtg_auto.current_render_signature())
                        self.assertFalse(vtg_auto.previous_render_signature_matches(previous, after))

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
