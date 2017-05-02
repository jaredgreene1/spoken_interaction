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
import background_listener
import threading


def run_test():
    query = raw_input("Who would you like to command?")
    bots_addressed = get_bots(query)
    if bots_addressed:
        wake_up_response = get_wake_up_response(bots_addressed)
        query = raw_input("What would you to do?")
        if query.lower() == 'exit':
            exit(0)
        vocalize.play_text_to_speech(wake_up_response)
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
            vocalize.play_text_to_speech(response)

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
    return robot_to_info, ip_to_robot

def main():
    if protocol == 'UDP':
        socket = build_udp_server_sock(response_ip, response_port)
        response_listener = threading.Thread(target=response_loop, args=([socket]))
        response_listener.start()
    try:
        if not test:
            background_listener.background_listening(robot_to_info.keys())
        else:
            while True:
                run_test()

    finally:
        socket.close()

if __name__ == '__main__':
    protocol        = 'UDP' # Might want to implment TCP if outside of LAN
    robot_to_info   = {}
    ip_to_robot     = {}
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
