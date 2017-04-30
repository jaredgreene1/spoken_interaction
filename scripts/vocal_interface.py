#!/usr/bin/env python
import udpSock
import cherrypy
import pprint
import requests
import rospy
import time
import sys
import json
from std_msgs.msg import String
from spoken_interaction.msg import VerbalRequest, VerbalResponse, KeyValue
from datetime import datetime

from socketHandler import *
from random import choice
from string import ascii_lowercase

generateSessionId   = lambda x: ''.join(choice(ascii_lowercase) for i in range(x))
index1      = lambda lst: [i[0] for i in lst]
BUFFER_SIZE = 4092
protocol = 'UDP'


def sendTCPResponses(socket):
    sock = id(socket)
    if id(socket) in sockToResponse:
        while len(sockToResponse[sock]):
            response = sockToResponse[sock].pop()
            respond(socket, response)

def sendUDPResponses(socket):
#   TODO

def respond(socket, response):
    print "SENING AN AUDIO RESPONSE"
    socket.send(response)

    ##use api.ai to resolve it to a wav file and then send it as a wav. Might want to
    ##do this with async

def addResponse(response):
    ip = response.clientInfo.ip
    port = response.clientInfo.port
    sock = infoToSocks[(ip, port)]
    sockToResponse[id(sock)] = response.verbal_response


def handleQuery(socket):
    print "handle the query!"

    if protocol == 'UDP':
        query, address = socket.recvfrom(BUFFER_SIZE)
    elif protocl == 'TCP':
        query = socket.recv(BUFFER_SIZE)
    print("I heard " + query)
    json_body = {
        'query': [ query ],
        'lang': 'en',
        'sessionId': generateSessionId(36)
    }
    headers = {
        'Authorization': 'Bearer d87cfe9b43a74fb19f8ebd01bc7cca12',
        'Content-Type' : 'application/json: charset=utf-8'
    }
    r = requests.post("https://api.api.ai/v1/query",
             data=json.dumps(json_body), headers=headers)
    processed_query = r.json()
    rosQuery = build_response(processed_query, socksToInfo[id(socket)])
    command_pub.publish(rosQuery)


#Should not be doing custom work on this side for API.AI response params
def build_response(response, sockInfo):
    ret = response['result']
    verbalInput = VerbalRequest()
    verbalInput.timestamp       = str(datetime.now())
    verbalInput.clientInfo.ip   = sockInfo[0]
    verbalInput.clientInfo.port = str(sockInfo[1])
    verbalInput.phrase          = str(ret['source'])
    verbalInput.action_id       = str(ret['action'])
    kv1                         = KeyValue()
    kv2                         = KeyValue()
    if ret['action'] == 'navigate_to_coordinate':
        kv1.key = 'x'
        kv1.value = str(ret['parameters']['coordinate']['x'])
        kv2.key = "y"
        kv2.value = str(ret['parameters']['coordinate']['y'])
        verbalInput.params      = [kv1, kv2]
    elif ret['action'] == 'build_landmark' or ret['action'] == 'navigate_to_landmark':
        kv1.key = 'landmark'
        kv1.value = str(ret['parameters']['landmark'])
        verbalInput.params      = [kv1]
    return verbalInput




if __name__ == "__main__":
    root = "https://api.ai/v1/"
    query = root + "query"

    payload = {
            "clientToken":"d87cfe9b43a74fb19f8ebd01bc7cca12",
            "devToken"    :"4eab53055a564438917c196c9a0bc37e",
            "version"     : "20150910",
            "sessionId"   : generateSessionId(36),
            "lang"        : 'en'
    }

    # Create the node
    rospy.init_node("vocal_request_handler")
    command_pub = rospy.Publisher("verbal_input", VerbalRequest, queue_size = 20)
    #add response subscription here
    response_sub = rospy.Subscriber("verbal_response", VerbalResponse, addResponse)


    # Build the serverSocket and list of open sockets
    socks       = []
    socksToInfo = {}
    infoToSocks = {}
    sockToResponse = {}


    #MULTIPLE CLIENTS USING MULTIPLE PROTOCOL SHOULD BE POSSIBLE! I
    #THINK THE SOCKETS ARE Protocol/IP/Port specific
    if protocol == 'UDP':
        servSock = buildUDPServerSock("128.59.15.68", int(sys.argv[1]))
    elif protocol == 'TCP':
        servSock = buildTCPServerSock("128.59.15.68", int(sys.argv[1])) #This ip/port should be a ROS parameter
        servSock.listen(5)

    try:
        socks.append(servSock)
        print socks
        while True:
            print "checking for action"
            ready_read, ready_write, has_error =\
                    checkForAction(socks,socks, socks)

            for sock in ready_read:
                print "found a message!"
                if sock == socks[0] and protocol == 'TCP': #if serverSock has new client
                    print "it's a new client!"
                    sock, info = sock.accept()
                    socks.append(sock)
                    socksToInfo[id(sock)]  = info
                    infoToSocks[info] = sock
                else:
                    print "it's from an existing connection!"
                    handleQuery(sock)

            for sock in ready_write:
                sendResponses(sock)

            for sock in has_error:
                pass
    finally:
        servSock.close()



#
#
# def build_mock_response(comType, param):
#     verbalInput = VerbalRequest()
#     verbalInput.timestamp  = str(datetime.now())
#     verbalInput.phrase      = "FILLER PHRASE"
#     verbalInput.action_id   = comType
#     kv1                     = KeyValue()
#     kv2                     = KeyValue()
#
#     if comType == "navigate_to_coordinate":
#         kv1.key = "x"
#         kv1.value = param[0]
#         kv2.key = "y"
#         kv2.value = param[1]
#         verbalInput.params      = [kv1, kv2]
#     else:
#         kv1.key = 'landmark'
#         kv1.value = param
#         verbalInput.params      = [kv1]
#     return verbalInput
#
#
#
#
#     command = raw_input("which command? {nav_to_lm=0 | create_lm=1 | nav_to_coord=2 |or just type an action }")
#
#     if command == '0':
#         comType = "navigate_to_landmark"
#         param = raw_input("What is the lm name?")
#     elif command == '1':
#         comType = "build_landmark"
#         param = raw_input("What is the lm name?")
#     elif command == '2':
#         comType = "navigate_to_coordinate"
#         x_c = raw_input("what is the x?")
#         y_c = raw_input("what is the y?")
#         param = (x_c, y_c)
#     else:
#         response = customQuery(command)
#         command_pub.publish(build_response(response))
#        # continue
#     command_pub.publish(build_mock_response(comType, param))
