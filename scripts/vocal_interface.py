#!/usr/bin/env python

import requests
import rospy
import time
from std_msgs.msg import String
from spoken_interaction.msg import VerbalRequest, VerbalResponse, KeyValue
from datetime import datetime

from random import choice
from string import ascii_lowercase

generateSessionId = lambda x: ''.join(choice(ascii_lowercase) for i in range(x))


def build_mock_response(comType, param):
    verbalInput = VerbalRequest()
    verbalInput.timestamp  = str(datetime.now())
    verbalInput.phrase      = "FILLER PHRASE"
    verbalInput.action_id   = comType 
    kv1                     = KeyValue()
    kv2                     = KeyValue()
    
    if comType == "coord_nav":
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
            "lang"        : 'en',
            "verify"      :'false'
    }

    # Create a node
    rospy.init_node("vocal_request_handler")
    command_pub = rospy.Publisher("verbal_input", VerbalRequest, queue_size = 20)
    print "fire"
    while True:
        command = raw_input("which command? {nav_to_lm=0 | create_lm=1 | nav_to_coord=2}")
        if command == '0':
            comType = "navigate_to_landmark"
            param = raw_input("What is the lm name?")
        elif command == '1':
            comType = "create_landmark"
            param = raw_input("What is the lm name?")
        elif command == '2':
            comType = "coord_nav"
            x_c = raw_input("what is the x?")
            y_c = raw_input("what is the y?")
            param = (x_c, y_c) 
        else:
            continue
        command_pub.publish(build_mock_response(comType, param))
        print "published"
        time.sleep(1)

    # queryInput = raw_input("give me your voice!")
    # payload["query"] = queryInput
    # print payload
    # queryReq = requests.get(query, params=payload)
    # print queryReq.text
