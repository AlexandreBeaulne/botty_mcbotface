
import unittest
import numpy as np

import backtest

def fun(x):
        return x + 1

class BotTest(unittest.TestCase):

    def test_process_trd(self):
        line = '2016-05-09T13:29:15.070003,ARIA,7.23,200.0'
        observed = backtest.process_trd(line)
        expected_ts = np.datetime64('2016-05-09T13:29:15.070003')
        expected = {'ts': expected_ts, 'symbol': 'ARIA', 'px': 7.23, 'sz': 200}
        self.assertDictEqual(expected, observed)

    def test_process_bbo(self):
        line = '2016-05-09T13:29:14.815093,ARIA,5.0,7.1,7.24,14.0'
        observed = backtest.process_bbo(line)
        expected_ts = np.datetime64('2016-05-09T13:29:14.815093')
        expected = {'ts': expected_ts, 'symbol': 'ARIA', 'bid_sz': 5,
                    'bid_px': 7.1, 'ask_px': 7.24, 'ask_sz': 14}
        self.assertDictEqual(expected, observed)

if __name__ == '__main__':
    unittest.main()

