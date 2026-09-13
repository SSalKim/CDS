import json
import unittest

import pandas as pd

import VTG


class PolarwxTests(unittest.TestCase):
    def settings(self) -> VTG.Settings:
        return VTG.Settings(
            typ_number=23,
            typ_name="BANG-LANG",
            storm_stage="TYP",
            storm_year="2026",
            atcf_id="wp202026",
            data_time="202608291200",
            fcst_hours=120,
        )

    def test_raw_aigfs_track_maps_to_agfs(self):
        payload = {
            "aigfs": {
                "fhr": [0, 6, 12],
                "time": ["2026082912", "2026082918", "2026083000"],
                "lat": [25.25, 27.5, 29.75],
                "lon": [169.0, 169.0, 169.0],
                "vmax": [75, 53, 51],
                "mslp": [971, 986, 992],
                "interp": {
                    "fhr": [0, 12],
                    "time": ["2026082912", "2026083000"],
                    "lat": [99.0, 99.0],
                    "lon": [99.0, 99.0],
                    "source_cycle": "2026082906",
                },
            },
        }

        frame = VTG.read_polarwx_json(json.dumps(payload), self.settings())

        self.assertEqual(["AGFS"], frame["SRC"].unique().tolist())
        self.assertEqual(["POLARWX"], frame[VTG.DATA_SOURCE_COLUMN].unique().tolist())
        self.assertEqual(["AIGFS"], frame[VTG.RAW_MODEL_COLUMN].unique().tolist())
        self.assertEqual([0.0, 6.0, 12.0], frame["TMD"].tolist())
        self.assertEqual([25.25, 27.5, 29.75], frame["LAT"].tolist())

    def test_empty_raw_aigfs_does_not_substitute_prior_cycle_interpolation(self):
        payload = {
            "aigfs": {
                "fhr": [],
                "time": [],
                "lat": [],
                "lon": [],
                "vmax": [],
                "mslp": [],
                "interp": {
                    "fhr": [0, 12],
                    "time": ["2026082918", "2026083006"],
                    "lat": [27.7, 32.0],
                    "lon": [169.2, 168.3],
                    "source_cycle": "2026082912",
                },
            },
        }

        frame = VTG.read_polarwx_json(json.dumps(payload), self.settings())

        self.assertTrue(frame.empty)

    def test_polarwx_aigfs_wins_normal_source_priority(self):
        polarwx = VTG.read_polarwx_json(
            json.dumps({
                "aigfs": {
                    "fhr": [0, 6],
                    "time": ["2026082912", "2026082918"],
                    "lat": [25.25, 27.5],
                    "lon": [169.0, 169.0],
                    "vmax": [75, 53],
                    "mslp": [971, 986],
                },
            }),
            self.settings(),
        )
        knackwx = polarwx.copy()
        knackwx[VTG.DATA_SOURCE_COLUMN] = "KNACKWX"
        knackwx["LAT"] += 0.1

        selected = VTG.select_model_sources_by_priority(
            pd.concat([knackwx, polarwx], ignore_index=True),
            self.settings(),
        )

        self.assertEqual(["POLARWX"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

    def test_ukmet_mean_maps_to_ukmo_eps(self):
        payload = {
            "ukmet_mean": {
                "fhr": [0, 6, 12],
                "time": ["2026082912", "2026082918", "2026083000"],
                "lat": [22.01, 23.55, 25.35],
                "lon": [167.34, 167.71, 167.59],
                "members": [35, 29, 24],
                "vmax": [37.35, 38.51, 38.92],
                "mslp": [998.83, 997.42, 998.56],
            },
        }

        frame = VTG.read_polarwx_json(json.dumps(payload), self.settings())

        self.assertEqual(["UKMO_EPS"], frame["SRC"].unique().tolist())
        self.assertEqual(["POLARWX"], frame[VTG.DATA_SOURCE_COLUMN].unique().tolist())
        self.assertEqual(["UKMET_MEAN"], frame[VTG.RAW_MODEL_COLUMN].unique().tolist())
        self.assertEqual([0.0, 6.0, 12.0], frame["TMD"].tolist())
        self.assertEqual([998.83, 997.42, 998.56], frame["PS"].tolist())

    def test_ukmo_eps_prefers_pressure_data_then_normal_source_priority(self):
        polarwx = VTG.read_polarwx_json(
            json.dumps({
                "ukmet_mean": {
                    "fhr": [0, 6],
                    "time": ["2026082912", "2026082918"],
                    "lat": [22.01, 23.55],
                    "lon": [167.34, 167.71],
                    "vmax": [37.35, 38.51],
                    "mslp": [998.83, 997.42],
                },
            }),
            self.settings(),
        )
        knackwx = polarwx.copy()
        knackwx[VTG.DATA_SOURCE_COLUMN] = "KNACKWX"
        knackwx["LAT"] += 0.1
        ral = polarwx.copy()
        ral[VTG.DATA_SOURCE_COLUMN] = "RAL.UCAR"
        ral["LAT"] += 0.2
        ral["PS"] = 0.0
        apihub = polarwx.copy()
        apihub[VTG.DATA_SOURCE_COLUMN] = "APIHUB"
        apihub["LAT"] += 0.3
        apihub["PS"] = 0.0

        all_sources = pd.concat([ral, knackwx, polarwx, apihub], ignore_index=True)
        selected = VTG.select_model_sources_by_priority(all_sources, self.settings())
        self.assertEqual(["POLARWX"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

        polarwx_without_pressure = polarwx.copy()
        polarwx_without_pressure["PS"] = 0.0
        selected = VTG.select_model_sources_by_priority(
            pd.concat([ral, knackwx, polarwx_without_pressure, apihub], ignore_index=True),
            self.settings(),
        )
        self.assertEqual(["KNACKWX"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

        knackwx_without_pressure = knackwx.copy()
        knackwx_without_pressure["PS"] = 0.0
        no_pressure = pd.concat(
            [ral, knackwx_without_pressure, polarwx_without_pressure, apihub],
            ignore_index=True,
        )
        selected = VTG.select_model_sources_by_priority(no_pressure, self.settings())
        self.assertEqual(["APIHUB"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())

        override_settings = VTG.Settings(
            data_time=self.settings().data_time,
            fcst_hours=self.settings().fcst_hours,
            source_overrides=(("UKMO_EPS", "RAL.UCAR"),),
        )
        selected = VTG.select_model_sources_by_priority(all_sources, override_settings)
        self.assertEqual(["RAL.UCAR"], selected[VTG.DATA_SOURCE_COLUMN].unique().tolist())


if __name__ == "__main__":
    unittest.main()
