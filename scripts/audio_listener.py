import sys
import pyaudio
import speech_recognition as sr
import requests
import pygame
import socketHandler

ROBOT_NAME = "steve"
ip = "128.59.15.68"
port = 8080
robots = {}
protocol = 'UDP'

def play_wakeup(fileName):
    pygame.init()
    pygame.mixer.Sound(fileName).play()

def vocalizeResponse(response_text):
    print "resolving response text: %s" % response_text
    headers = {
         'Authorization': 'Bearer d87cfe9b43a74fb19f8ebd01bc7cca12',
         'Content-Type' : 'application/json: charset=utf-8'
    }
    text = {'text': response_text}
    r = requests.get("https://api.api.ai/v1/tts", params=text, headers=headers)
    with open("temp.wav", 'wb') as responseAudio:
        responseAudio.write(r.content)

    play_wakeup('temp.wav')
    return None
    p = pyaudio.PyAudio()
    stream = p.open(format = p.get_format_from_width(r.getsamwidth()),\
                     channels = r.getnchannels(),
                     rate = r.getframerate(),
                     output = True)
    data = r.readframes(1024)
    while data != '':
        stream.write(data)
        data = r.readframes(1024)
    stream.close()
    p.terminate()

def handle_responses():
    if socket:
        read, write, error = socketHandler.checkForAction([socket], [socket], [socket])
        for sock in read:
            if protocol == 'UDP':
                msg, address = sock.recvfrom(4096)
            elif protocol == 'TCP':
                msg = sock.recv(4096)
            print "Heard response: " + msg
            vocalizeResponse(msg)


if __name__ == '__main__':
    #allow multiple robot ip address mappings
    if len(sys.argv) > 3:
        ROBOT_NAME = sys.argv[1]
        ip = sys.argv[2]
    if len(sys.argv) == 3:
        ROBOT_NAME = sys.argv[1]
        port = int(sys.argv[2])
    if len(sys.argv) == 2:
        ROBOT_NAME = sys.argv[1]

    r = sr.Recognizer()
    if protocol == 'UDP':
        socket = None
    elif protocol == 'TCP':
        socket = socketHandler.buildTCPClientSock(ip, port)

    try:
        with  sr.Microphone() as source:
            while True:
                try:
                    audio = r.listen(source)
                    keyWordCheck = r.recognize_sphinx(audio)
                except speech_recognition.UnknownValueError:
                    continue

                print keyWordCheck
                if keyWordCheck == 'exit':
                    break
                elif ROBOT_NAME in keyWordCheck:
                    play_wakeup('wakeup.wav')
                    while pygame.mixer.get_busy():
                        pass
                    audio = r.listen(source)
                    textFromSpeech = r.recognize_google(audio)
                    print "google heard: " + textFromSpeech
                    if textFromSpeech:
                        if protocol == 'UDP':
                            socketHandler.sendUDPMessage(ip, port, textFromSpeech)
                        elif protocol == 'TCP':
                            socket.send(textFromSpeech)
    finally:
        if socket:
            socket.close()
