import base64
import json
import pyaudio

from ws4py.client.threadedclient import WebSocketClient

class Tal(WebSocketClient):
    def __init__(self, token, anna):

        # Set up Aime socket
        self.anna = anna

        # Set up mic
        self.open_mic()
        self.transcripts = OrderedDict()

        # Initialize Tal socket
        self.uri = 'wss://tal.ru.is/v1/speech:streamingrecognize'
        super(Tal, self).__init__('{}?token={}'.format(self.uri, token))

    def open_mic(self):
        self.pa = pyaudio.PyAudio()
        self.sample_rate = 16000
        self.chunk_size = 800
        config = {
            'format': pyaudio.paInt16,
            'channels': 1,
            'rate': self.sample_rate,
            'input': True,
            'start': False,
            'frames_per_buffer': self.chunk_size,
            'stream_callback': self.stream_callback,
        }
        self.mic = self.pa.open(**config)

    def stream_callback(self, in_data, frame_count, time_info, status):
        b64chunk = base64.b64encode(in_data)
        self.send(json.dumps({'audioContent': b64chunk.decode('utf-8')}))
        return (None, pyaudio.paContinue)
            
    def start_streaming(self):
        self.send(
            json.dumps(
                {
                    'streamingConfig': {
                        'config': {
                            'sampleRate': self.sample_rate,
                            'wordAlignment': False
                        },
                        'interimResults': True
                    }
                }
            )
        )
        self.mic.start_stream()

    def stop_streaming(self):
        self.send(json.dumps({'audioContent': ''}))
        self.mic.stop_stream()

    def opened(self):
        print('Tal socket connected')

    def closed(self, code, reason=None):
        print('Tal socket closed')

    def received_message(self, message):
        response = json.loads(message.data.decode('utf-8'))
        payload = json.dumps(response, ensure_ascii=False).encode('utf8')
        self.anna.sendMessage(payload)