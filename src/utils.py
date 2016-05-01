
import time
import json
import numpy as np
from datetime import datetime

def now():
    return np.datetime64(datetime.now().isoformat())

class Logger(object):

    def __init__(self):
        log = 'recoil.{}.jsonl'.format(datetime.now().strftime('%Y%M%d.%H%M%S'))
        self.fh = open(log, 'w')

    def __log__(self, type_, msg):
        template = '{{"ts": "{}", "type": "{}", "msg": {}}}\n'
        t = datetime.now().isoformat()
        tz = time.tzname[0]
        ts = '{} {}'.format(t, tz)
        log = template.format(ts, type_, json.dumps(msg))
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

