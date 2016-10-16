
"""
an exercise in overfitting
"""

import re
import glob
import argparse
from multiprocessing import Process, Queue, cpu_count
from itertools import product
import pandas as pd
import feather

#from bot.strategies.recoil import Recoil
from bot.strategies.recoil2 import Recoil2
from bot.utils import Logger
from research.backtest import backtest
from research.report import compute_outcomes

COLS = ['watch_threshold', 'watch_duration', 'slowdown_threshold',
        'slowdown_duration', 'direction', 'timeout', 'return']

# enumerate parameter spaces
watch_thrshlds = [0.035, 0.05, 0.075, 0.1]
watch_drtns = [5, 10, 30, 60, 90, 120, 180]
slowdown_thrshlds = [0.001, 0.002, 0.005, 0.01, 0.02, 0.04]
slowdown_drtns = [2, 5, 10, 20, 30]
exit_timeouts = [2, 5, 10, 20, 30, 40, 60, 90, 120]

def backtester(queue):

    while True:
        next_params_set = queue.get()
        if next_params_set:
            (bbos_file, trds_file), strategy = next_params_set
            params = strategy.params()
            log.operation({'msg': 'backtest', 'params': params,
                           'bbos': bbos_file, 'trds': trds_file})

            bbos_df = feather.read_dataframe(bbos_file)
            bbos_df['symbol'] = bbos_df['symbol'].astype('category')
            bbos_df['ts'] = pd.to_datetime(bbos_df['ts'])

            trds_df = feather.read_dataframe(trds_file)
            trds_df['symbol'] = trds_df['symbol'].astype('category')
            trds_df['ts'] = pd.to_datetime(trds_df['ts'])
            trds_df.index = trds_df['ts']

            signals = backtest([strategy], bbos_df, trds_df)
            results = []
            for signal in signals:
                outcomes = compute_outcomes(signal, trds_df, exit_timeouts)
                results.extend([{**params, **outcome} for outcome in outcomes])
            if results:
                (pd.DataFrame.from_dict(results)
                   .to_csv('gridsearch.csv', index=False, mode='a'))
        else:
            break

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='gridsearch')
    parser.add_argument('--data_dir')
    args = parser.parse_args()

    log = Logger('gridsearch')
    log.operation('launching parameters grid search')

    pathname = '{}/*.201?????.feather'.format(args.data_dir)
    data_files = glob.glob(pathname)
    dates = set()
    for data_file in data_files:
        result = re.search('201\d{5}', data_file)
        if result:
            dates.add(result.group())

    def file_tuple(data_dir, date):
        bbos_file = '{}/bbos.{}.feather'.format(data_dir, date)
        trds_file = '{}/trds.{}.feather'.format(data_dir, date)
        return bbos_file, trds_file

    file_tuples = [file_tuple(args.data_dir, date) for date in dates]

    queue = Queue()
    num_workers = cpu_count() - 1
    worker = lambda: Process(target=backtester, args=[queue])
    backtesters = [worker() for i in range(num_workers)]
    [backtester.start() for backtester in backtesters]

    # loop over all possibilities
    combos = product(file_tuples, watch_thrshlds, watch_drtns,
                     slowdown_thrshlds, slowdown_drtns)
    combos = [(fs, wt, wd, st, sd)
              for (fs, wt, wd, st, sd) in combos
              if sd < wd and st < wt]
    log.operation('# runs: {}'.format(len(combos)))
    for files, wt, wd, st, sd in combos:
        if sd < wd and st < wt:
            queue.put((files, Recoil2(wt, wd, st, sd)))

    [queue.put(None) for i in range(num_workers)]
    queue.close()
    [backtester.join() for backtester in backtesters]

