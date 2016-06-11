
"""
an exercise in overfitting
"""

import io
import gzip
import json
import argparse
import collections
from multiprocessing import Process, Queue, cpu_count
from itertools import product
import pandas as pd

from bot.strategy import Strategy
from bot.utils import Logger
from research.backtest import backtest, process_bbo, process_trd
from research.report import compute_outcomes

COLS = ['watch_threshold', 'watch_duration', 'slowdown_threshold',
        'slowdown_duration', 'direction', 'timeout', 'return']

# enumerate parameter spaces
watch_thrshlds = [0.02, 0.035, 0.05, 0.075, 0.1]
watch_drtns = [5, 10, 30, 60, 90, 120, 300]
slowdown_thrshlds = [0.001, 0.002, 0.005, 0.01, 0.02, 0.04]
slowdown_drtns = [1, 2, 5, 10, 20, 30, 60]
exit_timeouts = [1, 2, 5, 10, 20, 30, 40, 60, 90, 120, 180]

def backtester(queue, bbos_csv, trds_csv):

    with io.TextIOWrapper(gzip.open(bbos_csv, 'r')) as fh:
        fh.readline() # skip header
        bbos = collections.deque((process_bbo(line) for line in fh))

    with io.TextIOWrapper(gzip.open(trds_csv, 'r')) as fh:
        fh.readline() # skip header
        trds = collections.deque((process_trd(line) for line in fh))

    trds_df = pd.read_csv(trds_csv, parse_dates=['ts']).set_index('ts')

    while True:
        strategy = queue.get()
        if strategy:
            params = strategy.params()
            log.operation({'msg': 'backtest', 'params': params})
            signals = backtest(strategy, bbos.copy(), trds.copy())
            results = []
            for signal in signals:
                outcomes = compute_outcomes(signal, trds_df, exit_timeouts)
                results.extend([{**params, **outcome} for outcome in outcomes])
            if results:
                (pd.DataFrame.from_dict(results)
                   .to_csv('gridsearch.csv', index=False, mode='a', header=False))
        else:
            break

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='gridsearch')
    parser.add_argument('--bbos')
    parser.add_argument('--trds')
    args = parser.parse_args()

    log = Logger('gridsearch')
    log.operation('launching parameters grid search')

    queue = Queue()
    num_workers = cpu_count()
    worker = lambda: Process(target=backtester, args=(queue, args.bbos, args.trds))
    backtesters = [worker() for i in range(num_workers)]
    [backtester.start() for backtester in backtesters]

    # loop over all possibilities
    combos = product(watch_thrshlds, watch_drtns, slowdown_thrshlds, slowdown_drtns)
    for wt, wd, st, sd in combos:
        queue.put(Strategy(wt, wd, st, sd))

    [queue.put(None) for i in range(num_workers)]
    queue.close()
    [backtester.join() for backtester in backtesters]

