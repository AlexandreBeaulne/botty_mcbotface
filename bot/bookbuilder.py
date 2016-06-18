
"""
receive raw, single-sided market data and return a bbo or trade from it
"""

from collections import defaultdict

class BookBuilder(): # pylint: disable=too-few-public-methods
    """
    receive raw, single-sided market data and return a bbo or trade from it
    """

    def __init__(self):
        empty_bbo = lambda: {'type': 'bbo', 'ts': None, 'symbol': None,
                             'bid_px': None, 'bid_sz': 0, 'ask_px': None,
                             'ask_sz': 0}
        empty_trd = lambda: {'type': 'trd', 'symbol': None,
                             'ts': None, 'px': None, 'sz': 0}
        self.bbos = defaultdict(empty_bbo)
        self.trds = defaultdict(empty_trd)

    def __handle_bbo_size__(self, msg, side):
        bbo = self.bbos[msg['symbol']]
        if msg['size'] != bbo[side]:
            bbo['symbol'] = msg['symbol']
            bbo['ts'] = msg['ts']
            bbo[side] = msg['size']
            return {**{'symbol': msg['symbol']}, **bbo}

    def __handle_bbo_px__(self, msg, side):
        bbo = self.bbos[msg['symbol']]
        if msg['price'] != bbo[side]:
            bbo['symbol'] = msg['symbol']
            bbo['ts'] = msg['ts']
            bbo[side] = msg['price']
            return {**{'symbol': msg['symbol']}, **bbo}

    def process_raw_tick(self, msg):
        """
        receive raw, single-sided market data and return a bbo or trade from it
        """

        if 'symbol' not in msg or 'field' not in msg:
            return None

        if msg['field'] in {0, 3} and msg['type'] == 'tickSize':
            side = {0: 'bid_sz', 3: 'ask_sz'}[msg['field']]
            return self.__handle_bbo_size__(msg, side)
        elif msg['field'] in {1, 2}  and msg['type'] == 'tickPrice':
            side = {1: 'bid_px', 2: 'ask_px'}[msg['field']]
            return self.__handle_bbo_px__(msg, side)
        elif msg['field'] == 4 and msg['type'] == 'tickPrice': # trd px
            trd = self.trds[msg['symbol']]
            trd['symbol'] = msg['symbol']
            trd['ts'] = msg['ts']
            trd['px'] = msg['price']
        elif msg['field'] == 5 and msg['type'] == 'tickSize': # trd sz
            trd = self.trds[msg['symbol']]
            trd['symbol'] = msg['symbol']
            trd['ts'] = msg['ts']
            trd['sz'] = msg['size']
            if trd['px']:
                return {**{'symbol': msg['symbol']}, **trd}

