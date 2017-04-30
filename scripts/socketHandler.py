import select
import socket


def buildTCPClientSock(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip,port))
	return s


def buildTCPServerSock(ip, port):
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.bind((ip, port))
	return ss


def checkForAction(senders, receivers, both, timeout=60):
	ready_to_read, ready_to_write, in_error = \
			select.select(senders, receivers, both, timeout)
	return ready_to_read, ready_to_write, in_error

def sendUDPMessage(ip, port, message):
    address = (ip,port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(message, address)
    #sock.recvfrom(4096)
    return sent
    sock.close()

def buildUDPServerSock(ip, port):
    address = (ip,port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address)
    return sock
