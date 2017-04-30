import sys
import pyaudio
import speech_recognition as sr
import requests
import pygame
import socketHandler
import vocalize

ROBOT_NAME = "steve"
serverIp = "128.59.15.68"
serverPort = 8080

responseIP = "160.39.10.232"
responsePort = 7070
robots = {}
protocol = 'UDP'


# # For async... someday
# class responseHandler(threading.Thread):
#     def __init__(self):
#         threading.Thread.__init__(self)
#     def run(self):
#         print "Starting response handler"
#     while True:
#         read, write, error = socketHandler.checkForAction(rcvSocks, sndSocks, [])
#         for sock in read:
#             if protocol == 'UDP':
#                 msg, address = sock.recvfrom(4096)
#             elif protocol == 'TCP':
#                 msg = sock.recv(4096)
#             print "Heard response: " + msg
#             vocalizeResponse(msg)
#
#         for sock in write:
#             pass
#         for sock in error:
#             pass






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

def handle_responses(socks):
    if socks:
        read, write, error = socketHandler.checkForAction([socks], [socks], [socks])
        for sock in read:
            if protocol == 'UDP':
                msg, address = sock.recvfrom(4096)
            elif protocol == 'TCP':
                msg = sock.recv(4096)
            print "Heard response: " + msg
            vocalize.play_text_to_speech(msg)


if __name__ == '__main__':
    test = False
    #allow multiple robot ip address mappings
    if sys.argv[1] == 'test':
        test = True
        print "testing"
        serverPort = int(sys.argv[2])
    elif len(sys.argv) == 3:
        ROBOT_NAME = sys.argv[1]
        port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        ROBOT_NAME = sys.argv[1]

    if protocol == 'UDP':
        socket = socketHandler.buildUDPServerSock(responseIP, responsePort)
    elif protocol == 'TCP':
        socket = socketHandler.buildTCPClientSock(ip, port)

    try:
        with  sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.5


            while True:
                textFromSpeech = None
                handle_responses(socket)
                if not test:

                    try:
                        audio = r.listen(source)
                        keyWordCheck = r.recognize_sphinx(audio)
                    except LookupError:
                        continue

                    print keyWordCheck
                    if keyWordCheck == 'exit':
                        break
                    elif ROBOT_NAME in keyWordCheck:
                        play_wakeup('wakeup.wav')
                        while pygame.mixer.get_busy():
                            pass
                        audio = r.listen(source, 5)
                        try:
                            textFromSpeech = r.recognize_google(audio)
                        except IndexError:
                            print "No internet connection"
                else:
                    textFromSpeech = raw_input("give me test text")


                if textFromSpeech:
                    print "google heard: " + textFromSpeech
                    if protocol == 'UDP':
                        message = textFromSpeech + "|" + responseIP + "|" + str(responsePort)
                        print message
                        result = socketHandler.sendUDPMessage(serverIp, serverPort, message)
                        print result
                    elif protocol == 'TCP':
                        socket.send(textFromSpeech)
    finally:
        if socket:
            socket.close()
