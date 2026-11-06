import importlib.util
from pathlib import Path
import sys
import types
import unittest

import numpy as np
import xarray as xr

if sys.platform == "win32":
    # The collector runs on Linux; allow its pure extraction helpers to be tested here.
    sys.modules.setdefault("resource", types.SimpleNamespace())
spec = importlib.util.spec_from_file_location("wm6_grid_sample", Path(__file__).resolve().parents[1] / "analysis/wm6_grid_sample.py")
sample = importlib.util.module_from_spec(spec)
spec.loader.exec_module(sample)


class GridSelectionTest(unittest.TestCase):
    def test_selection_excludes_unrequested_chunks(self):
        self.assertTrue(sample.needed_part("mean/temperature/0.0.0"))
        self.assertTrue(sample.needed_part("mean/temperature/.zarray"))
        self.assertTrue(sample.needed_part(".zattrs"))
        self.assertFalse(sample.needed_part("mean/specific_humidity/0.0.0"))

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


if __name__ == "__main__":
    unittest.main()
