
import unittest
import numpy as np

from research.backtest import process_trd, process_bbo

class BotTest(unittest.TestCase):

    def test_process_trd(self):
        line = '2016-05-09T13:29:15.070003,ARIA,200.0,7.23'
        observed = process_trd(line)
        expected_ts = np.datetime64('2016-05-09T13:29:15.070003')
        expected = {'type': 'trd', 'ts': expected_ts, 'symbol': 'ARIA',
                    'px': 7.23, 'sz': 200}
        self.assertDictEqual(expected, observed)

    def test_process_bbo(self):
        line = '2016-05-09T13:29:14.815093,ARIA,5.0,7.1,7.24,14.0'
        observed = process_bbo(line)
        expected_ts = np.datetime64('2016-05-09T13:29:14.815093')
        expected = {'type': 'bbo', 'ts': expected_ts, 'symbol': 'ARIA',
                    'bid_sz': 5, 'bid_px': 7.1, 'ask_px': 7.24, 'ask_sz': 14}
        self.assertDictEqual(expected, observed)

if __name__ == '__main__':
    unittest.main()

