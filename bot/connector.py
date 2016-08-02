
from bot.utils import now

from ib.ext.EWrapper import EWrapper

class Connector(EWrapper):

    def __init__(self, inst_map, msgs):
        super(Connector, self).__init__()
        self.msgs = msgs
        self.inst_map = inst_map

    def tickPrice(self, tickerId, field, px, _canAutoExecute):
        msg = {'type': 'tickPrice', 'symbol': self.inst_map[tickerId]['symbol'],
               'field': field, 'price': px, 'ts': now()}
        self.msgs.put(msg)

    def tickSize(self, tickerId, field, sz):
        msg = {'type': 'tickSize', 'symbol': self.inst_map[tickerId]['symbol'],
               'field': field, 'size': sz, 'ts': now()}
        self.msgs.put(msg)

    def tickOptionComputation(self, tickerId, field, impliedVol, delta,
                              optPrice, pvDividend, gamma, vega, theta, undPrice):
        pass

    def tickGeneric(self, tickerId, tickType, value):
        msg = {'type': 'tickGeneric', 'symbol': self.inst_map[tickerId]['symbol'],
               'tickType': tickType, 'value': value, 'ts': now()}
        self.msgs.put(msg)

    def tickString(self, tickerId, tickType, value):
        msg = {'type': 'tickString', 'symbol': self.inst_map[tickerId]['symbol'],
               'tickType': tickType, 'value': value, 'ts': now()}
        self.msgs.put(msg)

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints,
                impliedFuture, holdDays, futureExpiry, dividendImpact,
                dividendsToExpiry):
        pass

    def orderStatus(self, orderId, status, filled, remaining, avgFillPrice,
                    permId, parentId, lastFillPrice, clientId, whyHeId):
        msg = {'type': 'orderStatus', 'orderId': orderId, 'status': status,
               'filled': filled, 'remaining': remaining,
               'avgFillPrice': avgFillPrice, 'permId': permId,
               'parentId': parentId, 'lastFillPrice': lastFillPrice,
               'clientId': clientId, 'whyHeId': whyHeId, 'ts': now()}
        self.msgs.put(msg)

    def openOrder(self, orderId, contract, order, state):
        msg = {'type': 'openOrder', 'orderId': orderId, 'contract': contract,
               'order': order, 'state': state, 'ts': now()}
        self.msgs.put(msg)

    def openOrderEnd(self):
        msg = {'type': 'openOrderEnd', 'ts': now()}
        self.msgs.put(msg)

    def updateAccountValue(self, key, value, currency, accountName):
        pass

    def updatePortfolio(self, contract, position, marketPrice, marketValue,
                        averageCost, unrealizedPNL, realizedPNL, accountName):
        pass

    def updateAccountTime(self, timeStamp):
        pass

    def accountDownloadEnd(self, accountName):
        pass

    def nextValidId(self, orderId):
        msg = {'type': 'nextValidId', 'orderId': orderId, 'ts': now()}
        self.msgs.put(msg)

    def contractDetails(self, reqId, contractDetails):
        pass

    def contractDetailsEnd(self, reqId):
        pass

    def bondContractDetails(self, reqId, contractDetails):
        pass

    def execDetails(self, reqId, contract, execution):
        msg = {'type': 'execDetails', 'reqId': reqId,
               'contract': contract, 'execution': execution, 'ts': now()}
        self.msgs.put(msg)

    def execDetailsEnd(self, reqId):
        msg = {'type': 'execDetailsEnd', 'reqId': reqId, 'ts': now()}
        self.msgs.put(msg)

    def connectionClosed(self):
        msg = {'type': 'connectionClosed'}
        self.msgs.put(msg)

    def error(self, id=None, errorCode=None, errorMsg=None):
        msg = {'type': 'error', 'id': id, 'errorCode': errorCode,
               'errorMsg': errorMsg, 'ts': now()}
        self.msgs.put(msg)

    def error_0(self, strvalue=None):
        msg = {'type': 'error_0', 'strvalue': strvalue, 'ts': now()}
        self.msgs.put(msg)

    def error_1(self, id=None, errorCode=None, errorMsg=None):
        msg = {'type': 'error_1', 'id': id, 'errorCode': errorCode,
               'errorMsg': errorMsg, 'ts': now()}
        self.msgs.put(msg)

    def updateMktDepth(self, tickerId, position, operation, side, price, size):
        pass

    def updateMktDepthL2(self, tickerId, position, marketMaker, operation,
                         side, price, size):
        pass

    def updateNewsBulletin(self, msgId, msgType, message, origExchange):
        pass

    def managedAccounts(self, accountsList):
        msg = {'type': 'managedAccounts',
               'accountsList': accountsList, 'ts': now()}
        self.msgs.put(msg)

    def receiveFA(self, faDataType, xml):
        pass

    def historicalData(self, reqId, date, open, high, low, close, volume,
                       count, WAP, hasGaps):
        msg = {'type': 'historicalData', 'reqId': reqId, 'date': date,
               'open': open, 'high': high, 'low': low, 'close': close,
               'volume': volume, 'count': count, 'WAP': WAP,
               'hasGaps': hasGaps, 'ts': now()}
        self.msgs.put(msg)

    def scannerParameters(self, xml):
        msg = {'type': 'scannerParameters', 'xml': xml}
        self.msgs.put(msg)

    def scannerData(self, reqId, rank, contractDetails, distance, benchmark,
                    projection, legsStr):
        msg = {'type': 'scannerData', 'reqId': reqId, 'rank': rank,
               'contractDetails': contractDetails, 'distance': distance,
               'benchmark': benchmark, 'projection': projection,
               'legsStr': legsStr}
        self.msgs.put(msg)

    def accountDownloadEnd(self, accountName):
        pass

    def commissionReport(self, commissionReport):
        pass

    def contractDetailsEnd(self, reqId):
        pass

    def currentTime(self, time):
        msg = {'type': 'currentTime', 'time': time, 'ts': now()}
        self.msgs.put(msg)

    def deltaNeutralValidation(self, reqId, underComp):
        pass

    def fundamentalData(self, reqId, data):
        pass

    def marketDataType(self, reqId, marketDataType):
        pass

    def realtimeBar(self, reqId, time, open, high, low, close, volume, wap, count):
        msg = {'type': 'realtimeBar', 'reqId': reqId, 'time': time,
               'open': open, 'high': high, 'low': low, 'close': close,
               'volume': volume, 'count': count, 'WAP': WAP, 'ts': now()}
        self.msgs.put(msg)

    def scannerDataEnd(self, reqId):
        msg = {'type': 'scannerDataEnd', 'reqId': reqId}
        self.msgs.put(msg)

    def tickEFP(self, tickerId, tickType, basisPoints, formattedBasisPoints,
                impliedFuture, holdDays, futureExpiry, dividendImpact,
                dividendsToExpiry):
        pass

    def tickSnapshotEnd(self, reqId):
        pass

    def position(self, account, contract, pos, avgCost):
        msg = {'type': 'position', 'account': account, 'contract': contract,
               'pos': pos, 'avgCost': avgCost, 'ts': now()}
        self.msgs.put(msg)

    def positionEnd(self):
        msg = {'type': 'positionEnd', 'ts': now(), 'ts': now()}
        self.msgs.put(msg)

    def accountSummary(self, reqId, account, tag, value, currency):
        pass

    def accountSummaryEnd(self, reqId):
        pass

