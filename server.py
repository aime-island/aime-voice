import sys
import json

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import Data

from utils.thread_with_trace import thread_with_trace
from streaming.stream import Stream


class Anna(WebSocketServerProtocol):


    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.stream = Stream()
        self.run_stream = thread_with_trace(
            target=self.stream.run,
            args=(self, ))
        self.run_stream.start()


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.stream.destroy_self()
        self.stream = None
        self.run_stream.kill()
        self.run_stream.join()


    def onMessage(self, payload, isBinary):
        print("toggled")
        self.stream.toggle_lm()


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    annaFactory = WebSocketServerFactory()
    annaFactory.protocol = Anna
    annaFactory.startFactory()
    aResource = WebSocketResource(annaFactory)

    # Establish a dummy root resource
    root = Data("", "text/plain")
    root.putChild(b"stream", aResource)

    # both under one Twisted Web Site
    site = Site(root)
    reactor.listenTCP(9000, site)

    reactor.run()
