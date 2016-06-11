
import sys
import json
import pandas as pd

from bot.bookbuilder import BookBuilder

if __name__ == '__main__':

    builder = BookBuilder()
    logs = (json.loads(line) for line in sys.stdin)
    ticks = [builder.process_raw_tick(log['msg']) for log in logs]
    bbos = (tick for tick in ticks if tick and tick['type'] == 'bbo')
    bbos = pd.DataFrame.from_dict(bbos).drop('type', axis=1)
    trds = (tick for tick in ticks if tick and tick['type'] == 'trd')
    trds = pd.DataFrame.from_dict(trds).drop('type', axis=1)

    bbos_df = pd.read_csv('logs/bbos.csv.gz')
    trds_df = pd.read_csv('logs/trds.csv.gz')

    bbos_df = pd.concat([bbos_df, bbos]).sort_values('ts')
    trds_df = pd.concat([trds_df, trds]).sort_values('ts')

    cols = ['ts', 'symbol', 'bid_sz', 'bid_px', 'ask_px', 'ask_sz']
    bbos_df.to_csv('logs/bbos.csv.gz', compression='gzip',
                   index=False, columns=cols)

    cols = ['ts', 'symbol', 'sz', 'px']
    trds_df.to_csv('logs/trds.csv.gz', compression='gzip',
                   index=False, columns=cols)

