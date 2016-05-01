
import time
import json
import numpy as np
from datetime import datetime

def now():
    return np.datetime64(datetime.now().isoformat())

class log(object):

    @staticmethod
    def __log__(type_, msg):
        template = '{{"ts": "{}", "type": "{}", "msg": {}}}'
        t = datetime.now().isoformat()
        tz = time.tzname[0]
        ts = '{} {}'.format(t, tz)
        print(template.format(ts, type_, json.dumps(msg)))

    @staticmethod
    def operation(msg):
        log.__log__('OPERATION', msg)

    @staticmethod
    def data(msg):
        log.__log__('DATA', msg)

    @staticmethod
    def order(msg):
        log.__log__('ORDER', msg)

    @staticmethod
    def execution(msg):
        log.__log__('EXECUTION', msg)

    @staticmethod
    def misc(msg):
        log.__log__('MISC', msg)

