
"""
Trading bot for recoil strat
"""

import json
import argparse
import queue
import numpy as np

from wrapper import Wrapper
from utils import Logger

from ib.ext.Contract import Contract
from ib.ext.EClientSocket import EClientSocket

from strategy import Strategy

class RecoilBot(object):

    def __init__(self, host, port, instruments, watch_threshold, watch_duration,
                 slowdown_threshold, slowdown_duration, logger, replay_file):

        self.msgs = queue.Queue()

        # strategy
        self.instruments = instruments
        self.strategy = Strategy(watch_threshold, watch_duration,
                slowdown_threshold, slowdown_duration)

        # operations
        self.host = host
        self.port = port
        if replay_file:
            self.replay_file = replay_file
        else:
            self.replay_file = None
            self.connection = EClientSocket(Wrapper(self.instruments, self.msgs))
        self.log = logger

    def connect(self):
        if self.replay_file:
            self.log.operation('Replaying {}...'.format(self.replay_file))
            with open(self.replay_file, 'r') as fh:
                for line in fh:
                    line = json.loads(line)
                    if line['type'] == 'DATA':
                        msg = line['msg']
                        msg['ts'] = np.datetime64(line['ts'])
                        self.msgs.put(msg)
        else:
            template = 'Attempting to connect host: {} port: {}...'
            self.log.operation(template.format(self.host, self.port))
            self.connection.eConnect(self.host, self.port, 0)
            self.log.operation('Connected.')

    def disconnect(self):
        if not self.replay_file:
            self.log.operation('Disconnecting...')
            self.connection.eDisconnect()
            self.log.operation('Disconnected.')

    def request_data(self):
        if not self.replay_file:
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
            if msg['type'] == 'tickPrice':
                self.log.data(msg)
                signal = self.strategy.handle_tick_price(msg)
            elif msg['type'] == 'tickSize':
                self.log.data(msg)
                signal = self.strategy.handle_tick_size(msg)
            else:
                self.log.misc(msg)

            if signal:
                self.log.order(signal)

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='recoil trading bot')
    parser.add_argument('--config', type=argparse.FileType('r'))
    parser.add_argument('--replay-file')
    args = parser.parse_args()

    config = json.load(args.config)
    config['instruments'] = {i:c for i, c in enumerate(config['instruments'])}
    config['replay_file'] = args.replay_file
    log = Logger('replay' if args.replay_file else 'log')
    log.operation({'config': config})

    config['logger'] = log
    bot = RecoilBot(**config)
    bot.connect()
    bot.request_data()
    try:
        bot.run()
    except Exception as e:
        log.operation('encountered exception {}'.format(e))
    finally:
        bot.disconnect()

