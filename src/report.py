
import sys
import os
import io
import base64
import gzip
import json
import argparse
import jinja2
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from math import floor, ceil
from utils import unix_ts, parse_ts, pretty_ts, pretty_date, pretty_label

def parse_log(params, file_handle):
    signals = []
    for line in file_handle:
        log = json.loads(line)
        if log['type'] == 'OPERATION' and 'config' in log['msg']:
            config = log['msg']['config']
            tmp = dict()
            tmp['watch_threshold'] = config['watch_threshold']
            tmp['watch_duration']= config['watch_duration']
            tmp['slowdown_threshold'] = config['slowdown_threshold']
            tmp['slowdown_duration'] = config['slowdown_duration']
            if params and tmp != params:
                print('[ERROR] building report from logs with different params')
                sys.exit(1)
            params = tmp
        elif log['type'] == 'ORDER' and log['msg']['msg'] == 'signal triggered':
            signal = dict()
            signal['symbol'] = log['msg']['symbol']
            signal['ts'] = parse_ts(log['ts'])
            signal['current_px'] = log['msg']['current_px']
            signal['direction'] = log['msg']['direction']
            signal['watch_ts'] = parse_ts(log['msg']['watch_ts'])
            signal['watch_px'] = log['msg']['watch_px']
            signal['watch_chng'] = log['msg']['watch_chng']
            signal['slowdown_ts'] = parse_ts(log['msg']['slowdown_ts'])
            signal['slowdown_px'] = log['msg']['slowdown_px']
            signal['slowdown_chng'] = log['msg']['slowdown_chng']
            signals.append(signal)
    return params, signals

def parse_logs(logs):
    params = dict()
    signals = []
    for logfile in logs:
        with io.TextIOWrapper(gzip.open(logfile, 'r')) as fh:
            params, logsignals = parse_log(params, fh)
        signals += logsignals
    return params, signals

def build_graph(signal, params, bbos, trds):

    # extract vars for the graphs
    ts = signal['ts']
    symbol = signal['symbol']
    watch_ts = unix_ts(signal['watch_ts'])
    watch_px = signal['watch_px']
    slowdown_ts = unix_ts(signal['slowdown_ts'])
    slowdown_px = signal['slowdown_px']
    px = signal['current_px']
    direction = signal['direction']
    watch_duration = params['watch_duration']

    # isolate data around the signal
    start = ts - np.timedelta64(3 * watch_duration, 's')
    end = ts + np.timedelta64(3 * watch_duration, 's')
    filter_ = (trds.index >= start) & (trds.index <= end)
    filter_ &= (trds['symbol'] == symbol)
    trds = trds[filter_]
    filter_ = (bbos['ts'] >= start) & (bbos['ts'] <= end)
    filter_ &= (bbos['symbol'] == symbol)
    bbos = bbos[filter_]

    # plot
    fig, ax1 = plt.subplots()
    xs = [unix_ts(ts) for ts in trds.index]
    ax1.plot(xs, trds['px'], marker='.', color='k', linestyle='', label='trades')
    xs = [unix_ts(ts) for ts in bbos['ts']]
    ax1.step(xs, bbos['bid_px'], color='b', label='bids', where='post')
    ax1.step(xs, bbos['ask_px'], color='r', label='asks', where='post')
    fmt = '{}: {} signal on {}'
    plt.title(fmt.format(pretty_ts(ts), direction.upper(), symbol))
    ts = unix_ts(ts)
    ax1.plot(ts, px, 'x', mew=2, ms=20, color='r')
    ax1.plot((watch_ts, ts), (px, px), 'k:')
    ax1.plot((watch_ts, watch_ts), (watch_px, px), 'k:')
    ax1.plot((slowdown_ts, ts), (px, px), 'k:')
    ax1.plot((slowdown_ts, slowdown_ts), (slowdown_px, px), 'k:')
    xticks = range(floor(unix_ts(start)/10)*10, ceil(unix_ts(end)/10)*10, 10)
    labels = [pretty_label(x) for x in xticks]
    plt.xticks(xticks, labels, rotation='vertical')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, 0.975 * y1, 1.025 * y2))
    ax1.set_ylabel('price')
    plt.legend(loc=0)

    # volume bars
    ax2 = ax1.twinx()
    bin_sz = 5
    trds = trds.sz.groupby(pd.TimeGrouper('{}s'.format(bin_sz))).sum()
    xs = [unix_ts(ts) for ts in trds.index]
    ax2.bar(xs, trds, width=bin_sz)
    ax2.set_ylabel('volume (lots)')
    x1, x2, y1, y2 = plt.axis()
    plt.axis((x1, x2, y1, 10 * y2))

    # save to png
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    return base64.b64encode(buf.getvalue()).decode('ascii')

