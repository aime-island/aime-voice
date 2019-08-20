import uuid
import os
import wave


def process_file(file):
    fileLocation = os.path.join('./tmp', str(uuid.uuid4()) + '.wav')
    wf = wave.open(fileLocation, 'wb')
    wf.setnchannels(1)
    wf.setsampwidth(2)
    wf.setframerate(16000)
    wf.writeframes(file)
    wf.close()
    return fileLocation