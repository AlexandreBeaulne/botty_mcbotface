
import sys
import json
import pandas as pd
import feather

from bot.bookbuilder import BookBuilder

if __name__ == '__main__':

    date = sys.argv[1]
    builder = BookBuilder()
    logs = (json.loads(line) for line in sys.stdin)
    ticks = [builder.process_raw_tick(log['msg']) for log in logs]

    # BBOS
    bbos = (tick for tick in ticks if tick and tick['type'] == 'bbo')
    bbos = pd.DataFrame.from_dict(bbos).drop('type', axis=1)
    bbos = bbos[['ts', 'symbol', 'bid_sz', 'bid_px', 'ask_px', 'ask_sz']]
    feather.write_dataframe(bbos, 'logs/bbos.{}.feather'.format(date))

    # TRADES
    trds = (tick for tick in ticks if tick and tick['type'] == 'trd')
    trds = trds[['ts', 'symbol', 'sz', 'px']]
    trds = pd.DataFrame.from_dict(trds).drop('type', axis=1)
    feather.write_dataframe(trds, 'logs/trdss.{}.feather'.format(date))
