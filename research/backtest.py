
import io
import json
import argparse
import gzip
import collections
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

def backtest(strategies, bbos, trds):

    end_of_time = np.datetime64('3000-01-01T00:00:00.000000')

    while bbos or trds:

        next_bbo = bbos[0] if bbos else {'ts': end_of_time}
        next_trd = trds[0] if trds else {'ts': end_of_time}

        if next_trd['ts'] < next_bbo['ts']:
            for strategy in strategies:
                signal = strategy.handle_tick(next_trd)
                if signal:
                    yield signal
            trds.popleft()
        else:
            for strategy in strategies:
                signal = strategy.handle_tick(next_bbo)
                if signal:
                    yield signal
            bbos.popleft()

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

    with io.TextIOWrapper(gzip.open(args.bbos, 'r')) as fh:
        fh.readline() # skip header
        bbos = collections.deque((process_bbo(line) for line in fh))

    with io.TextIOWrapper(gzip.open(args.trds, 'r')) as fh:
        fh.readline() # skip header
        trds = collections.deque((process_trd(line) for line in fh))

    for signal in backtest(strategies, bbos, trds):
        log.order(signal)

