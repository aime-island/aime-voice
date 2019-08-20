import sys
import json

from autobahn.twisted.websocket import WebSocketServerFactory, \
    WebSocketServerProtocol
from autobahn.twisted.resource import WebSocketResource

from twisted.internet import reactor
from twisted.python import log
from twisted.web.server import Site
from twisted.web.static import Data

from utils.model import DeepSpeech
from utils.thread_with_trace import thread_with_trace

from streaming.stream import stream
from streaming.vadaudio import VADAudio

from config import config

ds_small = DeepSpeech(config, 'small_lm')
ds_large = DeepSpeech(config, 'large_lm')

class Stream(WebSocketServerProtocol):


    def onConnect(self, request):
        print("Client connecting: {0}".format(request.peer))
        self.vad_audio = VADAudio(aggressiveness=3,
                            device=None,
                            input_rate=16000)
        self.run_stream = thread_with_trace(
            target=stream,
            args=(ds_small, ds_large, self.vad_audio, self, ))
        self.run_stream.start()

    def onClose(self, wasClean, code, reason):
        print("WebSocket connection closed: {0}".format(reason))
        self.vad_audio = None
        self.run_stream.kill()
        self.run_stream.join()

    # def onMessage(self, payload, isBinary):
    #    lm = json.loads(payload)


if __name__ == '__main__':

    log.startLogging(sys.stdout)

    streamFactory = WebSocketServerFactory()
    streamFactory.protocol = Stream
    streamFactory.startFactory()
    sResource = WebSocketResource(streamFactory)

    # Establish a dummy root resource
    root = Data("", "text/plain")
    root.putChild(b"stream", sResource)

    # both under one Twisted Web Site
    site = Site(root)
    reactor.listenTCP(9000, site)

    reactor.run()
