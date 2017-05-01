#!/usr/bin/env python
import pprint
import requests
import rospy
import time
import sys
import json
from std_msgs.msg import String
from spoken_interaction.msg import VerbalRequest, VerbalResponse, KeyValue
from datetime import datetime
from socket_handler import *
from random import choice
from string import ascii_lowercase

API_AI_CLIENT_ACCESS_TOKEN = 'd87cfe9b43a74fb19f8ebd01bc7cca12'
generate_session_id   = lambda x: ''.join(choice(ascii_lowercase) for i in range(x))
index1      = lambda lst: [i[0] for i in lst]
BUFFER_SIZE = 4092
protocol = 'UDP'

def handle_response(response):
    ip = response.client_info.ip
    port = response.client_info.port
    msg = response.verbal_response
    if protocol == 'UDP':
        sendUDPMessage(ip, int(port), msg)

def handle_query(socket):
    #TODO add a logger out here
    if protocol == 'UDP':
        query, client_info = socket.recvfrom(BUFFER_SIZE)
        msg, response_ip, response_port = query.split("|")
        client_info = (response_ip, response_port)
    processed_query = resolve_query_with_api_ai(query, API_AI_CLIENT_ACCESS_TOKEN)
    ros_query = build_response(processed_query, client_info)
    command_pub.publish(ros_query)

def resolve_query_with_api_ai(text_to_process, api_id):
    authorization = 'Bearer ' + api_id
    json_body = {
        'query': [ text_to_process ],
        'lang': 'en',
        'sessionId': generate_session_id(36)
    headers = {
        'Authorization': authorization
        'Content-Type' : 'application/json: charset=utf-8'}
    r = requests.post("https://api.api.ai/v1/query",
             data=json.dumps(json_body), headers=headers)
    return processed_query = r.json()

def build_response(response, sockInfo):
    result      = response['result']
    verbal_req = VerbalRequest()
    verbal_req.timestamp        = str(datetime.now())
    verbal_req.client_info.ip   = sockInfo[0]
    verbal_req.client_info.port = str(sockInfo[1])
    verbal_req.phrase           = str(result['source'])
    verbal_req.action_id        = str(result['action'])
    parameter_keys = result['parameters'].keys()
    parameters = []
    for key in parameter_keys:
        new_param       = KeyValue()
        new_param.key   = str(key)
        new_param.value = str(result['parameters'][key])
        parameters.append(new_param)
    verbal_req.parameters = parameters
    return verbal_req

def main():
    rospy.init_node("vocal_request_handler")
    command_pub = rospy.Publisher("verbal_input", VerbalRequest, queue_size = 20)
    response_sub = rospy.Subscriber("verbal_response", VerbalResponse, handle_response)
    socks       = []

    if protocol == 'UDP':
        servSock = build_udp_server_sock(server_ip_address, server_port_number))
    try:
        socks.append(servSock)
        while True:
            ready_read, ready_write, has_error =\
                    check_socks_for_action(socks,socks, socks)
            for sock in ready_read:
                handleQuery(sock)
            for sock in ready_write:
                pass
            for sock in has_error:
                pass
    finally:
        servSock.close()

if __name__ == "__main__":
    server_port_number = sys.argv[1]
    server_ip_address  = sys.argv[2]
    main()
