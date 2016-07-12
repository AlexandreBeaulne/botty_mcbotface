
import numpy as np
import pandas as pd

def downside_deviation(xs):
    return np.std(xs[xs<0])

if __name__ == '__main__':


    cols = ['strategy', 'watch_threshold', 'watch_duration',
            'slowdown_threshold', 'slowdown_duration', 'direction', 'timeout']

    lambdas = [np.size, np.min, np.mean, np.max, np.std, downside_deviation]
    results = (pd.read_csv('/dev/shm/gridsearch.csv')
                 .groupby(cols)
                 .agg(lambdas)
                 .reset_index())
    results.columns = cols + ['count', 'min', 'mean', 'max', 'stddev', 'downside_dev']
    results.to_csv('gridsearch_results.csv', index=False)

