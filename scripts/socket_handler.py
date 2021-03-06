import select
import socket


def build_tcp_client_sock(ip, port):
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((ip,port))
	return s


def build_tcp_sever_sock(ip, port):
	ss = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	ss.bind((ip, port))
	return ss


def check_socks_for_action(senders, receivers, both, timeout=60):
	ready_to_read, ready_to_write, in_error = \
			select.select(senders, receivers, both, timeout)
	return ready_to_read, ready_to_write, in_error

def send_udp_message(ip, port, message):
    address = (ip,port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sent = sock.sendto(message, address)
    #sock.recvfrom(4096)
    return sent
    sock.close()

def build_udp_server_sock(ip, port):
    address = (ip,port)
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(address)
    return sock
