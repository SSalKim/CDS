import importlib.util
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

import numpy as np
import xarray as xr

spec = importlib.util.spec_from_file_location("wm6_grid_sample", Path(__file__).resolve().parents[1] / "analysis/wm6_grid_sample.py")
sample = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample)


class GridSelectionTest(unittest.TestCase):
    def test_selection_excludes_unrequested_chunks(self):
        self.assertTrue(sample.needed_part("ensemble_mean/temperature_500/c/0/0"))
        self.assertTrue(sample.needed_part("ensemble_mean/temperature_500/zarr.json"))
        self.assertTrue(sample.needed_part("zarr.json"))
        self.assertFalse(sample.needed_part("ensemble_mean/specific_humidity_500/c/0/0"))
        self.assertFalse(sample.needed_part("ensemble_mean/temperature_700/c/0/0"))
        self.assertFalse(sample.needed_part("members/temperature_500/c/0/0"))

    def dataset(self, level_name="level", levels=(500, 700), member=False):
        dims = ["time", level_name, "latitude", "longitude"]
        values = np.arange(8).reshape(1, 2, 2, 2)
        coords = {"time": [0], level_name: list(levels), "latitude": [10, 11], "longitude": [120, 121]}
        if member:
            dims.insert(0, "member")
            values = np.stack([values, values])
            coords["member"] = [0, 1]
        return xr.Dataset({"temperature": (dims, values)}, coords=coords)

    def test_exact_500_hpa_mean(self):
        result = sample.select_field(self.dataset(), "temperature", "latitude", "longitude")
        np.testing.assert_array_equal(result.values, np.arange(4).reshape(2, 2))

    def test_pressure_in_pa(self):
        result = sample.select_field(self.dataset("pressure", (50000, 70000)), "temperature", "latitude", "longitude")
        self.assertEqual(result.shape, (2, 2))

    def test_missing_level_is_not_nearest_neighbor(self):
        with self.assertRaisesRegex(ValueError, "500 hPa"):
            sample.select_field(self.dataset(levels=(400, 600)), "temperature", "latitude", "longitude")

    def test_never_silently_average_or_choose_member(self):
        with self.assertRaisesRegex(ValueError, "non-singleton"):
            sample.select_field(self.dataset(member=True), "temperature", "latitude", "longitude")

    def test_named_mean(self):
        ds = self.dataset().rename({"temperature": "temperature_mean"})
        self.assertEqual(sample.select_field(ds, "temperature", "latitude", "longitude").shape, (2, 2))

    def test_provider_500_suffix(self):
        ds = self.dataset().rename({"temperature": "temperature_500"})
        self.assertEqual(sample.select_field(ds, "temperature", "latitude", "longitude").shape, (2, 2))

    def test_real_zarr_layout_and_exact_time(self):
        from zarr.storage import ZipStore
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            store = ZipStore(directory / "sample.zip", mode="w")
            lat, lon = np.linspace(0, 60, 121), np.linspace(50, 180, 261)
            attrs = {"initialization_time": "2026-11-06T00:00:00Z", "forecast_hour": 24,
                     "valid_time": "2026-11-07T00:00:00Z"}
            xr.Dataset(coords={"latitude": lat, "longitude": lon}, attrs=attrs).to_zarr(store, mode="w", consolidated=False)
            fields = {}
            for name in sample.FIELDS:
                raw = name + "_500" if name in {"temperature", "geopotential", "wind_u", "wind_v"} else name
                fields[raw] = (("latitude", "longitude"), np.ones((len(lat), len(lon)), dtype=np.float32))
            xr.Dataset(fields).to_zarr(store, group="ensemble_mean", mode="a", consolidated=False)
            store.close()
            metrics = {}
            cycle = datetime(2026, 11, 6, tzinfo=timezone.utc)
            sample.extract(directory / "sample.zip", directory, cycle, 24, metrics)
            with np.load(directory / "asia_fields.npz") as result:
                self.assertEqual(result["temperature"].shape, (121, 261))
                self.assertEqual(int(result["forecast_hour"]), 24)
            with self.assertRaisesRegex(ValueError, "forecast hour"):
                sample.extract(directory / "sample.zip", directory, cycle, 27, {})


if __name__ == "__main__":
    unittest.main()
