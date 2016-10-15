
import os
import io
import json
import argparse
import gzip
import numpy as np
import feather

#from bot.strategies.recoil import Recoil
from bot.strategies.recoil2 import Recoil2
from bot.utils import Logger

def peek(iterable):
    try:
        return next(iterable)[1]
    except StopIteration:
        return None

def backtest(strategies, bbos_df, trds_df):

    bbos = bbos_df.iterrows()
    trds = trds_df.iterrows()

    next_bbo = peek(bbos)
    next_trd = peek(trds)

    while not (next_bbo is None and next_trd is None):

        if next_bbo is None:
            next_tick = next_trd
            next_tick['type'] = 'trd'
            next_trd = peek(trds)
        elif next_trd is None:
            next_tick = next_bbo
            next_tick['type'] = 'bbo'
            next_bbo = peek(bbos)
        elif next_trd['ts'] < next_bbo['ts']:
            next_tick = next_trd
            next_tick['type'] = 'trd'
            next_trd = peek(trds)
        else:
            next_tick = next_bbo
            next_tick['type'] = 'bbo'
            next_bbo = peek(bbos)

        for strategy in strategies:
            signal = strategy.handle_tick(next_tick)
            if signal:
                yield signal

def gunzip(filepath):
    assert(filepath[-3:] == '.gz')
    with gzip.open(filepath, mode='rb') as in_fh:
        with open(filepath[:-3], mode='wb') as out_fh:
            out_fh.write(in_fh.read())
    return filepath[:-3]

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

    bbos_unzipped = gunzip(args.bbos)
    trds_unzipped = gunzip(args.trds)

    bbos_df = feather.read_dataframe(bbos_unzipped)
    trds_df = feather.read_dataframe(trds_unzipped)

    os.remove(bbos_unzipped)
    os.remove(trds_unzipped)

    for signal in backtest(strategies, bbos_df, trds_df):
        log.order(signal)

