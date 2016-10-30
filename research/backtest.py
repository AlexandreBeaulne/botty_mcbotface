
import os
import json
import argparse
import pandas as pd
import feather

#from bot.strategies.recoil import Recoil
from bot.strategies.recoil2 import Recoil2
from bot.utils import Logger, gunzip

def zip(bbos, trds):
    ticks = []
    while bbos or trds:
        if not bbos:
            ticks.append(trds.pop())
        elif not trds:
            ticks.append(bbos.pop())
        elif bbos[-1]['ts'] > trds[-1]['ts']:
            ticks.append(bbos.pop())
        else:
            ticks.append(trds.pop())
    return reversed(ticks)

def backtest(strategies, ticks):
    for tick in ticks:
        for strategy in strategies:
            signal = strategy.handle_tick(tick)
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
    bbos_df['type'] = 'bbo'

    trds_df = feather.read_dataframe(trds_unzipped)
    trds_df['symbol'] = trds_df['symbol'].astype('category')
    trds_df['ts'] = pd.to_datetime(trds_df['ts'])
    trds_df['type'] = 'trd'

    os.remove(bbos_unzipped)
    os.remove(trds_unzipped)

    ticks = zip(bbos_df.to_dict(orient='records'),
                trds_df.to_dict(orient='records'))

    for signal in backtest(strategies, ticks):
        log.order(signal)

