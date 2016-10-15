
import collections
from datetime import datetime, timedelta
import numpy as np
#import pytz

from ib.ext.Order import Order

from bot.ticks import BBOs, Trades

class Recoil2(object):

    def __init__(self, watch_threshold, watch_duration,
                 slowdown_threshold, slowdown_duration):

        # strategy
        self.watch_threshold = watch_threshold
        self.watch_dur = watch_duration
        self.slowdown_threshold = slowdown_threshold
        self.slowdown_dur = slowdown_duration

        # data
        self.bbos = collections.defaultdict(BBOs)
        self.trds = collections.defaultdict(Trades)

    def satisfy_conditions(self, watch_px, slowdown_px, px):

        watch_chng = (px - watch_px) / watch_px
        slowdown_chng = (px - slowdown_px) / slowdown_px

        # check if there was enough price movement
        if self.watch_threshold > 0 and watch_chng < self.watch_threshold:
            return None
        if self.watch_threshold < 0 and watch_chng > self.watch_threshold:
            return None

        # check if price movement slowed enough
        if not (abs(slowdown_chng) <= self.slowdown_threshold):
            return None

        direction = 'long' if watch_chng < 0 else 'short'
        return {'direction': direction, 'watch_px': watch_px,
                'watch_chng': watch_chng, 'slowdown_chng': slowdown_chng}

    def entry_signal(self, symbol, ts, px):

        # check if price is high enough
        if px < 1:
            return None

        bbos = self.bbos[symbol]
        trds = self.trds[symbol]

        # check if spread small enough
        if bbos.spread > px / 20:
            return None

        watch_dur_ago = ts - np.timedelta64(self.watch_dur, 's')
        slowdown_dur_ago = ts - np.timedelta64(self.slowdown_dur, 's')

        if self.watch_threshold < 0:
            watch_ts, watch_px = trds.maximum_since(watch_dur_ago)
        else:
            watch_ts, watch_px = trds.minimum_since(watch_dur_ago)

        slowdown_ts, slowdown_px = trds.asof(slowdown_dur_ago)

        if np.isnan(watch_px) or np.isnan(slowdown_px):
            # means there's no trades old enough to check condns
            return None

        if watch_ts > slowdown_ts:
            return None

        signal = self.satisfy_conditions(watch_px, slowdown_px, px)

        if signal:
            signal['watch_ts'] = watch_ts.to_datetime().isoformat()
            metadata = {'msg': 'signal triggered',
                        'ts': ts, 'symbol': symbol, 'current_px': px,
                        'slowdown_ts': slowdown_ts.to_datetime().isoformat(),
                        'slowdown_px': slowdown_px}
            return {**metadata, **signal}

    def handle_tick(self, tick):
        if tick['type'] == 'bbo':
            self.bbos[tick['symbol']].new_bbo(tick)
        elif tick['type'] == 'trd':
            self.trds[tick['symbol']].new_trd(tick)
            return self.entry_signal(tick['symbol'], tick['ts'], tick['px'])

    def place_order(self, signal):

        if signal['direction'] == 'short':
            return # don't short sell for now

        symbol = signal['symbol']
        current_bbo = self.bbos[symbol].current_bbo()
        order = Order()
        order.m_totalQuantity = 10
        order.m_orderType = 'LMT'
        order.m_tif = 'GTD'
        #expiry_time = datetime.now(pytz.timezone('America/New_York'))
        expiry_time = datetime.now()
        expiry_time += timedelta(seconds=5)
        order.m_goodTillDate = expiry_time.strftime('%Y%m%d %H:%M:%S')
        if signal['direction'] == 'long':
            order.m_lmtPrice = current_bbo['bid_px'] + 0.01
            order.m_action = 'BUY'
        else:
            order.m_lmtPrice = current_bbo['ask_px'] - 0.01
            order.m_action = 'SELL'
        return order

    def params(self):
        return {'strategy': 'recoil2',
                'watch_threshold': self.watch_threshold,
                'watch_duration': self.watch_dur,
                'slowdown_threshold': self.slowdown_threshold,
                'slowdown_duration': self.slowdown_dur}

