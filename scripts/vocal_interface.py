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


def build_mock_response():
    verbalInput = VerbalRequest()
    verbalInput.timestamp  = str(datetime.now())
    verbalInput.phrase      = "Please remember that this is the kitchen"
    verbalInput.action_id   = "navigate_to_landmark"
    kv1                     = KeyValue()
    kv1.key = 'landmark'
    kv1.value = 'table'
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
        command_pub.publish(build_mock_response())
        print "published"
        time.sleep(10)

    # queryInput = raw_input("give me your voice!")
    # payload["query"] = queryInput
    # print payload
    # queryReq = requests.get(query, params=payload)
    # print queryReq.text
