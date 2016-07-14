
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
        preallocated_size = 10000000
        self.ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.bbos = []
        self.spread = 0

    def new_bbo(self, bbo, factor=0.2):
        self.ts[self.num] = bbo['ts']
        self.bbos.append(bbo)
        self.num += 1
        if bbo['ask_px'] and bbo['bid_px']:
            spread = bbo['ask_px'] - bbo['bid_px']
            self.spread = (1 - factor) * self.spread + factor * spread

    def current_bbo(self):
        return self.bbos[-1]

class Trades(object):

    def __init__(self):
        self.num = 0
        preallocated_size = 1000000
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

    def maximums_since(self, ts):
        i = bisect.bisect_left(self.ts[:self.num], ts)
        if i:
            prices = [(trd['px'], trd['ts']) for trd in self.trds[i:]]
            min_px, min_ts = min(prices)
            max_px, max_ts = max(prices)
            return (min_ts, min_px), (max_ts, max_px)
        return (np.nan, np.nan), (np.nan, np.nan)

