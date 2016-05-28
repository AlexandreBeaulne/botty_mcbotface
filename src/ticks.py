
"""
Handrolled data structures to store tick data.
Intuitively pandas DataFrame would be used to store this data,
however they are ill-suited for dynamic "real-time" continuous appends.
"""

import numpy as np
import bisect

PREALLOCATED_SIZE = 1000000

class Trades(object):

    def __init__(self):
        self.num_trades = 0
        self.ts = np.empty(PREALLOCATED_SIZE, dtype='datetime64[us]')
        self.px = np.empty(PREALLOCATED_SIZE, dtype='float32')
        self.sz = np.empty(PREALLOCATED_SIZE, dtype='float32')

    def append(self, ts, px, sz=np.nan):
        self.ts[self.num_trades] = ts
        self.px[self.num_trades] = px
        self.sz[self.num_trades] = sz
        self.num_trades += 1

    def asof(self, ts):
        i = bisect.bisect_left(self.ts[:self.num_trades], ts)
        if i:
            return self.ts[i], self.px[i], self.sz[i]
        return np.nan, np.nan, np.nan

