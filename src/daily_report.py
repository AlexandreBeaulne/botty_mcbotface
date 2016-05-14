
import sys
import json
import io
import base64
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from utils import unix_ts, parse_ts
from math import floor, ceil
from datetime import timezone, timedelta, datetime

def pretty_label(ts, offset=-4):
    ts = datetime.fromtimestamp(ts).replace(tzinfo=timezone(timedelta()))
    return ts.astimezone(timezone(timedelta(hours=offset))).strftime('%H:%M:%S')

def pretty_ts(ts, offset=-4):
    ts = pd.to_datetime(ts).tz_localize('UTC')
    ts = ts.astimezone(timezone(timedelta(hours=offset)))
    return ts.strftime('%A %B %d %Y, %H:%M:%S %Z')

def print_html(metadata, figures):
    print("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>report</title></head><body>""")

    print('<h1>Daily Report</h1>')

    row_fmt = '<tr><td>{}:</td><td>{}{}</td></tr>'

    print('<table>')
    print(row_fmt.format('watch duration', metadata['watch_duration'], 's'))
    print(row_fmt.format('watch threshold', 100 * metadata['watch_threshold'], '%'))
    print(row_fmt.format('slowdown duration', metadata['slowdown_duration'], 's'))
    print(row_fmt.format('slowdown threshold', 100 * metadata['slowdown_threshold'], '%'))
    print(row_fmt.format('start time', metadata['start'], ''))
    print(row_fmt.format('end time', metadata['end'], ''))
    print(row_fmt.format('# instruments', metadata['num_instruments'], ''))
    print(row_fmt.format('# trades', metadata['num_trades'], ''))
    print(row_fmt.format('# signals', metadata['num_signals'], ''))
    print('</table>')

    for figure in figures:
        print("<img src='data:image/png;base64,{}'/></td></tr>".format(figure))

    print('</body></html>')

if __name__ == '__main__':

    trades = []
    signals = []

    for log in sys.stdin:

        log = json.loads(log)

        if log['type'] == 'OPERATION' and 'config' in log['msg']:
            watch_threshold = log['msg']['config']['watch_threshold']
            watch_duration = log['msg']['config']['watch_duration']
            slowdown_threshold = log['msg']['config']['slowdown_threshold']
            slowdown_duration = log['msg']['config']['slowdown_duration']

        elif log['type'] == 'DATA':

            # trade price
            if log['msg']['type'] == 'tickPrice' and log['msg']['field'] == 4:
                symbol = log['msg']['symbol']
                ts = parse_ts(log['ts'])
                px = log['msg']['price']
                trades.append({'symbol': symbol, 'ts': ts, 'px': px})

        elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
            signal = dict()
            signal['symbol'] = log['msg']['symbol']
            signal['ts'] = parse_ts(log['ts'])
            signal['px'] = log['msg']['current_px']
            signal['direction'] = log['msg']['direction']
            signal['watch_ts'] = parse_ts(log['msg']['watch_ts'])
            signal['watch_px'] = log['msg']['watch_px']
            signal['watch_chng'] = log['msg']['watch_chng']
            signal['slowdown_ts'] = parse_ts(log['msg']['slowdown_ts'])
            signal['slowdown_px'] = log['msg']['slowdown_px']
            signal['slowdown_chng'] = log['msg']['slowdown_chng']
            signals.append(signal)

    metadata = dict()
    metadata['watch_threshold'] = watch_threshold
    metadata['watch_duration'] = watch_duration
    metadata['slowdown_threshold'] = slowdown_threshold
    metadata['slowdown_duration'] = slowdown_duration
    metadata['start'] = pretty_ts(trades[0]['ts'])
    metadata['end'] = pretty_ts(trades[-1]['ts'])
    metadata['num_instruments'] = len({trade['symbol'] for trade in trades})
    metadata['num_trades'] = len(trades)
    metadata['num_signals'] = len(signals)

    trades = pd.DataFrame(trades)
    graphs = []

    for signal in signals:

        # extract vars for the graphs
        ts = signal['ts']
        symbol = signal['symbol']
        watch_ts = unix_ts(signal['watch_ts'])
        watch_px = signal['watch_px']
        slowdown_ts = unix_ts(signal['slowdown_ts'])
        slowdown_px = signal['slowdown_px']
        px = signal['px']
        direction = signal['direction']

        # isolate data around the signal
        start = ts - np.timedelta64(3 * watch_duration, 's')
        end = ts + np.timedelta64(3 * watch_duration, 's')
        filter_ = (trades['ts'] >= start) & (trades['ts'] <= end)
        filter_ &= (trades['symbol'] == symbol)
        data = trades[filter_]

        # plot
        xs = [unix_ts(ts) for ts in data['ts']]
        xticks = range(floor(unix_ts(start)/10)*10, ceil(unix_ts(end)/10)*10, 10)
        plt.plot(xs, data['px'])
        fmt = '{}: {} signal on {}'
        plt.title(fmt.format(pretty_ts(ts), direction.upper(), symbol))
        ts = unix_ts(ts)
        plt.plot(ts, px, 'x', mew=2, ms=20, color='r')
        plt.plot((watch_ts, ts), (px, px), 'k:')
        plt.plot((watch_ts, watch_ts), (watch_px, px), 'k:')
        plt.plot((slowdown_ts, ts), (px, px), 'k:')
        plt.plot((slowdown_ts, slowdown_ts), (slowdown_px, px), 'k:')
        labels = [pretty_label(x) for x in xticks]
        plt.xticks(xticks, labels, rotation='vertical')
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')
        graphs.append(graph_figure)

    print_html(metadata, graphs)

