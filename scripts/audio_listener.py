import sys
import pyaudio
import speech_recognition as sr
import requests
import pygame
import vocalize
import threading
from Queue import Queue
import socket

ROBOT_NAME = "steve"
peer_server_IP = "128.59.15.68"
peer_server_port = 9010

client_IP = "160.39.149.98"
client_port = 7076
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
VALID_TYPES = [
    'SEND',
    'VOCALIZE'
]

class Command:
    def __init__(self, cmd_type, data):

        if cmd_type not in VALID_TYPES:
            raise Exception

        self.cmd_type = cmd_type
        self.data = data

    def __repr__(self):
        return str(self.__dict__)

queue = Queue()

class Listener:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.addr = (host, port)
        self.sock = None

    def start(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(self.addr)

        while True:
            data, addr = self.sock.recvfrom(10000)
            self.handle_data(data)

    def handle_data(self, data):
        cmd = Command('VOCALIZE', data)
        queue.put(cmd)

class Client:
    def __init__(self):
        pass

    def start(self, host, port):
        host = peer_server_IP
        port = peer_server_port
        print("Client targeting ({}:{})".format(host, port))
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("160.39.149.98", 7075))
        while True:
            cmd = queue.get(block=True)
            if cmd.cmd_type == 'SEND':
                print("Trying to send {}".format(cmd.data))
                sock.sendto(cmd.data, (host, port))
                print("Just send {} to ({}:{})".format(cmd.data, host, port))
            elif cmd.cmd_type == 'VOCALIZE':
                print("Trying to vocalize '{}'".format(cmd.data))
                vocalize.play_text_to_speech(cmd.data, filename='test.wav')

def main(test):
    if test:
        while True:
            text_from_speech = raw_input("give me test text: ")
            cmd = Command('VOCALIZE', text_from_speech)
            queue.put(cmd)
        return

    with sr.Microphone() as source:
        r = sr.Recognizer()
        r.adjust_for_ambient_noise(source)
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.5

        while True:
            print("Trying to listen")
            try:
                audio = r.listen(source)
                keyWordCheck = r.recognize_sphinx(audio)
                print(keyWordCheck)
            except LookupError:
                continue

            if keyWordCheck == 'exit':
                break
            if ROBOT_NAME not in keyWordCheck:
                continue

            vocalize.play_wav_file('wakeup.wav')
            while pygame.mixer.get_busy():
                pass

            audio = r.listen(source, 5)
            try:
                textFromSpeech = r.recognize_google(audio)
            except IndexError:
                print "No internet connection"

            if len(textFromSpeech) < 0:
                continue

            message = "{}|{}|{}".format(textFromSpeech,
                client_IP,
                client_port)
            cmd = Command("SEND", message)
            queue.put(cmd)


if __name__ == '__main__':
    test = False
    #allow multiple robot ip address mappings
    if sys.argv[1] == 'test':
        test = True
        peer_server_port = int(sys.argv[2])
    elif len(sys.argv) == 3:
        ROBOT_NAME = sys.argv[1]
        peer_server_port = int(sys.argv[2])
    elif len(sys.argv) == 2:
        ROBOT_NAME = sys.argv[1]

    listener = Listener(client_IP, client_port)
    listener_thread = threading.Thread(target=listener.start)
    listener_thread.daemon = True
    listener_thread.start()

    client = Client()
    print("Peer server is ({}:{})".format(peer_server_IP, peer_server_port))
    client_thread = threading.Thread(target=client.start,
        args=[peer_server_IP, peer_server_port])
    client_thread.daemon = True
    client_thread.start()

    try:
        main(test)
    except KeyboardInterrupt:
        exit()