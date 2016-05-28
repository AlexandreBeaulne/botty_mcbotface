
import unittest
import numpy as np

import backtest

def fun(x):
        return x + 1

class BotTest(unittest.TestCase):

    def test_line2dict(self):
        line = '2016-05-09T13:29:15.070003,ARIA,7.23,200.0'
        observed = backtest.line2dict(line)
        expected_ts = np.datetime64('2016-05-09T13:29:15.070003')
        expected = {'type': 'tickPrice', 'symbol': 'ARIA', 'field': 4,
                    'price': 7.23, 'ts': expected_ts}
        self.assertDictEqual(expected, observed)

if __name__ == '__main__':
    unittest.main()

