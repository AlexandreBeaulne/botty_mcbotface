
import argparse
import json
import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import unix_ts, parse_ts

EXIT_PERIOD = 20 # exit time of trade in seconds

def asof(xs, ys, offset):
    if offset < xs[0]:
        print('ERROR impossible asof parameters')
        raise Exception
    for x, y in zip(xs, [None] + ys):
        if x > offset:
            return y
    return y

def print_html(figures):
    print("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>report</title></head><body>""")

    print('<h1>Aggregated Report</h1>')

    print('<ul>')
    print('<li>Pre fees and slippage</li>')
    print('<li>"Good" call is when price moved in right direction</li>')
    print('<li>"Bad" call is when price moved in wrong direction or didnt move</li>')
    print('</ul>')

    for figure in figures:
        print("<img src='data:image/png;base64,{}'/></td></tr>".format(figure))

    print('</body></html>')

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="aggregated report")
    parser.add_argument('--logs', nargs='*')
    args = parser.parse_args()

    long_signals = []
    short_signals = []

    for log in args.logs:
        with open(log, 'r') as fh:

            trades = []
            signals = []

            for log in fh:

                log = json.loads(log)

                if log['type'] == 'OPERATION' and 'config' in log['msg']:
                    watch_duration = log['msg']['config']['watch_duration']
                    slowdown_duration = log['msg']['config']['slowdown_duration']

                elif log['type'] == 'DATA':

                    # trade price
                    if log['msg']['type'] == 'tickPrice' and log['msg']['field'] == 4:
                        symbol = log['msg']['symbol']
                        ts = parse_ts(log['ts'])
                        px = log['msg']['price']
                        trades.append({'ts': ts, 'px': px, 'symbol': symbol})

                elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
                    signal = dict()
                    signal['symbol'] = log['msg']['symbol']
                    signal['ts'] = parse_ts(log['ts'])
                    signal['px'] = log['msg']['current_px']
                    signal['direction'] = log['msg']['direction']
                    signals.append(signal)

        trades = pd.DataFrame(trades)
        graphs = []

        for signal in signals:

            # extract vars for the graphs
            ts = signal['ts']
            symbol = signal['symbol']
            px = signal['px']
            direction = signal['direction']

            # isolate data around the signal
            start = ts - np.timedelta64(2 * watch_duration, 's')
            end = ts + np.timedelta64(2 * watch_duration, 's')
            filter_ = (trades['ts'] >= start) & (trades['ts'] <= end)
            filter_ &= (trades['symbol'] == symbol)
            data = trades[filter_]
            ts = unix_ts(ts)

            signal = {'xs': [unix_ts(x) - ts for x in data['ts']],
                      'ys': (data['px'] / px).tolist()}
            if direction == 'long':
                long_signals.append(signal)
            elif direction == 'short':
                short_signals.append(signal)

    long_returns = []
    for signal in long_signals:
        long_returns.append(asof(signal['xs'], signal['ys'], EXIT_PERIOD))
    long_num_signals = len(long_signals)
    num_good_calls = [r for r in long_returns if r > 1]
    long_pcnt_good_calls = round(100 * len(num_good_calls) / long_num_signals)
    num_bad_calls = [r for r in long_returns if r <= 1]
    long_pcnt_bad_calls = round(100 * len(num_bad_calls) / long_num_signals)

    for signal in long_signals:
        plt.plot(signal['xs'], signal['ys'])
    fmt = '{} LONG signals: {}% good calls, {}% bad calls after {}s'
    plt.title(fmt.format(long_num_signals, long_pcnt_good_calls,
        long_pcnt_bad_calls, EXIT_PERIOD))
    plt.tight_layout()
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    long_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    plt.clf()

    short_returns = []
    for signal in short_signals:
        short_returns.append(asof(signal['xs'], signal['ys'], EXIT_PERIOD))
    short_num_signals = len(short_signals)
    num_good_calls = [r for r in short_returns if r < 1]
    short_pcnt_good_calls = round(100 * len(num_good_calls) / short_num_signals)
    num_bad_calls = [r for r in short_returns if r >= 1]
    short_pcnt_bad_calls = round(100 * len(num_bad_calls) / short_num_signals)

    for signal in short_signals:
        plt.plot(signal['xs'], signal['ys'])
    fmt = '{} short signals: {}% good calls, {}% bad calls after {}s'
    plt.title(fmt.format(short_num_signals, short_pcnt_good_calls,
        short_pcnt_bad_calls, EXIT_PERIOD))
    plt.tight_layout()
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    short_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    print_html([long_graph_figure, short_graph_figure])

