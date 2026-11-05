import unittest
from analysis.collect_infa_verification import parse_polar, parse_smca, kma_models
from analysis.collect_track_verification import STORMS, cycles, parse_kma


class InfaVerificationTests(unittest.TestCase):
    def test_observation_cutoff(self):
        c = list(cycles(STORMS['IN-FA']))
        self.assertEqual(c[0], '2026102318')
        self.assertEqual(c[-1], '2026110400')
        self.assertEqual(len(c), 46)

    def test_polar_identity_valid_time_and_signed_longitude(self):
        p = {'atcf_id': 'wp302026', 'cycle': '2026102318', 'models': {'icon': {
            'fhr': [24, 48], 'lat': [20, 21], 'lon': [181, 140], 'time': ['2026102418', '2026102512']}}}
        rows = parse_polar(p, 'test')
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]['lon'], -179)
        p['atcf_id'] = 'wp292026'
        self.assertEqual(parse_polar(p, 'test'), [])

    def test_smca_exact_forecast_cycle_not_analysis_time(self):
        p = {'code': 200, 'data': {'ident': '202631', 'points': [{'forecast': [{
            'sets': 'GEML', 'init_time_utc': '2026-10-24T00:00:00',
            'points': [{'forecastTime': 24, 'lat': 20, 'lng': 140}]}]}]}}
        self.assertEqual(parse_smca(p, 'test')[0]['valid_time'], '2026102500')
        p['data']['ident'] = '202630'
        self.assertEqual(parse_smca(p, 'test'), [])

    def test_kim_aliases_and_exact_id(self):
        line = '1 2026 31 0 24 202610231800 202610241800 20 140 - -9 990 30 -9 -9 -9 - -9 KIM_6h'
        rows, _ = parse_kma(line, 'IN-FA', '2026102318', [31], models=kma_models())
        self.assertEqual(rows[0]['model'], 'KIM')


if __name__ == '__main__':
    unittest.main()
