import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from cartopy.mpl.geoaxes import GeoAxes

import VTG
from test_vtg_zero_hour_pressure import official_point, track


class ModelZorderTests(unittest.TestCase):
    def test_requested_model_zorders(self):
        expected = {
            "ECMWF": 69, "ECMWF_EPS": 68,
            "KIM_3h": 67, "KIM_6h": 67, "KIM_GFDL_6h": 67, "KIM_EPS": 66,
            "UM": 65, "UM_GFDL_6h": 65, "UM_KEPS": 64, "UKM": 65, "UKMO_EPS": 64,
            "GFS": 63, "GFS_EPS": 62, "CMC": 61, "CMC_EPS": 60,
            "NAVGEM": 59, "FNMOC_EPS": 58, "ICON": 57, "ICON_EPS": 56,
            "JGSM": 55, "TEPS": 54, "CTCX": 53, "COAMPS_EPS": 52, "AFUM": 51,
            "HAFS": 50, "HWRF": 49, "ECMWF_AIFS": 94, "ECMWF_AIFS_EPS": 93,
            "IFEC_AI": 92, "IFKM_AI": 91, "AGFS": 90, "AIGEFS": 89,
            "GEML": 88, "AICON": 87, "FNEC_AI": 86, "FNKM_AI": 83, "FNUM_AI": 80,
            "PGEC_AI": 85, "PGKM_AI": 82, "PGUM_AI": 79,
            "GCEC_AI": 84, "GCKM_AI": 81, "GCUM_AI": 78,
            "GENC": 97, "WNC": 98, "WNV3": 99, "WMSH": 95,
            "HKO_AREC": 77, "HKO_FXEC": 76, "HKO_FWEC": 75,
        }
        actual = {m["name"]: m["zorder"] for m in VTG.MODEL_INFO if "zorder" in m}
        self.assertEqual(expected, actual)
        self.assertLess(max(actual.values()), 100)

    def test_official_start_marker_renders_above_overlapping_model_markers(self):
        official = official_point()
        forecast = track("WINDBORNE", "WMSH", hours=(0, 24), pressures=(980, 970))
        forecast.loc[forecast["TMD"].eq(0), ["LAT", "LON"]] = [16.0, 150.0]
        frame = pd.concat([official, forecast], ignore_index=True)
        frame["FT_TIME"] = VTG.parse_ft_time(frame["FT_TM(UTC)"])
        with tempfile.TemporaryDirectory() as folder:
            settings = VTG.Settings(
                data_time="202610210000", fcst_hours=240, output_root=Path(folder),
                figure_width=8, figure_height=6, figure_dpi=100, show_plot=False,
            )
            figure = None
            try:
                # No coastline downloads or legend layout are needed for the overlap regression.
                with patch.object(GeoAxes, "add_feature"), \
                        patch.object(GeoAxes, "gridlines"), \
                        patch.object(VTG, "filtered_country_borders"), \
                        patch.object(VTG, "draw_header"), \
                        patch.object(VTG, "draw_model_legend_table"), \
                        patch.object(VTG, "plot_past_track"), \
                        patch.object(VTG.plt, "close"):
                    path = VTG.plot_guidance(frame, pd.DataFrame(), settings, "TYP")
                    figure = VTG.plt.gcf()
                self.assertTrue(path.exists())
                ax = figure.axes[0]
                official_marker = ax.lines[-1]
                self.assertEqual("white", official_marker.get_color())
                self.assertEqual(100, official_marker.get_zorder())
                self.assertEqual([95, 95], [line.get_zorder() for line in ax.lines[:-1]])
                self.assertTrue(all(m.get("zorder", 2) < official_marker.get_zorder() for m in VTG.MODEL_INFO))
                figure.canvas.draw()
                x, y = official_marker.get_transform().transform((150.0, 16.0))
                pixels = np.asarray(figure.canvas.buffer_rgba())
                rgb = pixels[pixels.shape[0] - 1 - round(y), round(x), :3]
                np.testing.assert_array_equal(rgb, [255, 255, 255])
            finally:
                if figure is not None:
                    VTG.plt.close(figure)


if __name__ == "__main__":
    unittest.main()
