
"""
Handrolled data structures to store tick data.
Intuitively pandas Series or DataFrame would be used to store this data,
however they are ill-suited for dynamic "real-time" continuous appends.
"""

import numpy as np
import bisect

class BBOs(object):

    def __init__(self):
        self.num = 0
        preallocated_size = 10000000
        self.ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.bbos = []

    def new_bbo(self, bbo):
        self.ts[self.num] = bbo['ts']
        self.bbos.append(bbo)
        self.num += 1

    def get_current(self):
        if self.bbos:
            return self.bbos[-1]['bid_px'], self.bbos[-1]['ask_px']
        return np.nan, np.nan

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

