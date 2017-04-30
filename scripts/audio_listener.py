import pyaudio
import wave
import sys
import speech_recognition as sr
import udpSender
import pygame

WAKE_UP_WORD = "steve"

def play_wakeup():
    pygame.init()
    pygame.mixer.Sound('wakeup.wav').play()



if __name__ == '__main__':
    r = sr.Recognizer()
    ip = "128.59.15.68"
    port = 8080
    udpClient = udpSender.buildClient(ip, port, user)

    with  sr.Microphone() as source:
        while True:
            audio = r.listen(source)
            user = r.recognize_sphinx(audio)
            print user
            if user == 'exit':
                break
            elif WAKE_UP_WORD in user:
                play_wakeup()
                while pygame.mixer.get_busy():
                    pass
                audio = r.listen(source)
                user = r.recognize_google(audio)
                print "google heard: " + user

