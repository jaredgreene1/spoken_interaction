import sys
import pyaudio
import speech_recognition as sr
import pygame
import socketHandler

ROBOT_NAME = "steve"
ip = "128.59.15.68"
port = 8080
robots = {}


def play_wakeup():
    pygame.init()
    pygame.mixer.Sound('wakeup.wav').play()



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
    socket = socketHandler.buildTCPClientSock(ip, port)

    with  sr.Microphone() as source:
        print "1"
        while True:
            print "while"
            read, write, error = socketHandler.checkForAction([socket], [socket], [socket])
            print "2"
            for socks in read:
                print "got a message here!"
                msg = socks.recv(100000000)
            print "listen"
            audio = r.listen(source)
            user = r.recognize_sphinx(audio)
            print user
            if user == 'exit':
                break
            elif ROBOT_NAME in user:
                play_wakeup()
                while pygame.mixer.get_busy():
                    pass
                audio = r.listen(source)
                textFromSpeech = r.recognize_google(audio)
                print "google heard: " + textFromSpeech
                if textFromSpeech:
                    socket.send(textFromSpeech)

