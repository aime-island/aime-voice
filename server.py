import sys
import json

from twisted.python import log
from twisted.internet import reactor
from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol

from utils.thread_with_trace import thread_with_trace
from api.tal import Tal
from config import token

class Anna(WebSocketServerProtocol):
    def __init__(self, *args, **kwargs):
        self.ws = Tal(token, self)
        super(Anna, self).__init__(*args, **kwargs)

    def onConnect(self, request):
        print("Anna connected")
        self.ws.connect()

    def onMessage(self, payload, isBinary):
        payload = json.loads(payload)
        if payload == 'start':
            self.ws.start_streaming()
        elif payload == 'stop':
            self.ws.stop_streaming()

    def onClose(self, wasClean, code, reason):
        print("Anna disconnected")
        self.ws.stop_streaming()
        self.ws.close()

    
if __name__ == '__main__':
    log.startLogging(sys.stdout)

    factory = WebSocketServerFactory()
    factory.protocol = Anna

    reactor.listenTCP(9000, factory)
    reactor.run()