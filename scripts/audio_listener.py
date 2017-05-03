import requests
import sys
import time
from parser import parse_args
from socket_handler import *

import pyaudio
import speech_recognition as sr
import pocketsphinx.pocketsphinx as ps
import pygame
import vocalize
import threading

AUDIO_LOCK = threading.Lock()
DEFAULT_KW_SENS = .9

def listen(recognizer, source, lock):
    lock.acquire()
    audio = recognizer.listen(source)
    lock.release()
    return audio

def accept_audible_requests(query, recognizer, media):
    bots_addressed = get_bots(query)
    if bots_addressed:
        wake_up_response = get_wake_up_response(bots_addressed)
        vocalize.play_text_to_speech(wake_up_response, AUDIO_LOCK)
        with media as source:
            audio = listen(recognizer, source, AUDIO_LOCK)
        try:
            query = recognizer.recognize_google(audio)
        except IndexError:
            print "No internet connection"
        if query:
            print "REQUEST HEARD: " + query
            if protocol == 'UDP':
                message = query + "|" + response_ip + "|" + str(response_port)
                print message
                for bot_name in bots_addressed:
                    server_ip, server_port = robot_to_info[bot_name]
                    print "Sending command to: %s at %s:%d" % (bot_name, server_ip, server_port)
                    send_udp_message(server_ip, server_port, message)

def run_test():
    query = raw_input("Who would you like to command?")
    bots_addressed = get_bots(query)
    if bots_addressed:
        wake_up_response = get_wake_up_response(bots_addressed)
        vocalize.play_text_to_speech(wake_up_response, AUDIO_LOCK)
        query = raw_input("What do you command?")
        if query.lower() == 'exit':
            exit(0)
        if protocol == 'UDP':
            message = query + "|" + response_ip + "|" + str(response_port)
            print message
            for bot_name in bots_addressed:
                server_ip, server_port = robot_to_info[bot_name]
                print "Sending command to: %s" % bot_name
                send_udp_message(server_ip, server_port, message)

def get_wake_up_response(robots):
    k = len(robots)
    if k == 1:
        wake_up_response = robots[0] + ", at your service! What can I do?"
    else:
        wake_up_response = "You are speaking to the following robots: "
        wake_up_response += robots[0]
        for bot in robots[1:]:
            wake_up_response += ", " + bot
    if k > 3:
        wake_up_response += ". Quite a big group we've got here... "
    return wake_up_response

def get_bots(command_phrase):
    if 'everyone' in command_phrase or 'all' in command_phrase or 'everybody' in command_phrase:
        return robot_to_info.keys()
    else:
        return [robot_name for robot_name in robot_to_info.keys() if robot_name in command_phrase]

def handle_responses(socks):
    if socks:
        read, write, error = check_socks_for_action(socks, socks, socks)
        for sock in read:
            if protocol == 'UDP':
                msg, address = sock.recvfrom(4096)
                response = ip_to_robot[address[0]] + " says " + msg
                print response
            vocalize.play_text_to_speech(response, AUDIO_LOCK)

def response_loop(sockets):
    while True:
        handle_responses([sockets])

def build_bot_army(file_name):
    robot_to_info, ip_to_robot
    bots = open(file_name, 'r')
    for robot in bots:
        server_ip, server_port, robot_name = [i.strip() for i in robot.split("|")]
        robot_to_info[robot_name.lower()] = (server_ip, int(server_port))
        ip_to_robot[server_ip] = robot_name.lower()
        wake_words.append((robot_name, DEFAULT_KW_SENS))
    return robot_to_info, ip_to_robot

def main():
    if protocol == 'UDP':
        socket = build_udp_server_sock(response_ip, response_port)
        response_listener = threading.Thread(target=response_loop, args=([socket]))
        response_listener.daemon = True
        response_listener.start()
    try:
        # Set up audio device and start listening
        m = sr.Microphone()
        r = sr.Recognizer()
        r.dynamic_energy_threshold = True
        r.pause_threshold = 0.3
        r.non_speaking_duration = 0.2
        with m as source:
            AUDIO_LOCK.acquire()
            r.adjust_for_ambient_noise(source)
            AUDIO_LOCK.release()

        while True:
            if not test:
                with m as source:
                    audio = listen(r, source, AUDIO_LOCK)
                print (audio.sample_width)
                print wake_words
                try:

                    result = r.recognize_sphinx(audio_data=audio, keyword_entries=wake_words)
                    print result
                    accept_audible_requests(result, r, m)
                except sr.UnknownValueError:
                    print "uninteligible speech"
                    continue

            else:
                while True:
                    run_test()
    finally:
        socket.close()

if __name__ == '__main__':
    protocol        = 'UDP' # Might want to implment TCP if outside of LAN
    robot_to_info   = {}
    ip_to_robot     = {}
    wake_words      = [('everyone', DEFAULT_KW_SENS),
                       ('all robots',DEFAULT_KW_SENS),
                       ('everybody', DEFAULT_KW_SENS)]
    com_line_args   = parse_args()
    args        = vars(com_line_args)
    test        = args['test']
    response_ip = args['response_ip']
    response_port = int(args['response_port'])
    if args['single']:
        server_ip, server_port, robot_name = args['single']
        robot_to_info[robot_name.lower()] = (server_ip, int(server_port))
        ip_to_robot[server_ip] = robot_name.lower
    elif args['multiple']:
        robot_to_info, ip_to_robot = build_bot_army(args['multiple'])
    main()
