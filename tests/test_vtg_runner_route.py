import unittest

from vtg_runner_route import HOSTED, select


def runners(*, busy=False, online=True, chart=False):
    return {"runners": [{"status": "online" if online else "offline", "busy": busy,
                         "labels": [{"name": "Linux"},
                                    {"name": "cds-public-charts" if chart else "cds-vtg"}]}]}


class RoutingTests(unittest.TestCase):
    def simulate(self, own, chart):
        elapsed = [0]
        sleeps = []

        def fetch(repo, timeout):
            self.assertGreater(timeout, 0)
            return (own if repo == "SSalKim/CDS" else chart)(elapsed[0])

        def sleep(seconds):
            elapsed[0] += seconds
            sleeps.append(seconds)

        result = select(fetch, clock=lambda: elapsed[0], sleep=sleep)
        return result, elapsed[0], sleeps

    def test_idle_laptop_is_used_immediately(self):
        result, elapsed, _ = self.simulate(lambda _: runners(), lambda _: runners(chart=True))
        self.assertEqual(result, ["self-hosted", "cds-vtg"])
        self.assertEqual(elapsed, 0)

    def test_chart_finishes_within_three_minutes_then_laptop_is_used(self):
        result, elapsed, _ = self.simulate(lambda _: runners(), lambda t: runners(busy=t < 60, chart=True))
        self.assertEqual(result, ["self-hosted", "cds-vtg"])
        self.assertEqual(elapsed, 60)

    def test_chart_stays_busy_then_github_after_exactly_three_minutes(self):
        result, elapsed, _ = self.simulate(lambda _: runners(), lambda _: runners(busy=True, chart=True))
        self.assertEqual(result, HOSTED)
        self.assertEqual(elapsed, 180)

    def test_vtg_busy_also_waits_before_hosted_fallback(self):
        result, elapsed, _ = self.simulate(lambda _: runners(busy=True), lambda _: runners(chart=True))
        self.assertEqual((result, elapsed), (HOSTED, 180))

    def test_offline_or_unreadable_status_falls_back_without_waiting(self):
        result, elapsed, _ = self.simulate(lambda _: runners(online=False), lambda _: runners(chart=True))
        self.assertEqual((result, elapsed), (HOSTED, 0))
        self.assertEqual(select(lambda *args: (_ for _ in ()).throw(ValueError("private data"))), HOSTED)


if __name__ == "__main__":
    unittest.main()
