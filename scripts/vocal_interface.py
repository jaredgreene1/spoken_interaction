#!/usr/bin/env python
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


import argparse

API_AI_CLIENT_ACCESS_TOKEN = 'd87cfe9b43a74fb19f8ebd01bc7cca12'
generate_session_id   = lambda x: ''.join(choice(ascii_lowercase) for i in range(x))
BUFFER_SIZE = 4092

respond_directly = ['domain']

def handle_action_response(response):
    ip = response.clientInfo.ip
    port = response.clientInfo.port
    msg = response.verbal_response
    try:
        respond_to_client(msg, ip, int(port))
    except ValueError:
        rospy.loginfo("Invalid client port number")

def respond_to_client(msg, ip, port):
    if protocol == 'UDP':
        send_udp_message(ip, port, msg)

def read_socket_and_resolve_query(socket):
    if protocol == 'UDP':
        query, client_info = socket.recvfrom(BUFFER_SIZE)
        msg, response_ip, response_port = query.split("|")
        client_info = (response_ip, response_port)
    rospy.loginfo("Verbal Command Received.")
    rospy.loginfo("Client Information:" + str(client_info))
    processed_query = resolve_query_with_api_ai(msg)
    source = str(processed_query['result']['source'])
    process_resolved_query(processed_query, client_info, source)

def process_resolved_query(processed_query, client_info, source):
    response = "I heard your request, thank you!"
    if 'fulfillment' in processed_query['result'] and 'speech' in processed_query[
            'result']['fulfillment']:
        response = processed_query['result']['fulfillment']['speech']
    if source in respond_directly:
        respond_to_client(response, client_info[0], int(client_info[1]))
    else:
        ros_query = build_ros_response(processed_query, client_info)
        command_pub.publish(ros_query)

def resolve_query_with_api_ai(text_to_process):
    authorization = 'Bearer ' + API_AI_CLIENT_ACCESS_TOKEN
    json_body = {
        'query': [ text_to_process ],
        'lang': 'en',
        'sessionId': generate_session_id(36)
        }
    headers = {
        'Authorization': authorization,
        'Content-Type' : 'application/json: charset=utf-8'
        }
    r = requests.post("https://api.api.ai/v1/query",
             data=json.dumps(json_body), headers=headers)

    processed_query = r.json()
    return processed_query

def build_ros_response(response, sockInfo):
    print "building response"
    result     = response['result']
    verbal_req = VerbalRequest()
    verbal_req.timestamp        = str(datetime.now())
    verbal_req.clientInfo.ip    = sockInfo[0]
    verbal_req.clientInfo.port  = str(sockInfo[1])
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
    socks       = []
    if protocol == 'UDP':
        serv_sock = build_udp_server_sock(server_ip_address, server_port_number)
    try:
        socks.append(serv_sock)
        while True:
            ready_read, ready_write, has_error =\
                    check_socks_for_action(socks,socks, socks)
            for sock in ready_read:
                read_socket_and_resolve_query(sock)
            for sock in ready_write:
                pass
            for sock in has_error:
                pass
    finally:
        serv_sock.close()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(dest='server_host', metavar='server-host')
    parser.add_argument(dest='server_port', metavar='server-port', type=int)
    parser.add_argument('-c', '--client-tokens', nargs='*')
    return parser.parse_args()

if __name__ == "__main__":
    #Get commandline args
    args = parse_args()
    server_port_number = args.server_port
    server_ip_address  = args.server_host
    if args.client_tokens:
        API_AI_CLIENT_ACCESS_TOKEN = args.client_tokens
    #Build ROS node and establish sub/pub
    rospy.init_node("vocal_request_handler")
    command_pub = rospy.Publisher("verbal_input", VerbalRequest, queue_size = 20)
    response_sub = rospy.Subscriber("verbal_response", VerbalResponse, handle_action_response)
    protocol = 'UDP'
    main()
