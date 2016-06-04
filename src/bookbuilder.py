
from collections import defaultdict

class BookBuilder():

    def __init__(self):
        empty_bbo = lambda: {'type': 'bbo', 'ts': None, 'symbol': None,
                             'bid_px': None, 'bid_sz': 0, 'ask_px': None,
                             'ask_sz': 0}
        empty_trd = lambda: {'type': 'trd', 'symbol': None,
                             'ts': None, 'px': None, 'sz': 0}
        self.bbos = defaultdict(empty_bbo)
        self.trds = defaultdict(empty_trd)

    def process_raw_tick(self, tick):

        msg = tick['msg']
        bbo = self.bbos[msg['symbol']]
        trd = self.trds[msg['symbol']]

        if msg['field'] == 0 and msg['type'] == 'tickSize': # bid sz
            if msg['size'] != bbo['bid_sz']:
                bbo['symbol'] = msg['symbol']
                bbo['ts'] = tick['ts']
                bbo['bid_sz'] = msg['size']
                if bbo['bid_px']:
                    return bbo.copy()

        elif msg['field'] == 1 and msg['type'] == 'tickPrice': # bid px
            if msg['price'] != bbo['bid_px']:
                bbo['symbol'] = msg['symbol']
                bbo['ts'] = tick['ts']
                bbo['bid_px'] = msg['price']
                if bbo['bid_sz']:
                    return bbo.copy()

        elif msg['field'] == 2 and msg['type'] == 'tickPrice': # ask px
            if msg['price'] != bbo['ask_px']:
                bbo['symbol'] = msg['symbol']
                bbo['ts'] = tick['ts']
                bbo['ask_px'] = msg['price']
                if bbo['ask_sz']:
                    return bbo.copy()

        elif msg['field'] == 3 and msg['type'] == 'tickSize': # ask sz
            if msg['size'] != bbo['ask_sz']:
                bbo['symbol'] = msg['symbol']
                bbo['ts'] = tick['ts']
                bbo['ask_sz'] = msg['size']
                if bbo['ask_px']:
                    return bbo.copy()

        elif msg['field'] == 4 and msg['type'] == 'tickPrice': # trd px
            trd['symbol'] = msg['symbol']
            trd['ts'] = tick['ts']
            trd['px'] = msg['price']

        elif msg['field'] == 5 and msg['type'] == 'tickSize': # trd sz
            trd['symbol'] = msg['symbol']
            trd['ts'] = tick['ts']
            trd['sz'] = msg['size']
            if trd['px']:
                return trd.copy()

