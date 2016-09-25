
import io
import json
import argparse
import gzip
import numpy as np

#from bot.strategies.recoil import Recoil
from bot.strategies.recoil2 import Recoil2
from bot.utils import Logger

def process_trd(line):
    ts, symbol, sz, px = line.split(',')
    return {'type': 'trd', 'ts': np.datetime64(ts), 'symbol': symbol,
            'px': float(px), 'sz': int(float(sz))}

def process_bbo(line):
    ts, symbol, bid_sz, bid_px, ask_px, ask_sz = line.split(',')
    bid_px = float(bid_px) if bid_px else np.nan
    ask_px = float(ask_px) if ask_px else np.nan
    return {'type': 'bbo', 'ts': np.datetime64(ts), 'symbol': symbol,
            'bid_sz': int(float(bid_sz)), 'bid_px': float(bid_px),
            'ask_px': float(ask_px), 'ask_sz': int(float(ask_sz))}

def my_pop_left(iterator):
    try:
        return next(iterator)
    except StopIteration:
        return {'ts': np.datetime64('3000-01-01T00:00:00.000000')}

def backtest(strategies, bbos, trds):

    next_bbo = None
    next_trd = None

    while bbos or trds:

        if not next_bbo:
            next_bbo = my_pop_left(bbos)

        if not next_trd:
            next_trd = my_pop_left(trds)

        if next_trd['ts'] < next_bbo['ts']:
            for strategy in strategies:
                signal = strategy.handle_tick(next_trd)
                if signal:
                    yield signal
            next_trd = None
        else:
            for strategy in strategies:
                signal = strategy.handle_tick(next_bbo)
                if signal:
                    yield signal
            next_bbo = None

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='backtest')
    parser.add_argument('--config', type=argparse.FileType('r'))
    parser.add_argument('--bbos')
    parser.add_argument('--trds')
    args = parser.parse_args()

    config = json.load(args.config)

    log = Logger('backtest')
    log.operation({'config': config})

    strategies = []
    for strategy in config['strategies']:
        watch_threshold = strategy['watch_threshold']
        watch_duration = strategy['watch_duration']
        slowdown_threshold = strategy['slowdown_threshold']
        slowdown_duration = strategy['slowdown_duration']
        strategies.append(Recoil2(watch_threshold, watch_duration,
                                  slowdown_threshold, slowdown_duration))

    fh_bbos = io.TextIOWrapper(gzip.open(args.bbos, 'r'))
    fh_bbos.readline() # skip header
    bbos = (process_bbo(line) for line in fh_bbos)

    fh_trds = io.TextIOWrapper(gzip.open(args.trds, 'r'))
    fh_trds.readline() # skip header
    trds = (process_trd(line) for line in fh_trds)

    for signal in backtest(strategies, bbos, trds):
        log.order(signal)

    fh_bbos.close()
    fh_trds.close()
