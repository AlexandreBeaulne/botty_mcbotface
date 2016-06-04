
import sys
import json
import pandas as pd
from collections import defaultdict

class Instrument(object):

    def __init__(self):

        self.bbo = {'ts': None, 'symbol': None, 'bid_px': None, 'bid_sz': 0,
                    'ask_px': None, 'ask_sz': 0}
        self.trd_px = None
        self.bbos = []
        self.trds = []

    def add_tick(self, tick):

        msg = tick['msg']

        if msg['field'] == 0 and msg['type'] == 'tickSize': # bid sz
            if msg['size'] != self.bbo['bid_sz']:
                self.bbo['symbol'] = msg['symbol']
                self.bbo['ts'] = tick['ts']
                self.bbo['bid_sz'] = msg['size']
                if self.bbo['bid_px']:
                    self.bbos.append(self.bbo.copy())

        elif msg['field'] == 1 and msg['type'] == 'tickPrice': # bid px
            if msg['price'] != self.bbo['bid_px']:
                self.bbo['symbol'] = msg['symbol']
                self.bbo['ts'] = tick['ts']
                self.bbo['bid_px'] = msg['price']
                if self.bbo['bid_sz']:
                    self.bbos.append(self.bbo.copy())

        elif msg['field'] == 2 and msg['type'] == 'tickPrice': # ask px
            if msg['price'] != self.bbo['ask_px']:
                self.bbo['symbol'] = msg['symbol']
                self.bbo['ts'] = tick['ts']
                self.bbo['ask_px'] = msg['price']
                if self.bbo['ask_sz']:
                    self.bbos.append(self.bbo.copy())

        elif msg['field'] == 3 and msg['type'] == 'tickSize': # ask sz
            if msg['size'] != self.bbo['ask_sz']:
                self.bbo['symbol'] = msg['symbol']
                self.bbo['ts'] = tick['ts']
                self.bbo['ask_sz'] = msg['size']
                if self.bbo['ask_px']:
                    self.bbos.append(self.bbo.copy())

        elif msg['field'] == 4 and msg['type'] == 'tickPrice': # trd px
            self.trd_px = msg['price']

        elif msg['field'] == 5 and msg['type'] == 'tickSize': # trd sz
            if self.trd_px:
                self.trds.append({'ts': tick['ts'], 'symbol': msg['symbol'],
                                  'px': self.trd_px, 'sz': msg['size']})

if __name__ == '__main__':

    instruments = defaultdict(Instrument)

    for line in sys.stdin:
        log = json.loads(line)
        instruments[log['msg']['symbol']].add_tick(log)

    bbos = [bbo for inst in instruments.values() for bbo in inst.bbos]
    bbos = pd.DataFrame.from_dict(bbos)
    trds = [trd for inst in instruments.values() for trd in inst.trds]
    trds = pd.DataFrame.from_dict(trds)

    bbos_df = pd.read_csv('logs/bbos.csv.gz')
    trds_df = pd.read_csv('logs/trds.csv.gz')

    bbos_df = pd.concat([bbos_df, bbos]).sort_values('ts')
    trds_df = pd.concat([trds_df, trds]).sort_values('ts')

    cols = ['ts', 'symbol', 'bid_sz', 'bid_px', 'ask_px', 'ask_sz']
    bbos_df.to_csv('logs/bbos.csv.gz', compression='gzip',
                   index=False, columns=cols)

    cols = ['ts', 'symbol', 'px', 'sz']
    trds_df.to_csv('logs/trds.csv.gz', compression='gzip',
                   index=False, columns=cols)

