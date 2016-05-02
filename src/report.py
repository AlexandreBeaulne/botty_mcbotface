
import sys
import json
import argparse
import pandas
import collections
import datetime

def pretty_ts(ts, offset):
    ts  = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f%z')
    ts += datetime.timedelta(hours=offset)
    return ts.strftime('%Y-%m-%d %H:%M:%S.%f')

def get_symbol(inst_map, ticker_id):
    return inst_map.get(ticker_id, 'ticker ID: {}'.format(ticker_id))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="human-readable report from logs")
    config_file = parser.add_argument('--tz-offset', type=int, default=-4)
    args = parser.parse_args()

    logs = collections.defaultdict(list)

    for log in sys.stdin:

        log = json.loads(log)

        if log['type'] == 'OPERATION' and 'config' in log['msg']:
            watch_threshold = log['msg']['config']['watch_threshold']
            watch_duration = log['msg']['config']['watch_duration']
            slowdown_threshold = log['msg']['config']['slowdown_threshold']
            slowdown_duration = log['msg']['config']['slowdown_duration']
            inst_map = log['msg']['config']['instruments']
            inst_map = {int(i):c['symbol'] for i, c in inst_map.items()}

        elif log['type'] == 'DATA':

            # trade price
            if log['msg']['type'] == 'tickPrice' and log['msg']['field'] == 4:
                symbol = get_symbol(inst_map, log['msg']['tickerId'])
                ts = pretty_ts(log['ts'], args.tz_offset)
                px = log['msg']['price']
                line = '{} trade - px: {}'.format(ts, px)
                logs[symbol].append(line)

        elif log['type'] == 'ORDER' and log['msg'] == 'signal triggered':
            symbol = get_symbol(inst_map, log['tickerId'])
            ts = pretty_ts(log['ts'], args.tz_offset)
            fmt  = '{} signal triggered! - px {}s ago: {}, '
            fmt += 'px {}s ago: {}, current px: {}'
            line = fmt.format(ts, log['pxWatchDurationAgo'], watch_duration,
                log['pxSlowdownDurationAgo'], slowdown_duration, log['currentPx'])
            logs[symbol].append(line)

    fmt = '\n##### symbol: {} - watch threshold: {}% - slowdown threshold: {}%'
    for symbol, logs in logs.items():
        print(fmt.format(symbol, 100 * watch_threshold, 100 * slowdown_threshold))
        for log in logs:
            print(log)

