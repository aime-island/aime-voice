from ws4py.client.threadedclient import WebSocketClient
import json
import wave
import base64

class Tal(WebSocketClient):

    def __init__(self, *args, **kwargs):
        #self.transcripts = OrderedDict()
        super(Tal, self).__init__(*args, **kwargs)

    def onOpen(self):
        self.send(json.dumps(
                    {'streamingConfig': {'config': {'sampleRate': 16000,# gera ekki hart
                                                    'wordAlignment': False},
                                         'interimResults': False}}))


    def onMessage(self, payload, isBinary):
        print(payload.decode('utf8'))

    def senda(self, wav_data):
        print("We made it")
        with wave.open(wav_data, 'r') as wav:
                chunk_width = 800
                while True:
                    chunk = wav.readframes(chunk_width)
                    if not chunk:
                        break
                    b64chunk = base64.b64encode(chunk)
                    self.send(json.dumps(
                        {'audioContent': b64chunk.decode('utf-8')}))

                self.send(json.dumps({'audioContent': ''}))