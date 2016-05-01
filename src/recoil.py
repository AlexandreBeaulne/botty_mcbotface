
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

        # settings
        self.host = host
        self.port = port
        self.wrapper = Wrapper(self.msgs)
        self.connection = EClientSocket(self.wrapper)

        # strategy
        self.instruments = instruments
        self.watch_threshold = watch_threshold
        self.watch_duration = watch_duration
        self.slowdown_threshold = slowdown_threshold
        self.slowdown_duration = slowdown_duration

        # data
        self.msgs = queue.Queue()
        self.bbos = collections.defaultdict(dict)
        ## create trades df with a dummy row for types
        self.trades = pd.DataFrame({'tickerId': -1, 'price': 0.0}, index=[now()])

    def connect(self):
        log.info('Attempting to connect host: {} port: {}...'.format(self.host, self.port))
        self.connection.eConnect(self.host, self.port, 0)
        log.info('Connected.')

    def disconnect(self):
        log.info('Disconnecting...')
        self.connection.eDisconnect()
        log.info('Disconnected.')

    def request_data(self):
        contract = Contract()
        contract.m_symbol = 'AUD'
        contract.m_currency = 'USD'
        contract.m_secType = 'CASH'
        contract.m_exchange = 'IDEALPRO'
        self.connection.reqMktData(1, contract, '', False)

    def check_for_triggered_signal(ticker_id):
        pass

    def handle_trade(msg):

        # first append trade to trades table
        data = {key: msg[key] for key in ['tickerId', 'price']}
        self.trades = self.trades.append(pd.DataFrame(data, index=[now()]))

        # second check if any signal is triggered
        self.check_for_triggered_signal(msg['tickerId'])

        # finally remove old trades from table
        cutoff = now() - np.timedelta(self.watch_duration, 's')
        self.trades = self.trades[self.trades.index >= cutoff]

    def handle_tick_price(msg):
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

    def handle_tick_size(msg):
        pass

    def run(self):
        while True:
            msg = self.msgs.get()
            log.error(msg)
            if msg['type'] == 'tickPrice':
                self.handle_tick_price(msg)
            elif msg['type'] == 'tickSize':
                self.handle_tick_size(msg)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="recoil trading bot")
    config_file = parser.add_argument('--config', type=argparse.FileType('r'))
    args = parser.parse_args()

    config = json.load(args.config)

    bot = RecoilBot(**config)
    bot.connect()
    bot.request_data()
    try:
        bot.run()
    except:
        bot.disconnect()

