"""Offline date-line panel geometry: no upstream observation requests."""
import unittest

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

import VTG


class MapPanelAlignmentTests(unittest.TestCase):
    def test_fixed_east_edge_meets_legend_without_map_distortion(self):
        for width, height, dpi in ((16, 12, 100), (8, 6, 100), (16, 12, 150)):
            # Different projected aspect assumptions must not recreate a gutter.
            for north in (51.45, 51.65):
                with self.subTest(width=width, dpi=dpi, north=north):
                    fraction = 1 / 1.325
                    fig = plt.figure(figsize=(width * 1.325, height), dpi=dpi)
                    try:
                        ax = fig.add_axes([0, 0, fraction, 1], projection=ccrs.Mercator())
                        ax.set_extent([100, 179.9, 0, north], crs=ccrs.PlateCarree())
                        before_x = ax.get_xlim()
                        before_south = ax.get_ylim()[0]
                        VTG.fit_fixed_map_panel(ax, fig_width=width, fig_height=height)
                        ax.set_anchor("W")
                        legend = fig.add_axes([fraction, 0, 1 - fraction, 1])
                        fig.canvas.draw()
                        self.assertAlmostEqual(ax.bbox.x1, legend.bbox.x0, places=6)
                        self.assertAlmostEqual(ax.bbox.height, height * dpi, places=6)
                        self.assertEqual(before_x, ax.get_xlim())
                        self.assertEqual(before_south, ax.get_ylim()[0])
                        self.assertEqual(1.0, float(ax.get_aspect()))
                        self.assertFalse(ax.spines["geo"].get_visible())
                        east = ccrs.PlateCarree().transform_point(ax.get_xlim()[1], 0, ax.projection)[0]
                        self.assertAlmostEqual(179.9, east, places=6)
                    finally:
                        plt.close(fig)


if __name__ == "__main__":
    unittest.main()
