
import sys
import json
import argparse
import numpy as np

from strategy import Strategy
from utils import Logger

def line2dict(line):
    ts, symbol, px, _sz = line.split(',')
    return {'type': 'tickPrice', 'symbol': symbol, 'field': 4,
            'price': float(px), 'ts': np.datetime64(ts)}

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='backtest')
    parser.add_argument('--config', type=argparse.FileType('r'))
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

    sys.stdin.readline() # skip header

    for line in sys.stdin:
        signal = strategy.handle_tick_price(line2dict(line))
        if signal:
            log.order(signal)

