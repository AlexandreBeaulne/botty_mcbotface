
import numpy as np
import pandas as pd
import dask.dataframe as dd

if __name__ == '__main__':

    cols = ['watch_threshold', 'watch_duration', 'slowdown_threshold',
            'slowdown_duration', 'direction', 'timeout']

    # raw dataset is too big for in-memory manipulation.
    # start by doing a big out-of-memory groubpy using Dask

    trades = dd.read_csv('gridsearch.csv')

    gby = trades.groupby(cols)

    gby.count().to_csv('count.csv')
    gby.min().to_csv('min.csv')
    gby.mean().to_csv('mean.csv')
    gby.max().to_csv('max.csv')
    gby['return'].apply(np.std, columns='return').to_csv('std.csv')

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
    df = (counts.join(mins, how='outer')
                .join(means, how='outer')
                .join(maxs, how='outer')
                .join(stds, how='outer')
                .reset_index())

    results = (df.loc[df['count'] > 36]
                 .sort_values('mean', ascending=False))
    results.to_csv('gridsearch_results.csv', index=False)
    print(results.head(25))

