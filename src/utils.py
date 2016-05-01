
import time
import json
import numpy as np
from datetime import datetime

def now():
    return np.datetime64(datetime.now().isoformat())

class log(object):

    @staticmethod
    def __log__(level, msg):
        template = '{{"ts": "{}", "level": "{}", "msg": {}}}'
        t = datetime.now().isoformat()
        tz = time.tzname[0]
        ts = '{} {}'.format(t, tz)
        print(template.format(ts, level, json.dumps(msg)))

    @staticmethod
    def info(msg):
        log.__log__('INFO', msg)

    @staticmethod
    def warn(msg):
        log.__log__('WARN', msg)

    @staticmethod
    def error(msg):
        log.__log__('ERROR', msg)

