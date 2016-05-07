
import sys
import json
import io
import base64
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def get_symbol(inst_map, ticker_id):
    return inst_map.get(ticker_id, 'ticker ID: {}'.format(ticker_id))

def print_html(metadata, figures):
    print("""
    <!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">
    <html lang="en">
    <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8">
    <title>report</title></head><body>""")

    print('<h1>Report</h1>')

    print('<table>')
    print('<tr><td>watch duration:</td><td>{}s</td></tr>'.format(metadata['watch_duration']))
    print('<tr><td>watch threshold:</td><td>{}%</td></tr>'.format(100 * metadata['watch_threshold']))
    print('<tr><td>slowdown duration:</td><td>{}s</td></tr>'.format(metadata['slowdown_duration']))
    print('<tr><td>slowdown threshold:</td><td>{}%</td></tr>'.format(100 * metadata['slowdown_threshold']))
    print('<tr><td>start time:</td><td>{}</td></tr>'.format(metadata['start']))
    print('<tr><td>end time:</td><td>{}</td></tr>'.format(metadata['end']))
    print('<tr><td># instruments:</td><td>{}</td></tr>'.format(metadata['num_instruments']))
    print('<tr><td># trade ticks:</td><td>{}</td></tr>'.format(metadata['num_trades']))
    print('<tr><td># signals:</td><td>{}</td></tr>'.format(metadata['num_signals']))
    print('</table>')

    for figure in figures:
        print("<img src='data:image/png;base64,{}'/></td></tr>".format(figure))

    print('</body></html>')

if __name__ == '__main__':

    trades = []
    signals = []

    metadata = dict()

    for log in sys.stdin:

        log = json.loads(log)

        if log['type'] == 'OPERATION' and 'config' in log['msg']:
            metadata['watch_threshold'] = log['msg']['config']['watch_threshold']
            metadata['watch_duration'] = log['msg']['config']['watch_duration']
            metadata['slowdown_threshold'] = log['msg']['config']['slowdown_threshold']
            metadata['slowdown_duration'] = log['msg']['config']['slowdown_duration']
            inst_map = log['msg']['config']['instruments']
            inst_map = {int(i):c['symbol'] for i, c in inst_map.items()}

        elif log['type'] == 'DATA':

            # trade price
            if log['msg']['type'] == 'tickPrice' and log['msg']['field'] == 4:
                symbol = get_symbol(inst_map, log['msg']['tickerId'])
                ts = np.datetime64(log['ts'])
                px = log['msg']['price']
                trades.append({'symbol': symbol, 'ts': ts, 'px': px})

        elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
            signal = dict()
            signal['symbol'] = get_symbol(inst_map, log['msg']['tickerId'])
            signal['ts'] = np.datetime64(log['ts'])
            signal['px'] = log['msg']['current_px']
            signal['watch_ts'] = np.datetime64(log['msg']['watch_ts'])
            signal['watch_px'] = log['msg']['watch_px']
            signal['watch_chng'] = log['msg']['watch_chng']
            signal['slowdown_ts'] = np.datetime64(log['msg']['slowdown_ts'])
            signal['slowdown_px'] = log['msg']['slowdown_px']
            signal['slowdown_chng'] = log['msg']['slowdown_chng']
            signals.append(signal)

    metadata['start'] = trades[0]['ts']
    metadata['end'] = trades[-1]['ts']
    metadata['num_instruments'] = len(inst_map)
    metadata['num_trades'] = len(trades)
    metadata['num_signals'] = len(signals)

    trades = pd.DataFrame(trades)
    graphs = []

    for signal in signals:
        ts = signal['ts']
        symbol = signal['symbol']
        start = ts - np.timedelta64(2 * metadata['watch_duration'], 's')
        end = ts + np.timedelta64(2 * metadata['watch_duration'], 's')
        filter_ = (trades['ts'] >= start) & (trades['ts'] <= end)
        filter_ &= (trades['symbol'] == symbol)
        data = trades[filter_]

        plot = data.plot(x='ts', y='px')
        plot.legend().remove()
        fig = plot.get_figure()
        plt.plot(ts, signal['px'], 'x', mew=2, ms=20, color='r')
        plt.plot((signal['watch_ts'], ts), (signal['px'], signal['px']), 'k:')
        plt.plot((signal['watch_ts'], signal['watch_ts']), (signal['watch_px'], signal['px']), 'k:')
        plt.plot((signal['slowdown_ts'], ts), (signal['px'], signal['px']), 'k:')
        plt.plot((signal['slowdown_ts'], signal['slowdown_ts']), (signal['slowdown_px'], signal['px']), 'k:')
        plt.title(symbol)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        plt.close()
        graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')
        graphs.append(graph_figure)

    print_html(metadata, graphs)

