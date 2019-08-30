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

from config import config
from utils.model import DeepSpeech

ds_aime = DeepSpeech(config, 'small_lm')
ds_large = DeepSpeech(config, 'large_lm')

class Anna(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.stream = Stream(ds_aime=ds_aime, ds_large=ds_large)
        
        self.run_stream = thread_with_trace(
            target=self.stream.run,
            args=(self, ))
        self.run_stream.start()


    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.stream = None
        self.run_stream.kill()
        self.run_stream.join()


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
