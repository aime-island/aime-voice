from config import config
from utils.parse import process_file
import scipy.io.wavfile as wav
import numpy as np
import os
import json


def handle_output(prev_output, output, ws):
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


def stt(ds, wav_data):
    filename = process_file(wav_data)
    fs, audio = wav.read(filename)
    stt = ds.stt(audio, fs)
    os.remove(filename)
    return stt


def stream(ds, vad_audio, ws):
    frames = vad_audio.vad_collector()
    wav_data = bytearray()

    for frame in frames:
        if frame is not None:
            wav_data.extend(frame)
        else:
            transcript_stt = stt(ds, wav_data)
            print('aime-lm: ', transcript_stt)
            obj = {
                'type': 'aime',
                'transcript': transcript_stt,
            }
            payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
            ws.sendMessage(payload)

            wav_data = bytearray()