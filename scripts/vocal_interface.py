#!/usr/bin/env python
import udpSock
import cherrypy
import pprint
import requests
import rospy
import time
import json
from std_msgs.msg import String
from spoken_interaction.msg import VerbalRequest, VerbalResponse, KeyValue
from datetime import datetime

from random import choice
from string import ascii_lowercase

generateSessionId = lambda x: ''.join(choice(ascii_lowercase) for i in range(x))

def customQuery(query):
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
    return processed_query

def build_response(response):
    ret = response['result']
    verbalInput = VerbalRequest()
    verbalInput.timestamp  = str(datetime.now())
    verbalInput.phrase      = str(ret['source']) 
    verbalInput.action_id   = str(ret['action']) 
    kv1                     = KeyValue() 
    kv2                     = KeyValue()
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

def build_mock_response(comType, param):
    verbalInput = VerbalRequest()
    verbalInput.timestamp  = str(datetime.now())
    verbalInput.phrase      = "FILLER PHRASE"
    verbalInput.action_id   = comType 
    kv1                     = KeyValue()
    kv2                     = KeyValue()
    
    if comType == "navigate_to_coordinate":
        kv1.key = "x"
        kv1.value = param[0] 
        kv2.key = "y"
        kv2.value = param[1]
        verbalInput.params      = [kv1, kv2]
    else:
        kv1.key = 'landmark'
        kv1.value = param
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

    # Create a node
    rospy.init_node("vocal_request_handler")
    command_pub = rospy.Publisher("verbal_input", VerbalRequest, queue_size = 20)
    while True:
        query = udpSock.buildUdp("128.59.15.68", 8080)
        print "I hear: " + query
        response = customQuery(query)
        command_pub.publish(build_response(response))

    command = raw_input("which command? {nav_to_lm=0 | create_lm=1 | nav_to_coord=2 |or just type an action }")
    
    if command == '0':
        comType = "navigate_to_landmark"
        param = raw_input("What is the lm name?")
    elif command == '1':
        comType = "build_landmark"
        param = raw_input("What is the lm name?")
    elif command == '2':
        comType = "navigate_to_coordinate"
        x_c = raw_input("what is the x?")
        y_c = raw_input("what is the y?")
        param = (x_c, y_c) 
    else:
        response = customQuery(command)
        command_pub.publish(build_response(response))
       # continue
    command_pub.publish(build_mock_response(comType, param))
