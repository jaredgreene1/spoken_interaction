import socket


def sendUdp(ip, port):
    sock = socket.socket(socket.AF_INET, # Internet
			 socket.SOCK_DGRAM) # UDP
    sock.sendto(MESSAGE, (ip, port))
    return (sock, (UDP_IP,UDP_PORT)

