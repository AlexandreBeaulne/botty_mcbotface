
import os
import json
import argparse
import pandas as pd
import feather

#from bot.strategies.recoil import Recoil
from bot.strategies.recoil2 import Recoil2
from bot.utils import Logger, gunzip

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

    while next_bbo is not None or next_trd is not None:

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
    bbos_df['symbol'] = bbos_df['symbol'].astype('category')
    bbos_df['ts'] = pd.to_datetime(bbos_df['ts'])

    trds_df = feather.read_dataframe(trds_unzipped)
    trds_df['symbol'] = trds_df['symbol'].astype('category')
    trds_df['ts'] = pd.to_datetime(trds_df['ts'])

    os.remove(bbos_unzipped)
    os.remove(trds_unzipped)

    for signal in backtest(strategies, bbos_df, trds_df):
        log.order(signal)

