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

