from config import config
from utils.model import DeepSpeech
from utils.parse import process_file
from streaming.vadaudio import VADAudio
import scipy.io.wavfile as wav
import numpy as np
import os
import json
from utils.thread_with_trace import thread_with_trace
from threading import Thread
from streaming.tal import Tal

class Stream(VADAudio):
    
    def __init__(
        self, 
        aggressiveness=3, 
        device=None, 
        input_rate=16000):

        super().__init__(
            aggressiveness=aggressiveness, 
            device=device, 
            input_rate=input_rate)

        #self.ds_aime = DeepSpeech(config, 'small_lm')
        self.ds_large = None

        self.uri = r'wss://tal.ru.is/v1/speech:streamingrecognize'
        self.api_key = 'ak_pjXE41O5LMo76BmQr4p9dgRNAD1KVywLDRwEebPazlYG5XkjqZ0J2vWO8KZDNoqJ'
        self.ws = Tal('{}?token={}'.format(self.uri, self.api_key))
        Thread(target=self.run_tal, args=(self.ws, )).start()
        

    def run_tal(self, ws):
        print(ws)
        ws.connect()
        ws.run()
    """
    def toggle_lm(self):
        if not self.ds_large:
            self.ds_large = DeepSpeech(config, 'large_lm')
        else:
            self.ds_large.__del__()
            self.ds_large = None
            self.sctxt = None
    """ 
    def stt(self, wav_data):
        filename = process_file(wav_data)
        fs, audio = wav.read(filename)
        transcript = self.ds_aime.stt(audio, fs)
        os.remove(filename)
        return transcript

    def tal(self, wav_data):
        filename = process_file(wav_data)
        self.ws.senda(filename)
        os.remove(filename)
        return transcript

    def handle_output(self, prev_output, output, ws):
        if (prev_output != output):
            print('intermediate: ', output)
            prev_output = output
            obj = {
                'type': 'intermediate',
                'transcript': output,
            }
            payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
            ws.sendMessage(payload)
        return prev_output

    def destroy_self(self):
        self.ds_aime.__del__()
        if self.ds_large:
            self.ds_large.__del__()
    
    def run(self, ws):
        frames = self.vad_collector()
        wav_data = bytearray()
        prev_output = ''
        output = ''
        counter = 0
        self.sctxt = None
        if self.ds_large:
            self.sctxt = self.ds_large.setupStream()
        
        for frame in frames:
            if frame is not None:
                wav_data.extend(frame)
                if self.ds_large and self.sctxt:
                    self.ds_large.feedAudioContent(
                        self.sctxt, np.frombuffer(frame, np.int16))
                    if counter == 8:
                        output = self.ds_large.intermediateDecode(self.sctxt)
                        prev_output = self.handle_output(prev_output, output, ws)
                        counter = 0
                    else:
                        counter += 1
            else:
                if self.ds_large and self.sctxt:
                    transcript = self.ds_large.finishStream(self.sctxt)
                    print('transcript: ', transcript)
                    obj = {
                        'type': 'final',
                        'transcript': transcript,
                    }
                    payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
                    ws.sendMessage(payload)
                transcript_stt = self.tal(wav_data)
                #print('aime-lm: ', transcript_stt)
                """
                obj = {
                    'type': 'aime',
                    'transcript': transcript_stt,
                }
                payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
                ws.sendMessage(payload)
                """
                wav_data = bytearray()
                if self.ds_large:
                    self.sctxt = self.ds_large.setupStream()