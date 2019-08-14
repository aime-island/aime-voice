import sys
import json

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import Data

from utils.model import create_model
from utils.thread_with_trace import thread_with_trace

from streaming.stream import stream
from streaming.vadaudio import VADAudio


from config import path, \
    settings

ds = create_model(path, settings)


class Model(WebSocketServerProtocol):

    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))

    def onMessage(self, payload, isBinary):
        deep_config = json.loads(payload)
        global ds
        ds = create_model(path, deep_config)

class Stream(WebSocketServerProtocol):


    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.vad_audio = VADAudio(aggressiveness=3,
                            device=None,
                            input_rate=16000)
        self.run_stream = thread_with_trace(
            target=stream,
            args=(ds, self.vad_audio, self, ))
        self.run_stream.start()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.vad_audio = None
        self.run_stream.kill()
        self.run_stream.join()


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    streamFactory = WebSocketServerFactory()
    streamFactory.protocol = Stream
    streamFactory.startFactory()
    sResource = WebSocketResource(streamFactory)

    modelFactory = WebSocketServerFactory()
    modelFactory.protocol = Model
    modelFactory.startFactory()
    mResource = WebSocketResource(modelFactory)

    # Establish a dummy root resource
    root = Data("", "text/plain")
    root.putChild(b"stream", sResource)
    root.putChild(b"model", mResource)

    # both under one Twisted Web Site
    site = Site(root)
    reactor.listenTCP(9000, site)

    reactor.run()
