
"""
Handrolled data structures to store tick data.
Intuitively pandas Series or DataFrame would be used to store this data,
however they are ill-suited for dynamic "real-time" continuous appends.
"""

import numpy as np
import bisect

class BBOs(object):

    def __init__(self):
        self.num_bids = 0
        self.num_asks = 0
        preallocated_size = 10000000
        self.bid_ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.bid_px = np.empty(preallocated_size, dtype='float32')
        self.ask_ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.ask_px = np.empty(preallocated_size, dtype='float32')

    def new_bid_px(self, ts, px):
        self.bid_ts[self.num_bids] = ts
        self.bid_px[self.num_bids] = px
        self.num_bids += 1

    def new_ask_px(self, ts, px):
        self.ask_ts[self.num_asks] = ts
        self.ask_px[self.num_asks] = px
        self.num_asks += 1

    def get_current(self):
        return self.bid_px[self.num_bids-1], self.ask_px[self.num_asks-1]

class Trades(object):

    def __init__(self):
        self.num_trades = 0
        preallocated_size = 1000000
        self.ts = np.empty(preallocated_size, dtype='datetime64[us]')
        self.px = np.empty(preallocated_size, dtype='float32')

    def new_trd_px(self, ts, px):
        self.ts[self.num_trades] = ts
        self.px[self.num_trades] = px
        self.num_trades += 1

    def asof(self, ts):
        i = bisect.bisect_left(self.ts[:self.num_trades], ts)
        if i:
            return self.ts[i], self.px[i]
        return np.nan, np.nan

