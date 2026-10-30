import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import numpy as np
import pandas as pd
from PIL import Image
from cartopy.mpl.geoaxes import GeoAxes
from cartopy.mpl.gridliner import Gridliner

import VTG
import vtg_render_runtime as runtime
from test_vtg_zero_hour_pressure import official_point, track


class RenderRuntimeTests(unittest.TestCase):
    def test_locked_versions_are_checked_not_just_a_requirements_timestamp(self):
        report = {"python": runtime.PYTHON_VERSION, "packages": runtime.pinned_versions()}
        self.assertEqual([], runtime.check_runtime(report))
        report["packages"]["cartopy"] = "0.24.1"
        self.assertTrue(any("cartopy" in error for error in runtime.check_runtime(report)))
        report["python"] = "3.14.4"
        self.assertTrue(any("Python" in error for error in runtime.check_runtime(report)))

    def test_text_uses_bundled_font_file_even_if_family_resolution_differs(self):
        prop = VTG.plot_font_properties(size=10)
        self.assertEqual(VTG.PREFERRED_PLOT_FONT_FILE.resolve(), Path(prop.get_file()).resolve())
        self.assertEqual(10, prop.get_size_in_points())
        with patch.object(VTG, "PREFERRED_PLOT_FONT_FILE", Path("missing-font.ttf")):
            with self.assertRaisesRegex(RuntimeError, "font.*missing"):
                VTG.configure_plot_fonts()

    def test_output_is_fully_opaque_and_left_aligned_with_explicit_tick_fonts(self):
        frame = pd.concat([official_point(), track(model="WMSH")], ignore_index=True)
        with tempfile.TemporaryDirectory() as folder:
            settings = VTG.Settings(data_time="202610210000", typ_number=30, typ_name="CHAMPI",
                                    fcst_hours=240, output_root=Path(folder), show_plot=False,
                                    figure_width=8, figure_height=6)
            figure = None
            try:
                with patch.object(GeoAxes, "add_feature"), patch.object(VTG, "filtered_country_borders"), \
                        patch.object(VTG.plt, "close"):
                    path = VTG.plot_guidance(frame, pd.DataFrame(), settings, "TYP")
                    figure = VTG.plt.gcf()
                figure.canvas.draw()
                with Image.open(path) as image:
                    self.assertEqual(255, int(np.asarray(image.convert("RGBA"))[:, :, 3].min()))
                ax = figure.axes[0]
                self.assertAlmostEqual(0, ax.bbox.x0)
                for gl in (child for child in ax.get_children() if isinstance(child, Gridliner)):
                    for label in gl.xlabel_artists + gl.ylabel_artists:
                        self.assertEqual(str(VTG.PREFERRED_PLOT_FONT_FILE), label.get_fontproperties().get_file())
                for axes in figure.axes:
                    for text in axes.texts:
                        if text.get_text():
                            self.assertEqual(str(VTG.PREFERRED_PLOT_FONT_FILE), text.get_fontproperties().get_file())
            finally:
                if figure is not None:
                    VTG.plt.close(figure)


if __name__ == "__main__":
    unittest.main()
