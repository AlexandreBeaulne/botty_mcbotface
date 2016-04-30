
"""
Trading bot for recoil strat
"""

import json
import argparse
import time
import queue

from wrapper import Wrapper
from utils import log

from ib.ext.Contract import Contract
from ib.ext.EClientSocket import EClientSocket

class RecoilBot(object):

    def __init__(self, host, port, instruments, watch_threshold, watch_duration,
                 slowdown_threshold, slowdown_duration):
        self.host = host
        self.port = port
        self.instruments = instruments
        self.watch_threshold = watch_threshold
        self.watch_duration = watch_duration
        self.slowdown_threshold = slowdown_threshold
        self.slowdown_duration = slowdown_duration
        self.msgs = queue.Queue()
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
        contract = Contract()
        contract.m_symbol = 'AUD'
        contract.m_currency = 'USD'
        contract.m_secType = 'CASH'
        contract.m_exchange = 'IDEALPRO'
        self.connection.reqMktData(1, contract, '', False)

    def run(self):
        while True:
            msg = self.msgs.get()
            log.info(msg)

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

