import tempfile
import unittest
from pathlib import Path

import vtg_auto


class LinkedTdCanonicalizationTests(unittest.TestCase):
    def test_late_td_link_rewrites_stale_status_image_path_without_source_folder(self):
        with tempfile.TemporaryDirectory() as directory:
            output_root = Path(directory) / "data"
            target_dir = output_root / "2026" / "TYP_2623_BANG-LANG"
            target_image = target_dir / "images" / "TD_2642_NONAME_202608281200_240h.png"
            target_image.parent.mkdir(parents=True)
            target_image.write_bytes(b"png")

            status_path = output_root / "status.json"
            status = {
                "cycles": {
                    "202608281200": {
                        "td_2026_42_240h": {
                            "last_status": "ok",
                            "metadata": {
                                "generated_at_utc": "20260828215152",
                                "image_path": "data/2026/TD_2642_NONAME/images/TD_2642_NONAME_202608281200_240h.png",
                                "storm_stage": "TD",
                                "storm_year": "2026",
                                "typ_number": 42,
                                "typ_name": "NONAME",
                                "data_time": "202608281200",
                                "fcst_hours": 240,
                                "canonical_storm_stage": "TD",
                                "canonical_typ_number": 42,
                                "canonical_typ_name": "NONAME",
                            },
                        },
                    },
                },
            }
            links = {
                ("2026", 42): {
                    "linked_typ_number": 23,
                    "canonical_typ_number": 23,
                    "canonical_typ_name": "BANG-LANG",
                    "canonical_typ_name_ko": "방랑",
                },
            }

            changed_paths = vtg_auto.canonicalize_linked_td_outputs(
                output_root,
                td_typ_links=links,
                restrict_to_linked_rows=True,
                status=status,
                status_path=status_path,
            )

            metadata = status["cycles"]["202608281200"]["td_2026_42_240h"]["metadata"]
            self.assertIn(status_path, changed_paths)
            self.assertEqual("TYP", metadata["canonical_storm_stage"])
            self.assertEqual(23, metadata["canonical_typ_number"])
            self.assertEqual("BANG-LANG", metadata["canonical_typ_name"])
            self.assertEqual(23, metadata["linked_typ_number"])
            self.assertEqual(vtg_auto.relative_asset_path(target_image), metadata["image_path"])


if __name__ == "__main__":
    unittest.main()
