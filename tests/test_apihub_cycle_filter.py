import csv
import io
import unittest

import VTG


def kma_csv_text(rows: list[list[object]]) -> str:
    output = io.StringIO()
    output.write("header 1\nheader 2\n")
    writer = csv.writer(output, lineterminator="\n")
    writer.writerows(rows)
    return output.getvalue()


def kma_row(*, source: str, base_time: str, valid_time: str, lead_hour: int) -> list[object]:
    return [
        int(lead_hour > 0),
        2026,
        46,
        int(lead_hour > 0),
        lead_hour,
        base_time,
        valid_time,
        24.0,
        142.0,
        "",
        "",
        998,
        20,
        "",
        "",
        "",
        "",
        "",
        source,
        "",
    ]


class ApihubCycleFilterTests(unittest.TestCase):
    def settings(self) -> VTG.Settings:
        return VTG.Settings(
            typ_number=46,
            storm_stage="TD",
            storm_year="2026",
            data_time="202608301800",
            fcst_hours=240,
        )

    def test_forecast_rows_require_exact_source_cycle(self):
        text = kma_csv_text([
            kma_row(source="KMA", base_time="202608301800", valid_time="202608301800", lead_hour=0),
            kma_row(source="FNEC_AI", base_time="202608301200", valid_time="202608301800", lead_hour=6),
            kma_row(source="FNEC_AI", base_time="202608301800", valid_time="202608310000", lead_hour=6),
            kma_row(source="PGEC_AI", base_time="", valid_time="202608310000", lead_hour=6),
        ])

        frame = VTG.read_kma_csv(text, self.settings(), forecast_only=True)

        self.assertEqual(2, len(frame))
        self.assertEqual({"KMA", "FNEC_AI"}, set(frame["SRC"]))
        self.assertEqual(
            {"202608301800"},
            {VTG.normalize_utc_stamp(value) for value in frame["TYP_TM(UTC)"]},
        )

    def test_past_kma_rows_are_not_limited_to_requested_cycle(self):
        text = kma_csv_text([
            kma_row(source="KMA", base_time="202608301200", valid_time="202608301200", lead_hour=0),
            kma_row(source="KMA", base_time="202608301800", valid_time="202608301800", lead_hour=0),
        ])

        frame = VTG.read_kma_csv(text, self.settings(), forecast_only=False)

        self.assertEqual(2, len(frame))


if __name__ == "__main__":
    unittest.main()
