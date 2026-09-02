import unittest

from VTG import discard_post_upgrade_invest_points


class TrackHistoryIdentityTests(unittest.TestCase):
    def test_discards_invest_point_after_regular_id_is_established(self) -> None:
        points = [
            {"time_utc": "202608170000", "lat": 8.0, "lon": 156.0, "atcf_id": "wp962026"},
            {"time_utc": "202608180000", "lat": 8.1, "lon": 155.5, "atcf_id": "wp172026"},
            {"time_utc": "202608311200", "lat": 22.8, "lon": 116.9, "atcf_id": "wp962026"},
            {"time_utc": "202609010000", "lat": 19.3, "lon": 113.1, "source": "KMA_OFFICIAL"},
        ]

        filtered = discard_post_upgrade_invest_points(points, "wp172026")

        self.assertEqual(
            [point["time_utc"] for point in filtered],
            ["202608170000", "202608180000", "202609010000"],
        )

    def test_keeps_invest_points_while_current_system_is_an_invest(self) -> None:
        points = [
            {"time_utc": "202608170000", "lat": 8.0, "lon": 156.0, "atcf_id": "wp962026"},
            {"time_utc": "202608171200", "lat": 8.1, "lon": 155.5, "atcf_id": "wp972026"},
        ]

        self.assertEqual(discard_post_upgrade_invest_points(points, "wp962026"), points)


if __name__ == "__main__":
    unittest.main()
