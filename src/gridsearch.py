
"""
an exercise in overfitting
"""

import io
import gzip
import json
import random
import argparse
import collections
import pandas as pd
from itertools import product

import backtest
from strategy import Strategy
from utils import Logger
from report import compute_outcomes

COLS = ['watch_threshold', 'watch_duration', 'slowdown_threshold',
        'slowdown_duration', 'direction', 'timeout', 'return']

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='backtest')
    parser.add_argument('--bbos')
    parser.add_argument('--trds')
    args = parser.parse_args()

    log = Logger('gridsearch')
    log.operation('launching parameters grid search')

    with io.TextIOWrapper(gzip.open(args.bbos, 'r')) as fh:
        fh.readline() # skip header
        bbos = collections.deque((backtest.process_bbo(line) for line in fh))

    with io.TextIOWrapper(gzip.open(args.trds, 'r')) as fh:
        fh.readline() # skip header
        trds = collections.deque((backtest.process_trd(line) for line in fh))

    trds_df = pd.read_csv(args.trds, parse_dates=['ts']).set_index('ts')

    # enumerate parameter spaces
    watch_thrshlds = [0.02, 0.035, 0.05, 0.075, 0.1]
    watch_drtns = [5, 10, 30, 60, 90, 120, 300]
    slowdown_thrshlds = [0.001, 0.002, 0.005, 0.01, 0.02, 0.04]
    slowdown_drtns = [1, 2, 5, 10, 20, 30, 60]
    exit_timeouts = [1, 2, 5, 10, 20, 30, 40, 60, 90, 120, 180]

    # loop over all possibilities
    combos = product(watch_thrshlds, watch_drtns, slowdown_thrshlds, slowdown_drtns)
    for wt, wd, st, sd in random.shuffle(list(combos)):
        setup = {'type': 'backtest', 'watch_threshold': wt, 'watch_duration': wd,
                 'slowdown_threshold': st, 'slowdown_duration': sd}
        log.operation(setup)
        strategy = Strategy(wt, wd, st, sd)
        signals = backtest.backtest(strategy, bbos.copy(), trds.copy())
        outcomes = [compute_outcomes(s, trds_df, exit_timeouts) for s in signals]
        outcomes_df = (pd.DataFrame.from_dict([x for xs in outcomes for x in xs])
                                   .assign(watch_threshold=wt)
                                   .assign(watch_duration=wd)
                                   .assign(slowdown_threshold=st)
                                   .assign(slowdown_duration=sd))

        (outcomes_df.loc[:, COLS]
                    .to_csv('gridsearch.csv', index=False, mode='a', header=False))
        log.operation('done')

