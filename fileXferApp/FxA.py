import socket
import sys
import argparse
import hashlib
import os

from rxp import RxpSocket

download_path = 'client_download/'

# python built in argparser for cmd arg inputs 
parser = argparse.ArgumentParser(description="File transver app")
parser.add_argument('-d', action='store_true', required=False, dest='debug', help='debugging option')
parser.add_argument('client_port_number', action='store', help='the port number which the FxA-client\'s UDP socket should bind to (even number). Please remember that this port number should be equal to the server\'s port number minus 1')
parser.add_argument('netemu_address', action='store', help='the IP address of NetEmu')
parser.add_argument('netemu_port', action='store', help='the UDP port number of NetEmu')

args = parser.parse_args()
debug = args.debug
client_port_number = args.client_port_number
netemu_address = args.netemu_address
netemu_port = args.netemu_port


# end arg parser

if debug: 
	print ('Client port: %s, NetEmu address: %s, NetEmu port: %s' % (client_port_number, netemu_address, netemu_port))

# creating TCP socket, and instantiating server_address to connect to 
sock = RxpSocket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
recv_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
server_address = (netemu_address, int(netemu_port))
#recv_sock.bind(client_port_number)


# connecting to server
def connect():
	if debug:
		print ('Connecting to %s port %s' % server_address)
		print(sock._sock)

	sock.connect(server_address)

# disconnecting the server
def disconnect():
	sock.sendall('CLOSE'.encode())
	if sock.recv(1024).decode() == 'G2C':
		print ('Connection to server closing')
		sock.close()
	else:
		print ('ERROR: unable to close')

def download(file_name):
	sock.sendall('GET'.encode())
	sock.sendall(file_name.encode())

	if sock.recv(1024).decode() == 'FILE_DNE':
		print ('No such file exists')
	else:
		size = int(sock.recv(1024))
		print(size)
		f = open(download_path+file_name, 'wb')
		print ('file opened')

		for x in range (0, size):
			data = sock.recv(1024)
			f.write(data)
			print ('Binaries received')

		f.close()
		print('File received')



def upload(file_name):

	sock.sendall('POST'.encode())
	sock.sendall(file_name.encode())

	statinfo = os.stat(file_name)
	byte_size = statinfo.st_size
	print (byte_size)
	sock.sendall(str(int((byte_size/1024)+1)).encode())

	print ('Opening file')
	f = open(file_name, 'rb')
	print ('Reading file binaries')
	binary = f.read(1024)
	while binary:
		print ('Uploading file')
		sock.sendall(binary)
		binary = f.read(1024)
	print ('Upload complete')



done = False
while not done:
	print ('Waiting for user input...')
	user_input = input('')
	user_input = user_input.split(' ')

	if debug:
		print ('User input is %s. Valid inputs are [connect, get, post, window, disconnect]' % user_input)

	if user_input[0] == 'connect':
		connect()

	elif user_input[0] == 'disconnect':
		disconnect()
		done = True

	elif user_input[0] == 'post':
		if len(user_input) == 1:
			print ('No file entered')
		else: 
			if os.path.exists(user_input[1]):
				upload(user_input[1])
			else:
				print ('No such file exists!!')

	elif user_input[0] == 'get':
		if len(user_input) == 1:
			print ('No file entered')
		else:
			download(user_input[1])

	else:
		print ('Invalid input please try again. Valid inputs are [connect, get, post, window, disconnect]')