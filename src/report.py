
import sys
import json
import argparse
import collections
import datetime
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def parse_ts(ts, offset):
    ts  = datetime.datetime.strptime(ts, '%Y-%m-%dT%H:%M:%S.%f%z')
    ts += datetime.timedelta(hours=offset)
    return np.datetime64(ts.isoformat())

def get_symbol(inst_map, ticker_id):
    return inst_map.get(ticker_id, 'ticker ID: {}'.format(ticker_id))

def print_html(metadata, figures):
    print("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>report</title></head><body>""")

    print('start time: {}</br>'.format(metadata['start']))
    print('end time:   {}</br>'.format(metadata['end']))
    print('{} instruments</br>'.format(metadata['instruments']))
    print('{} trade ticks</br>'.format(metadata['trades']))
    print('{} signals</br></br>'.format(metadata['signals']))

    for figure in figures:
        print("<img src='data:image/png;base64,{}'/></br>".format(figure))

    print('</body></html>')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="reports from logs")
    config_file = parser.add_argument('--tz-offset', type=int, default=-12)
    args = parser.parse_args()

    trades = []
    signals = []

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
                ts = parse_ts(log['ts'], args.tz_offset)
                px = log['msg']['price']
                trades.append({'symbol': symbol, 'ts': ts, 'px': px})

        elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
            symbol = get_symbol(inst_map, log['msg']['tickerId'])
            ts = parse_ts(log['ts'], args.tz_offset)
            signals.append({'symbol': symbol, 'ts': ts})


    metadata = {'start': trades[0]['ts'], 'end': trades[-1]['ts'],
                'instruments': len(inst_map), 'trades': len(trades),
                'signals': len(signals)}

    trades = pd.DataFrame(trades)
    signals = pd.DataFrame(signals)
    figures = []

    for _idx, signal in signals.iterrows():
        ts = signal['ts']
        symbol = signal['symbol']
        start = ts - np.timedelta64(2 * watch_duration, 's')
        end = ts + np.timedelta64(2 * watch_duration, 's')
        filter_ = (trades['ts'] >= start) & (trades['ts'] <= end)
        filter_ &= (trades['symbol'] == symbol)
        data = trades[filter_]

        plot = data.plot(x='ts', y='px')
        fig = plot.get_figure()
        plt.axvline(ts, color='r')
        plt.title(symbol)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close()
        figures.append(base64.b64encode(buf.getvalue()).decode('ascii'))

    print_html(metadata, figures)

