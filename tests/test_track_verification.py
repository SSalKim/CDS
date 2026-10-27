import unittest

from analysis.collect_track_verification import STORMS, cycles, parse_deck, parse_kma


class TrackVerificationTests(unittest.TestCase):
    def row(self, model="KIM_3h", cycle="202610150600", valid="202610160600", lead=24, number=30, lat=16):
        return f"1 2026 {number} 0 {lead} {cycle} {valid} {lat} 150 - -9 1000 15 -9 -9 -9 - -9 {model}"

    def test_exact_cycle_and_identity(self):
        text = "\n".join([self.row(), self.row(cycle="202610150000"), self.row(number=29), self.row(valid="202610160000")])
        rows, conflicts = parse_kma(text, "CHAMPI", "2026101506", [30])
        self.assertEqual(len(rows), 1)
        self.assertEqual(conflicts, 0)
        self.assertEqual(rows[0]["valid_time"], "2026101606")

    def test_native_alias_priority_and_confirmed_td(self):
        rows, _ = parse_kma("\n".join([self.row(model="KIM_6h", lat=17), self.row(), self.row(number=58)]), "CHAMPI", "2026101506", [30, 58])
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["raw_model"], "KIM_3h")
        self.assertEqual(rows[0]["storm_id"], 30)

    def test_conflicting_duplicates_excluded_not_averaged(self):
        rows, conflicts = parse_kma(self.row() + "\n" + self.row(lat=17), "CHAMPI", "2026101506", [30])
        self.assertEqual(rows, [])
        self.assertEqual(conflicts, 1)

    def test_csv_and_invalid_position(self):
        rows, _ = parse_kma(self.row().replace(" ", ",") + ",\n" + self.row(lat=99), "CHAMPI", "2026101506", [30])
        self.assertEqual(len(rows), 1)

    def test_atcf_signed_longitude_members_and_duplicates(self):
        line = "WP,29,2026101506,03,WMSH,24,160N,1790W,40,990"
        rows, _ = parse_deck(line + "\n" + line + "\n" + line.replace("WMSH", "W001"), "CHAMPI", "2026101506", "WMSH", "WP292026", "WINDBORNE")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["lon"], -179)

    def test_collection_excludes_unverifiable_last_day(self):
        self.assertEqual(list(cycles(STORMS["CHAMPI"]))[-1], "2026102418")
        self.assertEqual(list(cycles(STORMS["BAVI"]))[0], "2026070200")


if __name__ == "__main__":
    unittest.main()
