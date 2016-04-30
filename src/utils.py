
import time
import json
from datetime import datetime

class log(object):

    @staticmethod
    def __log__(level, msg):
        template = '{{"ts": "{}", "level": "{}", "msg": {}}}'
        t = datetime.now().strftime('%Y-%m-%dD%H:%M:%S.%f')
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

