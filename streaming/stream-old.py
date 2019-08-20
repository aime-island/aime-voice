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


def stream(ds_small, ds_large, vad_audio, ws):
    frames = vad_audio.vad_collector()
    sctxt = ds_large.setupStream()

    prev_output = ''
    output = ''
    counter = 0
    wav_data = bytearray()

    for frame in frames:
        if frame is not None:
            ds_large.feedAudioContent(
                sctxt, np.frombuffer(frame, np.int16))
            wav_data.extend(frame)
            if counter == 8:
                output = ds_large.intermediateDecode(sctxt)
                prev_output = handle_output(prev_output, output, ws)
                counter = 0
            else:
                counter += 1
        else:
            transcript = ds_large.finishStream(sctxt)
            print('transcript: ', transcript)
            obj = {
                'type': 'final',
                'transcript': transcript,
            }
            payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
            ws.sendMessage(payload)

            transcript_stt = stt(ds_small, wav_data)
            print('stt small: ', transcript_stt)
            obj = {
                'type': 'small',
                'transcript': transcript_stt,
            }
            payload = json.dumps(obj, ensure_ascii=False).encode('utf8')
            ws.sendMessage(payload)

            wav_data = bytearray()
            sctxt = ds_large.setupStream()
