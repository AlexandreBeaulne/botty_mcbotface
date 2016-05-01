
"""
Trading bot for recoil strat
"""

import json
import argparse
import time
import queue
import collections
import numpy as np
import pandas as pd
from datetime import datetime

from wrapper import Wrapper
from utils import log, now

from ib.ext.Contract import Contract
from ib.ext.EClientSocket import EClientSocket

class RecoilBot(object):

    def __init__(self, host, port, instruments, watch_threshold, watch_duration,
                 slowdown_threshold, slowdown_duration):

        # strategy
        self.instruments = instruments
        self.watch_threshold = watch_threshold
        self.watch_dur = watch_duration
        self.slowdown_threshold = slowdown_threshold
        self.slowdown_dur = slowdown_duration

        # data
        self.msgs = queue.Queue()
        self.bbos = collections.defaultdict(dict)
        ## create trades df with a dummy row for types
        self.trades = pd.DataFrame({'tickerId': -1, 'px': 0.0}, index=[now()])

        # settings
        self.host = host
        self.port = port
        self.wrapper = Wrapper(self.msgs)
        self.connection = EClientSocket(self.wrapper)

    def connect(self):
        log.info('Attempting to connect host: {} port: {}...'.format(self.host, self.port))
        self.connection.eConnect(self.host, self.port, 0)
        log.info('Connected.')

    def disconnect(self):
        log.info('Disconnecting...')
        self.connection.eDisconnect()
        log.info('Disconnected.')

    def request_data(self):
        for ticker_id, instrument in self.instruments.items():
            contract = Contract()
            contract.m_symbol = instrument['symbol']
            contract.m_currency = instrument['currency']
            contract.m_secType = instrument['secType']
            contract.m_exchange = instrument['exchange']
            self.connection.reqMktData(ticker_id, contract, '', False)

    def check_for_triggered_signal(self, ticker_id, cur_px):

        inst_trades = self.trades[self.trades['tickerId'] == ticker_id]

        watch_dur_ago = now() - np.timedelta64(self.watch_dur, 's')
        latest_ts_asof_watch_dur = inst_trades.index.asof(watch_dur_ago)
        px_watch_dur_ago = inst_trades.loc[latest_ts_asof_watch_dur]['px']
        chng_since_watch_dur = px - px_watch_dur_ago / px_watch_dur_ago

        slowdown_dur_ago = now() - np.timedelta64(self.slowdown_dur, 's')
        latest_ts_asof_slowdown_dur = inst_trades.index.asof(slowdown_dur_ago)
        px_slowdown_dur_ago = inst_trades.loc[latest_ts_asof_slowdown_dur]['px']
        chng_since_slowdown_dur = px - px_slowdown_dur_ago / px_slowdown_dur_ago

        # check if signal is triggered
        if abs(chng_since_watch_dur) >= self.watch_threshold and \
           abs(chng_since_slowdown_dur) <= self.slowdown_threshold:
               log.info({'msg': 'signal triggered',
                         'tickerId': ticker_id,
                         'currentPx': cur_px,
                         'px_slowdown_duration_ago': px_slowdown_dur_ago,
                         'px_watch_duration_ago': px_watch_dur_ago})

    def handle_trade(self, msg):

        # first append trade to trades table
        data = {key: msg[key] for key in ['tickerId', 'price']}
        self.trades = self.trades.append(pd.DataFrame(data, index=[now()]))

        # second check if any signal is triggered
        self.check_for_triggered_signal(msg['tickerId'], msg['price'])

        # finally remove old trades from table
        cutoff = now() - np.timedelta64(self.watch_duration, 's')
        self.trades = self.trades[self.trades.index >= cutoff]

    def handle_tick_price(self, msg):
        """
        field semantics: 1 = bid, 2 = ask, 4 = last,
                         6 = high, 7 = low, 9 = close
        """
        if msg['field'] == 1:
            self.bbos[msg['tickerId']]['bid'] = msg['price']
        elif msg['field'] == 2:
            self.bbos[msg['tickerId']]['ask'] = msg['price']
        elif msg['field'] == 4:
            self.handle_trade(msg)

    def handle_tick_size(self, msg):
        pass

    def run(self):
        while True:
            msg = self.msgs.get()
            log.info(msg)
            if msg['type'] == 'tickPrice':
                self.handle_tick_price(msg)
            elif msg['type'] == 'tickSize':
                self.handle_tick_size(msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="recoil trading bot")
    config_file = parser.add_argument('--config', type=argparse.FileType('r'))
    args = parser.parse_args()

    config = json.load(args.config)
    config['instruments'] = {i:c for i, c in enumerate(config['instruments'])}

    bot = RecoilBot(**config)
    bot.connect()
    bot.request_data()
    try:
        bot.run()
    except Exception as e:
        log.error('encountered exception {}'.format(e))
    finally:
        bot.disconnect()

