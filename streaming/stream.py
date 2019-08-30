from utils.parse import process_file
from streaming.vadaudio import VADAudio
import scipy.io.wavfile as wav
import numpy as np
import os
import json

class Stream(VADAudio):
    
    def __init__(
        self, 
        aggressiveness=3, 
        device=None, 
        input_rate=16000,
        ds_aime=None,
        ds_large=None):

        super().__init__(
            aggressiveness=aggressiveness, 
            device=device, 
            input_rate=input_rate)

        self.ds_aime = ds_aime
        self.ds_large = ds_large

    def stt(self, wav_data):
        filename = process_file(wav_data)
        fs, audio = wav.read(filename)
        transcript = self.ds_aime.stt(audio, fs)
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
    
    def run(self, ws):
        frames = self.vad_collector()
        wav_data = bytearray()
        prev_output = ''
        output = ''
        counter = 0
        self.sctxt = self.ds_large.setupStream()
        
        for frame in frames:
            if frame is not None:
                wav_data.extend(frame)
                self.ds_large.feedAudioContent(
                    self.sctxt, np.frombuffer(frame, np.int16))
                if counter == 8:
                    output = self.ds_large.intermediateDecode(self.sctxt)
                    prev_output = self.handle_output(prev_output, output, ws)
                    counter = 0
                else:
                    counter += 1
            else:
                transcript = self.ds_large.finishStream(self.sctxt)
                print('transcript: ', transcript)
                obj = {
                    'type': 'final',
                    'transcript': transcript,
                }
                payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
                ws.sendMessage(payload)
                transcript_stt = self.stt(wav_data)
                print('aime-lm: ', transcript_stt)
                obj = {
                    'type': 'aime',
                    'transcript': transcript_stt,
                }
                payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
                ws.sendMessage(payload)

                wav_data = bytearray()
                self.sctxt = self.ds_large.setupStream()