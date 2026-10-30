import json
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image

from vtg_render_parity import compare, image_signature


class RenderParityTests(unittest.TestCase):
    def test_only_isolated_one_level_rounding_is_allowed(self):
        with tempfile.TemporaryDirectory() as folder:
            left, right = Path(folder) / "left", Path(folder) / "right"
            for directory in (left, right):
                directory.mkdir()
            for changed, difference, accepted in ((0, 0, True), (1, 1, True),
                                                   (1, 2, False), (2, 1, False)):
                for directory in (left, right):
                    pixels = np.full((100, 100, 4), 255, dtype=np.uint8)
                    if directory == right:
                        pixels[0, :changed, 0] -= difference
                    images = {}
                    for name in ("120h.png", "240h.png"):
                        Image.fromarray(pixels).save(directory / name)
                        images[name] = image_signature(directory / name)
                    (directory / "report.json").write_text(json.dumps({
                        "runtime": {}, "input_sha256": "same", "map_assets": {}, "images": images,
                    }))
                if accepted:
                    compare(left, right)
                else:
                    with self.assertRaisesRegex(RuntimeError, "pixel mismatch"):
                        compare(left, right)


if __name__ == "__main__":
    unittest.main()
