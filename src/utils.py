
import copy
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime

def unix_ts(ts):
    return pd.to_datetime(ts).timestamp()

def parse_ts(ts):
    # times are in UTC in logs
    return np.datetime64(ts+'+0000')

def ts():
    return datetime.utcnow().isoformat()

def now():
    return np.datetime64(ts())

class Logger(object):

    def __init__(self, mode):
        if mode == 'log':
            datestr = datetime.utcnow().strftime('%Y%m%d')
        elif mode == 'replay':
            datestr = datetime.utcnow().strftime('%Y%m%d.%H%M%S')
        else:
            print('ERROR unknown mode')
            raise Exception
        file_ = '{}.{}.jsonl'.format(mode, datestr)
        self.fh = open(file_, 'a')

    def __log__(self, type_, msg):
        msg = copy.deepcopy(msg)
        template = '{{"ts": "{}", "type": "{}", "msg": {}}}\n'
        if 'ts' in msg:
            timestamp = msg['ts'].tolist().isoformat()
            del msg['ts']
        else:
            timestamp = ts()
        log = template.format(timestamp, type_, json.dumps(msg))
        self.fh.write(log)
        print(log)

    def operation(self, msg):
        self.__log__('OPERATION', msg)

    def data(self, msg):
        self.__log__('DATA', msg)

    def order(self, msg):
        self.__log__('ORDER', msg)

    def execution(self, msg):
        self.__log__('EXECUTION', msg)

    def misc(self, msg):
        self.__log__('MISC', msg)

