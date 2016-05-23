
import sys
import queue
from wrapper import Wrapper
from ib.ext.ScannerSubscription import ScannerSubscription
from ib.ext.EClientSocket import EClientSocket

from utils import Logger

log = Logger('scanner')

msgs = queue.Queue()
wrapper = Wrapper({}, msgs)
connection = EClientSocket(wrapper)

host = "54.197.15.42"
port = 7496

connection.eConnect(host, port, 1)
subscription = ScannerSubscription()
subscription.numberOfRows(100)
subscription.instrument('STK')
subscription.locationCode('STK.US')
subscription.scanCode('TOP_PERC_GAIN')
subscription.abovePrice(1.0)
subscription.aboveVolume(1)
subscription.marketCapBelow(1000000000.0)

ticker_id = 10

log.operation('Requesting subscription')

connection.reqScannerSubscription(ticker_id, subscription)

while True:
    msg = msgs.get()
    if msg['type'] == 'scannerDataEnd':
        log.operation('Received end scanner data end signal')
        break
    elif msg['type'] == 'scannerData':
        log.data(msg)
    else:
        log.misc(msg)

log.operation('Disconnecting')
connection.cancelScannerSubscription(ticker_id)
connection.eDisconnect()

