
import io
import json
import argparse
import gzip
import collections
import numpy as np

from strategy import Strategy
from utils import Logger

def process_trd(line):
    ts, symbol, px, sz = line.split(',')
    return {'ts': np.datetime64(ts), 'symbol': symbol,
            'px': float(px), 'sz': int(float(sz))}

def repackage_trd(trd):
    return {'type': 'tickPrice', 'symbol': trd['symbol'], 'field': 4,
            'price': trd['px'], 'ts': trd['ts']}

def process_bbo(line):
    ts, symbol, bid_sz, bid_px, ask_px, ask_sz = line.split(',')
    return {'ts': np.datetime64(ts), 'symbol': symbol,
            'bid_sz': int(float(bid_sz)), 'bid_px': float(bid_px),
            'ask_px': float(ask_px), 'ask_sz': int(float(ask_sz))}

def repackage_bid(bbo):
    return {'type': 'tickPrice', 'symbol': bbo['symbol'], 'field': 1,
            'price': bbo['bid_px'], 'ts': bbo['ts']}

def repackage_ask(bbo):
    return {'type': 'tickPrice', 'symbol': bbo['symbol'], 'field': 2,
            'price': bbo['ask_px'], 'ts': bbo['ts']}

def backtest(strategy, bbos, trds):

    current_trd = {'px': np.nan}
    current_bbo = {'bid_px': np.nan, 'ask_px': np.nan}

    end_of_time = np.datetime64('3000-01-01T00:00:00.000000')

    while bbos or trds:

        next_bbo = bbos[0] if bbos else {'ts': end_of_time}
        next_trd = trds[0] if trds else {'ts': end_of_time}

        if next_trd['ts'] < next_bbo['ts']:
            if next_trd['px'] != current_trd['px']:
                signal = strategy.handle_tick_price(repackage_trd(next_trd))
                if signal:
                    yield signal
            current_trd = trds.popleft()
        else:
            if next_bbo['bid_px'] != current_bbo['bid_px']:
                signal = strategy.handle_tick_price(repackage_bid(next_bbo))
                if signal:
                    log.order(signal)
            if next_bbo['ask_px'] != current_bbo['ask_px']:
                signal = strategy.handle_tick_price(repackage_ask(next_bbo))
                if signal:
                    yield signal
            current_bbo = bbos.popleft()

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='backtest')
    parser.add_argument('--config', type=argparse.FileType('r'))
    parser.add_argument('--bbos')
    parser.add_argument('--trds')
    args = parser.parse_args()

    config = json.load(args.config)

    log = Logger('backtest')
    log.operation({'config': config})

    watch_threshold = config['watch_threshold']
    watch_duration = config['watch_duration']
    slowdown_threshold = config['slowdown_threshold']
    slowdown_duration = config['slowdown_duration']

    strategy = Strategy(watch_threshold, watch_duration,
                        slowdown_threshold, slowdown_duration)

    with io.TextIOWrapper(gzip.open(args.bbos, 'r')) as fh:
        fh.readline() # skip header
        bbos = collections.deque((process_bbo(line) for line in fh))

    with io.TextIOWrapper(gzip.open(args.trds, 'r')) as fh:
        fh.readline() # skip header
        trds = collections.deque((process_trd(line) for line in fh))

    for signal in backtest(strategy, bbos, trds):
        log.order(signal)

