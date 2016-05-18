
import sys
import queue
from wrapper import Wrapper
from ib.ext.Contract import Contract
from ib.ext.EClientSocket import EClientSocket

msgs = queue.Queue()
wrapper = Wrapper({}, msgs)
connection = EClientSocket(wrapper)

host = "54.197.15.42"
port = 7496

connection.eConnect(host, port, 1)
connection.reqScannerParameters()

for i in range(10):

    msg = msgs.get()
    if msg['type'] == 'scannerParameters':
        print(msg['xml'])
        sys.exit()

connection.eDisconnect()

