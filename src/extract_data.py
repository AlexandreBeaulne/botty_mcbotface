
import sys
import json
import pandas as pd
from collections import defaultdict

def bbo(ts, symbol, bid, ask):
    return {'ts': ts, 'symbol': symbol, 'bid_px': bid['px'],
            'bid_sz': bid['sz'], 'ask_px': ask['px'], 'ask_sz': ask['sz']}

class Instrument(object):

    def __init__(self):

        self.bid = {'ts': None, 'px': None, 'sz': 0}
        self.ask = {'ts': None, 'px': None, 'sz': 0}
        self.trd = None
        self.bbos = []
        self.trds = []

    def add_tick(self, tick):

        msg = tick['msg']

        if msg['field'] == 0 and msg['type'] == 'tickSize': # bid sz
            if self.bid['sz'] == 0:
                self.bid['sz'] = msg['size']
            elif msg['size'] != self.bid['sz']:
                self.bbos.append(bbo(self.bid['ts'], msg['symbol'], 
                                     self.bid, self.ask))
                self.bid = {'ts': tick['ts'], 'px': self.bid['px'], 'sz': msg['size']}

        elif msg['field'] == 1 and msg['type'] == 'tickPrice': # bid px
            if not self.bid['px']:
                self.bid['ts'] = tick['ts']
                self.bid['px'] = msg['price']
            elif self.bid['px'] != msg['price']:
                if self.bid['ts'] and self.bid['px'] and self.bid['sz']:
                    self.bbos.append(bbo(self.bid['ts'], msg['symbol'], 
                                         self.bid, self.ask))
                self.bid = {'ts': tick['ts'], 'px': msg['price'], 'sz': 0}

        elif msg['field'] == 2 and msg['type'] == 'tickPrice': # ask px
            if not self.ask['px']:
                self.ask['ts'] = tick['ts']
                self.ask['px'] = msg['price']
            elif self.ask['px'] != msg['price']:
                if self.ask['ts'] and self.ask['px'] and self.ask['sz']:
                    self.bbos.append(bbo(self.ask['ts'], msg['symbol'],
                                         self.bid, self.ask))
                self.ask = {'ts': tick['ts'], 'px': msg['price'], 'sz': 0}

        elif msg['field'] == 3 and msg['type'] == 'tickSize': # ask sz
            if self.ask['sz'] == 0:
                self.ask['sz'] = msg['size']
            elif msg['size'] != self.ask['sz']:
                self.bbos.append(bbo(self.ask['ts'], msg['symbol'],
                                     self.bid, self.ask))
                self.ask = {'ts': tick['ts'], 'px': self.ask['px'], 'sz': msg['size']}

        elif msg['field'] == 4 and msg['type'] == 'tickPrice': # trd px
            self.trd = msg['price']

        elif msg['field'] == 5 and msg['type'] == 'tickSize': # trd sz
            if self.trd:
                self.trds.append({'ts': tick['ts'], 'symbol': msg['symbol'],
                                  'px': self.trd, 'sz': msg['size']})

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

