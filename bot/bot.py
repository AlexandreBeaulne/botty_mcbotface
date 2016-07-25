
"""
Trading bot
"""

import json
import argparse
import queue
import numpy as np

from ib.ext.Contract import Contract
from ib.ext.EClientSocket import EClientSocket

from bot.connector import Connector
from bot.bookbuilder import BookBuilder
from bot.utils import Logger
from bot.strategies.recoil2 import Recoil2

class Bot(object):

    def __init__(self, host, port, strategies, instruments, logger):

        self.msgs = queue.Queue()
        self.book_builder = BookBuilder()

        # strategies
        self.instruments = instruments
        self.contracts = dict()
        self.strategies = []
        for strategy in strategies:
            strat = Recoil2(strategy['watch_threshold'],
                            strategy['watch_duration'],
                            strategy['slowdown_threshold'],
                            strategy['slowdown_duration'])
            self.strategies.append(strat)

        # operations
        self.host = host
        self.port = port
        self.connection = EClientSocket(Connector(self.instruments, self.msgs))
        self.next_id = 1
        self.log = logger

    def connect(self):
        template = 'Attempting to connect host: {} port: {}...'
        self.log.operation(template.format(self.host, self.port))
        self.connection.eConnect(self.host, self.port, 0)
        self.log.operation('Connected.')

    def disconnect(self):
        self.log.operation('Disconnecting...')
        self.connection.eDisconnect()
        self.log.operation('Disconnected.')

    def request_data(self):
        for ticker_id, instrument in self.instruments.items():
            contract = Contract()
            contract.m_symbol = instrument['symbol']
            contract.m_currency = instrument['currency']
            contract.m_secType = instrument['secType']
            contract.m_exchange = instrument['exchange']
            self.contracts[instrument['symbol']] = contract
            self.connection.reqMktData(ticker_id, contract, '', False)

    def run(self):
        while True:
            msg = self.msgs.get()
            self.log.raw(msg)

            tick = self.book_builder.process_raw_tick(msg)

            if not tick:
                continue

            self.log.data(tick)

            for strategy in self.strategies:
                signal = strategy.handle_tick(tick)

                if not signal:
                    continue

                self.log.order(signal)
                order = strategy.place_order(signal)

                if not order:
                    continue

                c = self.contracts[signal['symbol']]
                self.log.order({'symbol': signal['symbol'],
                                'qty': order.m_totalQuantity,
                                'type': order.m_orderType,
                                'goodTill': order.m_goodTillDate,
                                'px': order.m_lmtPrice,
                                'action': order.m_action})
                self.connection.placeOrder(id=self.next_id, contract=c,
                                           order=order)
                self.next_id += 1

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='bot')
    parser.add_argument('--config', type=argparse.FileType('r'))
    args = parser.parse_args()

    config = json.load(args.config)
    config['instruments'] = {i:c for i, c in enumerate(config['instruments'])}
    log = Logger('log')
    log.operation({'config': config})

    config['logger'] = log
    bot = Bot(**config)
    bot.connect()
    bot.request_data()
    try:
        bot.run()
    except Exception as e:
        log.operation('encountered exception {}'.format(e))
    finally:
        bot.disconnect()

