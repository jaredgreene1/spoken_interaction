import sys
import pyaudio
import speech_recognition as sr
import requests
import pygame
import socketHandler
import vocalize
from parser import parse_args

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
#             vocalize_response(msg)
#
#         for sock in write:
#             pass
#         for sock in error:
#             pass

def get_wake_up_response(robots):
    k = len(robots)
    if k == 1:
        wake_up_response = robots[0] + ", at your service! What can I do?"
    else:
        wake_up_response = "You are commanding the following robots: "
        wake_up_response += robots[0]
        for bot in robots[1:]:
            wake_up_response += ", " + bot
    if k > 3:
        wake_up_response += ". Quite a big group we've got here... "
    return wake_up_response


def play_wakeup(fileName):
    pygame.init()
    pygame.mixer.Sound(fileName).play()

# def vocalize_response(response_text):
#     print "resolving response text: %s" % response_text
#     headers = {
#          'Authorization': 'Bearer d87cfe9b43a74fb19f8ebd01bc7cca12',
#          'Content-Type' : 'application/json: charset=utf-8'
#     }
#     text = {'text': response_text}
#     r = requests.get("https://api.api.ai/v1/tts", params=text, headers=headers)
#     with open("temp.wav", 'wb') as responseAudio:
#         responseAudio.write(r.content)
#
#     play_wakeup('temp.wav')
#     return None
#     p = pyaudio.PyAudio()
#     stream = p.open(format = p.get_format_from_width(r.getsamwidth()),\
#                      channels = r.getnchannels(),
#                      rate = r.getframerate(),
#                      output = True)
#     data = r.readframes(1024)
#     while data != '':
#         stream.write(data)
#         data = r.readframes(1024)
#     stream.close()
#     p.terminate()

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

def build_bot_army(file_name):
    robot_army
    bots = open(file_name, 'r')
    for robot in bots:
        server_ip, server_port, robot_name = [i.strip() for i in robot.split("|")]
        robot_army[robotName] = (server_ip, int(server_port))
    return robot_army

def main():
    #allow multiple robot ip address mappings
    if protocol == 'UDP':
        socket = socketHandler.buildUDPServerSock(response_ip, response_port)
    elif protocol == 'TCP':
        socket = socketHandler.buildTCPClientSock(ip, port)
    try:
        with  sr.Microphone() as source:
            r = sr.Recognizer()
            r.adjust_for_ambient_noise(source)
            r.dynamic_energy_threshold = True
            r.pause_threshold = 0.5

        while True:
            text_from_speech = None
            handle_responses(socket)
            if test:
                key_word_check = raw_input("Who would you like to command? ")
                print key_word_check
            if not test:
                try:
                    audio = r.listen(source)
                    key_word_check = r.recognize_sphinx(audio)
                except LookupError:
                    continue
            print key_word_check
            bots_addressed = [robot_name for robot_name in robot_army.keys() if robot_name in key_word_check]
            print "You're commanding the following robots: "
            print bots_addressed

            if key_word_check == 'exit':
                exit()

            elif bots_addressed:
                wake_up_response = get_wake_up_response(bots_addressed)
                play_text_to_speech(wake_up_response)
                while pygame.mixer.get_busy():
                    pass
                if test:
                    text_from_speech = raw_input("What would you like us to do?\n")
                else:
                    audio = r.listen(source)
                    try:
                        text_from_speech = r.recognize_google(audio)
                    except IndexError:
                        print "No internet connection"
                if text_from_speech:
                    print "google heard: " + text_from_speech
                    if protocol == 'UDP':
                        message = text_from_speech + "|" + response_ip + "|" + str(response_port)
                        print message
                        for bot_name in bots_addressed:
                            severIp, serverPort = robot_army[bot_name]
                            print "Sending command to: %s" % bot_name
                            socketHandler.sendUDPMessage(serverIp, serverPort, message)

                    #TCP HAS NOT BEEN REFACTORED FOR THE ROBOT MAP
                    elif protocol == 'TCP':
                        socket.send(text_from_speech)
    finally:
        if socket:
            socket.close()

if __name__ == '__main__':
        protocol    = 'UDP'
        robot_army  = {}
        cla         = parse_args()
        args        = vars(cla)
        test        = args['test']
        response_ip = args['response_ip']
        response_port = args['response_port']
        if args['single']:
            server_ip, server_port, robot_name = args['single']
            robot_army[robot_name] = (server_ip, server_port)
        elif args['multiple']:
            robot_army = build_bot_army(args['multiple'])
        main()






    # usage = '''OPTIONS:
    # testing -t for entry using commandline (uses voice by default)
    # <clientIp> <clientPort>
    # server {
    #             single server -s <serverIp> <serverPort> [ROBOT_NAME] DEFAULT is steve
    #             OR
    #             multiple servers -m <fileName> which contains serverIp,serverPort,ROBOT_NAME (value separated by commans, entries separated by newlines)
    #         }
    #     '''
    # audio_listener 120.12.3.10 8080 -t  -m robots.txt
    # audio_listener 120.12.3.10 8080     -s 160.21.30.14 9001 steve
    # audio_listener 120.12.3.10 8080 -t  -s 160.21.30.14 9001 steve
    #
    #
    # parser = argparse.ArgumentParser(description='Process some integers.')
    #
    # if len(sys.argv) < 6:
    #     print usage
    #     exit()
    #
    # response_ip = sys.argv[1]
    # response_port = int(sys.argv[2])
    #
    # inc = 3
    # size = len(sys.argv[3:])
    # test = False
    # ROBOT_NAME = "steve"
    #
    # robot_army =
    #
    #
    # while inc < size:
    #     if sys.argv[inc] == '-t':
    #         print "testing mode engaged"
    #         testing = TRUE
    #     if sys.argv[inc] == '-s':
    #         serverIP   = sys.argv[inc + 1]
    #         serverPort = int(sys.argv[inc + 2])
    #         inc += 2
    #         if inc < size:
    #             inc += 1
    #             ROBOT_NAME = sys.argv[inc]
    #             robot_army[ROBOT_NAME] = (serverIp, serverPort)
    #         print "single robot usage: %s | %d | %s " %(serverIp, serverPort, ROBOT_NAME)
    #     elif sys.argv[inc] == "-m":
    #         print "building robot map"
    #         robot_army = buildBotMap(sys.argv[inc+1])
    #     inc += 1
