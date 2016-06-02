
"""
an exercise in overfitting
"""

import io
import gzip
import argparse
import collections
from itertools import product

import backtest
from strategy import Strategy
from utils import Logger

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

    # enumerate parameter spaces
    watch_thrshlds = [0.01, 0.02, 0.03, 0.04, 0.05, 0.075, 0.1]
    watch_drtns = [5, 10, 15, 30, 45, 60, 90, 120, 180, 300]
    slowdown_thrshlds = [0.001, 0.002, 0.003, 0.005, 0.0075, 0.01, 0.02, 0.04]
    slowdown_drtns = [1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 60]

    # loop over all possibilities
    combos = product(watch_thrshlds, watch_drtns, slowdown_thrshlds, slowdown_drtns)
    for wt, wd, st, sd in combos:
        strategy = Strategy(wt, wd, st, sd)
        log.operation({'type': 'backtest', 'params': strategy.params()})
        # signals = backtest.backtest(strategy, bbos.copy(), trds.copy())
        log.operation('done')

