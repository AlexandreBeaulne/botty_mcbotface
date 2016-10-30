
"""
Handrolled data structures to store tick data.
Intuitively pandas Series or DataFrame would be used to store this data,
however they are ill-suited for dynamic "real-time" continuous appends.
"""

import numpy as np
import statistics
import bisect

class BBOs(object):

    def __init__(self):
        self.num = 0
        preallocated_size = 1000000
        self.ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.bbos = []

    def new_bbo(self, bbo):
        self.ts[self.num] = bbo['ts']
        self.bbos.append(bbo)
        self.num += 1

    def current_bbo(self):
        return self.bbos[-1]

    def spread(self):
        if self.num:
            bbo = self.current_bbo()
            if bbo['ask_px'] and bbo['bid_px']:
                return bbo['ask_px'] - bbo['bid_px']
        return 1000000 # arbitrary large spread

class Trades(object):

    def __init__(self):
        self.num = 0
        preallocated_size = 200000
        self.ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.trds = []

    def new_trd(self, trd):
        self.ts[self.num] = trd['ts']
        self.trds.append(trd)
        self.num += 1

    def asof(self, ts):
        i = bisect.bisect_left(self.ts[:self.num], ts)
        if i:
            return self.trds[i]['ts'], self.trds[i]['px']
        return np.nan, np.nan

    def maximum_since(self, ts):
        i = bisect.bisect_left(self.ts[:self.num], ts)
        if i:
            prices = [(trd['px'], trd['ts']) for trd in self.trds[i:]]
            max_px, max_ts = max(prices)
            return (max_ts, max_px)
        return (np.nan, np.nan)

    def minimum_since(self, ts):
        i = bisect.bisect_left(self.ts[:self.num], ts)
        if i:
            prices = [(trd['px'], trd['ts']) for trd in self.trds[i:]]
            min_px, min_ts = min(prices)
            return (min_ts, min_px)
        return (np.nan, np.nan)
