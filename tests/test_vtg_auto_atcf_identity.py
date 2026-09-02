import unittest
from unittest.mock import patch

import vtg_auto


class AtcfIdentityTests(unittest.TestCase):
    def status(self):
        return {
            "cycles": {
                "202609010600": {
                    "typ_2026_18_120h": {"atcf_id": "wp172026"},
                },
                "202609011200": {
                    "typ_2026_18_120h": {"atcf_id": "wp962026"},
                },
            },
        }

    def test_previous_status_can_skip_newer_invest_id(self):
        match = vtg_auto.previous_atcf_match_from_status(
            self.status(),
            storm_keys=["typ_2026_18"],
            data_time="202609011200",
            regular_only=True,
        )

        self.assertIsNotNone(match)
        self.assertEqual("wp172026", match.atcf_id)

    @patch.object(vtg_auto, "fetch_bdeck_text", return_value="WP, 17, SAUDEL")
    def test_named_regular_id_replaces_nearby_invest(self, fetch_bdeck_text):
        current = vtg_auto.AtcfMatch(
            atcf_id="wp962026",
            method="sector_position",
            distance_km=12.0,
        )

        match = vtg_auto.retain_previous_named_regular_atcf_match(
            current,
            self.status(),
            storm_keys=["typ_2026_18"],
            data_time="202609011200",
            typ_en="SAUDEL",
        )

        self.assertEqual("wp172026", match.atcf_id)
        self.assertEqual("previous_regular_name", match.method)
        fetch_bdeck_text.assert_called_once_with("wp172026", timeout=15)

    @patch.object(vtg_auto, "fetch_bdeck_text", return_value="WP, 17, ANOTHER-STORM")
    def test_regular_id_is_not_retained_when_bdeck_name_differs(self, _fetch_bdeck_text):
        current = vtg_auto.AtcfMatch(atcf_id="wp962026", method="sector_position")

        match = vtg_auto.retain_previous_named_regular_atcf_match(
            current,
            self.status(),
            storm_keys=["typ_2026_18"],
            data_time="202609011200",
            typ_en="SAUDEL",
        )

        self.assertIs(current, match)


if __name__ == "__main__":
    unittest.main()
