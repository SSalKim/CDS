import unittest
from urllib.parse import parse_qs, urlsplit

import VTG


class KnackwxUrlTests(unittest.TestCase):
    def test_25w_18z_uses_history_text_endpoint(self):
        self.assertEqual(
            "https://api.knackwx.com/atcf/v2/aid/history/text?stormID=25W&cycle=late&initTime=18z",
            VTG.knackwx_url("wp252026", "202609261800"),
        )

    def test_storm_ids_and_initialization_hours_remain_dynamic(self):
        for atcf_id, storm_id in [
            ("wp902026", "90W"), ("al012026", "01L"),
            ("ep052026", "05E"), ("cp012026", "01C"),
            ("io012026", "01A"), ("sh012026", "01S"),
        ]:
            for hour in ("00", "06", "12", "18"):
                with self.subTest(atcf_id=atcf_id, hour=hour):
                    url = urlsplit(VTG.knackwx_url(atcf_id, f"20260926{hour}00"))
                    self.assertEqual("https", url.scheme)
                    self.assertEqual("api.knackwx.com", url.netloc)
                    self.assertEqual("/atcf/v2/aid/history/text", url.path)
                    self.assertEqual(
                        {"stormID": [storm_id], "cycle": ["late"], "initTime": [f"{hour}z"]},
                        parse_qs(url.query),
                    )

    def test_primary_and_extra_storms_all_use_new_endpoint(self):
        settings = VTG.Settings(
            atcf_id="wp252026", extra_atcf_ids=("wp902026", "wp252026"),
            data_time="202609261800",
        )
        urls = [url for source, url, _ in VTG.atcf_urls(settings) if source == "KNACKWX"]
        self.assertEqual(2, len(urls))
        self.assertEqual(["25W", "90W"], [parse_qs(urlsplit(url).query)["stormID"][0] for url in urls])
        for url in urls:
            self.assertEqual("/atcf/v2/aid/history/text", urlsplit(url).path)

    def test_invalid_storm_id_does_not_create_a_request(self):
        for atcf_id in ("", "wp", "wpXX2026", "xx252026"):
            with self.subTest(atcf_id=atcf_id):
                self.assertEqual("", VTG.knackwx_url(atcf_id, "202609261800"))


if __name__ == "__main__":
    unittest.main()
