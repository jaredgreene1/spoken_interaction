import socket


def buildUdp(ip, port):
    UDP_IP = ip
    UDP_PORT = port
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind((UDP_IP, UDP_PORT))
    data, addr = sock.recvfrom(1024)
    print "Received: " + data
    print addr
    return data