def normalize_signal(signal, params, trds):

    # extract vars for the graphs
    ts = signal['ts']
    symbol = signal['symbol']
    px = signal['current_px']
    direction = signal['direction']
    watch_duration = params['watch_duration']

    # isolate data around the signal
    start = ts - np.timedelta64(3 * watch_duration, 's')
    end = ts + np.timedelta64(3 * watch_duration, 's')
    filter_ = (trds.index >= start) & (trds.index <= end)
    filter_ &= (trds['symbol'] == symbol)
    data = trds[filter_]
    ts = unix_ts(ts)

    return {'xs': [unix_ts(x) - ts for x in data.index],
            'ys': (data['px'] / px).tolist(), 'direction': direction}

def normalized_graphs(signals):

    longs = [s for s in signals if s['direction'] == 'long']
    for signal in longs:
        plt.plot(signal['xs'], signal['ys'])
    plt.title('{} LONG signals'.format(len(longs)))
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    long_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    shorts = [s for s in signals if s['direction'] == 'short']
    for signal in shorts:
        plt.plot(signal['xs'], signal['ys'])
    plt.title('{} SHORT signals'.format(len(shorts)))
    plt.xlabel('seconds (signal == 0)')
    plt.ylabel('price (signal == 1)')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    short_graph_figure = base64.b64encode(buf.getvalue()).decode('ascii')

    return long_graph_figure, short_graph_figure

def compute_outcomes(signal, trds, exit_timeouts):
    sym = signal['symbol']
    t0 = signal['ts']
    px0 = signal['current_px']
    dir = signal['direction']
    mult = {'long': 100, 'short': -100}[dir]
    outcomes = []
    df = trds[trds['symbol'] == sym]
    for exit_timeout in exit_timeouts:
        t = df.index.asof(t0 + np.timedelta64(exit_timeout, 's'))
        px = df.loc[t]['px']
        return_ = mult * (px / px0 - 1)
        outcome = {'direction': dir, 'timeout': exit_timeout, 'return': return_}
        outcomes.append(outcome)
    return outcomes

def outcomes_graphs(direction, outcomes):
    df = outcomes[outcomes['direction'] == direction][['return', 'timeout']]
    if not df.empty:
        df = df.set_index('timeout', append=True).unstack()
        df.columns = df.columns.droplevel()
        df.plot.box()
        avgs = df.mean()
        plt.plot(avgs.index // 5, avgs.values, label='avg', marker='H', color='k', linestyle='')
        plt.xlabel('time after signal (s)')
        plt.ylabel('return (%)')
        title = '{} calls - distribution of price movements post-signal'
        plt.title(title.format(direction))
        plt.legend(loc=0)
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        return base64.b64encode(buf.getvalue()).decode('ascii')

def rebuild_index():

    for _dirname, _dirnames, filenames in os.walk('reports/'):
        files = [f for f in filenames if 'report' in f]

    with open('reports/index_template.html') as fh:
        template = jinja2.Template(fh.read())

    with open('reports/index.html', 'w') as fh:
        fh.write(template.render(reports=files))

if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="report")
    parser.add_argument('--logs', nargs='+')
    args = parser.parse_args()

    params, signals = parse_logs(args.logs)

    bbos = pd.read_csv('logs/bbos.csv.gz', parse_dates=['ts'])
    trds = pd.read_csv('logs/trds.csv.gz', parse_dates=['ts']).set_index('ts')

    data = dict()
    data['figures'] = [build_graph(s, params, bbos, trds) for s in signals]
    normalized = [normalize_signal(s, params, trds) for s in signals]
    data['longs'], data['shorts'] = normalized_graphs(normalized)
    outcomes = [compute_outcomes(s, trds, range(5, 180, 5)) for s in signals]
    outcomes = pd.DataFrame.from_dict([x for xs in outcomes for x in xs])
    data['longs_distn'] = outcomes_graphs('long', outcomes)
    data['shorts_distn'] = outcomes_graphs('short', outcomes)

    with open('reports/template.html') as fh:
        template = jinja2.Template(fh.read())

    min_date = min([s['ts'] for s in signals])
    max_date = max([s['ts'] for s in signals])
    params['start'] = pretty_ts(min_date)
    params['end'] = pretty_ts(max_date)
    data['params'] = params
    filename = 'reports/report.{}.{}.html'
    filename = filename.format(pretty_date(min_date), pretty_date(max_date))
    with open(filename, 'w') as fh:
        fh.write(template.render(data=data))

    rebuild_index()

