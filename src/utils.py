
import copy
import time
import json
import numpy as np
from datetime import datetime, timedelta, timezone

def ts():
    timestamp = datetime.now(tz=timezone(timedelta(seconds=-time.timezone)))
    return timestamp.strftime('%Y-%m-%dT%H:%M:%S.%f%z')

def now():
    return np.datetime64(ts())

class Logger(object):

    def __init__(self):
        log = 'log.{}.jsonl'.format(datetime.now().strftime('%Y%m%d'))
        self.fh = open(log, 'a')

    def __log__(self, type_, msg):
        msg = copy.deepcopy(msg)
        template = '{{"ts": "{}", "type": "{}", "msg": {}}}\n'
        if 'ts' in msg:
            timestamp = str(msg['ts'])
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

