import requests
from requests.auth import HTTPBasicAuth
import pyaudio
import wave

USER = 'ff0756e5-77ce-4e61-9bba-bb0b21db5261'
PASSWORD = 'PaU87RKmnVOK'
URL = 'https://stream.watsonplatform.net/text-to-speech/api/v1/'

def play_wav_file(filename):
    p = pyaudio.PyAudio()
    f = wave.open(filename, 'rb')
    stream = p.open(format = p.get_format_from_width(f.getsampwidth()),
            channels = f.getnchannels(),
            rate = f.getframerate(),
            output = True)

    data = f.readframes(1024)
    while data:
        stream.write(data)
        data = f.readframes(1024)

    stream.stop_stream()
    stream.close()

    p.terminate()

def make_bluemix_speech_request(text):
    method = 'synthesize'
    params = {
        'accept': 'audio/wav',
        'text': text,
    }
    r = requests.get(URL + method,
        params=params,
        auth=HTTPBasicAuth(USER, PASSWORD))
    return r

def play_text_to_speech(response_text, lock, filename='output.wav', play=True):
    r = make_bluemix_speech_request(response_text)
    with open(filename, 'wb') as handle:
        for block in r.iter_content(1024):
            handle.write(block)
    if play:
        lock.acquire()
        play_wav_file(filename)
        lock.release()

if __name__ == "__main__":
    play_text_to_speech("Go to the kitchen")
