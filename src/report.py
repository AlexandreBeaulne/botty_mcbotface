
import sys
import json
import argparse
import pandas
import collections
import datetime

def pretty_ts(ts, offset):
    ts  = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f %Z')
    ts += datetime.timedelta(hours=offset)
    return ts.strftime('%Y-%m-%d %H:%M:%S.%f')

def get_symbol(instrument_mapping, ticker_id):
    return instrument_mapping.get(ticker_id, 'ticker ID: {}'.format(ticker_id))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="human-readable report from logs")
    config_file = parser.add_argument('--tz-offset', type=int, default=-4)
    args = parser.parse_args()

    logs = collections.defaultdict(list)

    for line in sys.stdin:

        log = json.loads(line)

        if log['type'] == 'OPERATION' and 'instrument_mapping' in log['msg']:
            instrument_mapping = log['msg']['instrument_mapping']
            instrument_mapping = {int(i):s for i, s in instrument_mapping.items()}

        elif log['type'] == 'DATA':

            # trade price
            if log['msg']['type'] == 'tickPrice' and log['msg']['field'] == 4:
                symbol = get_symbol(instrument_mapping, log['msg']['tickerId'])
                ts = pretty_ts(log['ts'], args.tz_offset)
                new_log = '{} trade px {}'.format(ts, log['msg']['price'])
                logs[symbol].append(new_log)

        elif log['type'] == 'ORDER' and log['msg'] == 'signal triggered':
            symbol = get_symbol(instrument_mapping, log['tickerId'])
            fmt  = '{} signal triggered! px watch duration ago: {} '
            fmt += 'px slowdown duration ago: {} current px: {}'
            ts = pretty_ts(log['ts'], args.tz_offset)
            new_log = fmt.format(ts, log['pxWatchDurationAgo'],
                                 log['pxSlowdownDurationAgo'], log['currentPx'])
            logs[symbol].append(new_log)

    for symbol, logs in logs.items():
        print('\n==========={}==========='.format(symbol))
        for log in logs:
            print(log)

