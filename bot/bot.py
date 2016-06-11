
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
from bot.strategy import Strategy

class Bot(object):

    def __init__(self, host, port, instruments, watch_threshold, watch_duration,
                 slowdown_threshold, slowdown_duration, logger):

        self.msgs = queue.Queue()
        self.book_builder = BookBuilder()

        # strategy
        self.instruments = instruments
        self.strategy = Strategy(watch_threshold, watch_duration,
                                 slowdown_threshold, slowdown_duration)

        # operations
        self.host = host
        self.port = port
        self.connection = EClientSocket(Connector(self.instruments, self.msgs))
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
            self.connection.reqMktData(ticker_id, contract, '', False)

    def run(self):
        while True:
            msg = self.msgs.get()
            self.log.raw(msg)

            tick = self.book_builder.process_raw_tick(msg)
            if tick:
                self.log.data(tick)
                signal = self.strategy.handle_tick(msg)

                if signal:
                    self.log.order(signal)

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

