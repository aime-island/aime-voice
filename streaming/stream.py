from streaming.vadaudio import VADAudio
import numpy as np
import json


def stream(model, vad_audio, ws):
    frames = vad_audio.vad_collector()
    sctxt = model.setupStream()
    prev_output = ''
    output = ''
    output_inter = {
        'type': 'intermediate',
        'transcript': ''
    }
    output_final = {
        'type': 'final',
        'transcript': ''
    }
    counter = 0
    for frame in frames:
        if frame is not None:
            model.feedAudioContent(
                sctxt, np.frombuffer(frame, np.int16))
            if counter == 4:
                output = model.intermediateDecode(sctxt)
                if (prev_output != output):
                    print(output)
                    output_inter['transcript'] = output
                    payload = json.dumps(output_inter, ensure_ascii=False).encode('utf8')
                    ws.sendMessage(payload)
                    prev_output = output
                counter = 0
            else:
                counter += 1
        else:
            text = model.finishStream(sctxt)
            print('transcript:', text)
            output_final['transcript'] = text
            payload = json.dumps(output_final, ensure_ascii=False).encode('utf8')
            ws.sendMessage(payload)
            sctxt = model.setupStream()