
import numpy as np
import pandas as pd
import dask.dataframe as dd

def downside_deviation(xs):
    return np.std([x for x in xs if x < 0])

if __name__ == '__main__':

    cols = ['strategy', 'watch_threshold', 'watch_duration', 'slowdown_threshold',
            'slowdown_duration', 'direction', 'timeout']

    # raw dataset is too big for in-memory manipulation.
    # start by doing a big out-of-memory groubpy using Dask

    trades = dd.read_csv('gridsearch.csv')

    gby = trades.groupby(cols)

    gby.count().to_csv('count.csv')
    gby.min().to_csv('min.csv')
    gby.mean().to_csv('mean.csv')
    gby.max().to_csv('max.csv')
    gby.apply(np.std)['return'].to_csv('std.csv')
    gby.apply(downside_deviation)['return'].to_csv('downside_dev.csv')

    # next present the results using full pandas feature set

    counts = (pd.read_csv('count.csv', index_col=cols)
                .rename(columns={'return': 'count'}))
    mins = (pd.read_csv('min.csv', index_col=cols)
              .rename(columns={'return': 'min'}))
    means = (pd.read_csv('mean.csv', index_col=cols)
               .rename(columns={'return': 'mean'}))
    maxs = (pd.read_csv('max.csv', index_col=cols)
              .rename(columns={'return': 'max'}))
    stds = pd.read_csv('std.csv', index_col=cols, header=None,
                       names=cols + ['std'])
    downside_devs = pd.read_csv('downside_dev.csv', index_col=cols, header=None,
                                names=cols + ['downside_dev'])

    df = (counts.join(mins, how='outer')
                .join(means, how='outer')
                .join(maxs, how='outer')
                .join(stds, how='outer')
                .join(downside_devs, how='outer')
                .reset_index())

    df.to_csv('gridsearch_results.csv', index=False)

