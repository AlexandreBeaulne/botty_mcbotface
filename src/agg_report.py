
import argparse
import json
import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def unix_ts(ts):
    return pd.to_datetime(ts).timestamp()

def parse_ts(ts):
    # times are in UTC in logs
    return np.datetime64(ts+'+0000')

def print_html(figures):
    print("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>report</title></head><body>""")

    print('<h1>Aggregated Report</h1>')

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
                        ticker_id = log['msg']['tickerId']
                        ts = parse_ts(log['ts'])
                        px = log['msg']['price']
                        trades.append({'ts': ts, 'px': px, 'tickerId': ticker_id})

                elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
                    signal = dict()
                    signal['tickerId'] = log['msg']['tickerId']
                    signal['ts'] = parse_ts(log['ts'])
                    signal['px'] = log['msg']['current_px']
                    signal['direction'] = log['msg']['direction']
                    signals.append(signal)

        trades = pd.DataFrame(trades)
        graphs = []

        for signal in signals:

            # extract vars for the graphs
            ts = signal['ts']
            ticker_id = signal['tickerId']
            px = signal['px']
            direction = signal['direction']

            # isolate data around the signal
            start = ts - np.timedelta64(2 * watch_duration, 's')
            end = ts + np.timedelta64(2 * watch_duration, 's')
            filter_ = (trades['ts'] >= start) & (trades['ts'] <= end)
            filter_ &= (trades['tickerId'] == ticker_id)
            data = trades[filter_]
            ts = unix_ts(ts)

            signal = {'xs': [unix_ts(x) - ts for x in data['ts']],
                      'ys': data['px'] / px}
            if direction == 'long':
                long_signals.append(signal)
            elif direction == 'short':
                short_signals.append(signal)

    for signal in long_signals:
        plt.plot(signal['xs'], signal['ys'])
    plt.title('{} LONG signals'.format(len(long_signals)))
    plt.tight_layout()
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    long_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    plt.clf()

    for signal in short_signals:
        plt.plot(signal['xs'], signal['ys'])
    plt.title('{} SHORT signals'.format(len(short_signals)))
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    short_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    print_html([long_graph_figure, short_graph_figure])

