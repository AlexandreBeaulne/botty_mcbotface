
import copy
import time
import json
import numpy as np
import pandas as pd
from datetime import datetime

def ts():
    return datetime.utcnow().isoformat()

def now():
    return np.datetime64(ts())

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.datetime64):
            return pd.to_datetime(obj).isoformat()
        if isinstance(obj, np.float32):
            return float(obj)
        # Let the base class default method raise the TypeError
        return json.JSONEncoder.default(self, obj)

class Logger(object):

    def __init__(self, mode):
        datestr = datetime.utcnow().strftime('%Y%m%d')
        file_ = '{}.{}.jsonl'.format(mode, datestr)
        self.fh = open(file_, 'a')

    def __log__(self, type_, msg):
        msg = copy.deepcopy(msg)
        template = '{{"ts": "{}", "type": "{}", "msg": {}}}\n'
        if isinstance(msg, dict) and 'ts' in msg:
            timestamp = msg['ts'].tolist().isoformat()
        else:
            timestamp = ts()
        try:
            serialized_msg = json.dumps(msg, cls=NumpyEncoder)
        except:
            serialized_msg = json.dumps(str(msg))
            err = {'msg': 'Unable to JSON encode', 'log': serialized_msg}
            self.fh.write(template.format(timestamp, 'ERROR', json.dumps(err)))
        log = template.format(timestamp, type_, serialized_msg)
        self.fh.write(log)
        self.fh.flush()
        print(log, end='')

    def operation(self, msg):
        self.__log__('OPERATION', msg)

    def data(self, msg):
        self.__log__('DATA', msg)

    def raw(self, msg):
        self.__log__('RAW', msg)

    def order(self, msg):
        self.__log__('ORDER', msg)

    def execution(self, msg):
        self.__log__('EXECUTION', msg)

    def misc(self, msg):
        self.__log__('MISC', msg)

    def debug(self, msg):
        self.__log__('DEBUG', msg)

