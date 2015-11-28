import socket
import sys
import argparse
import hashlib
import os
import threading

from rxp import RxpSocket

address = 'localhost'
download_path = 'server_download/'
file_num = 0

parser = argparse.ArgumentParser(description='FxA server')
parser.add_argument('-d', action='store_true', required=False, dest='debug', help='debugging option')
parser.add_argument('server_port_number', action='store', help='the port number which the FxA-server\'s UDP socket should bind to (odd number).')
parser.add_argument('netemu_address', action='store', help='the IP address of NetEmu')
parser.add_argument('netemu_port', action='store', help='the UDP port number of NetEmu')

args = parser.parse_args()
debug = args.debug
server_port_number = args.server_port_number
netemu_address = args.netemu_address
netemu_port = args.netemu_port
# end arg parser

# creating TCP socket
sock = RxpSocket() #socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (address, int(server_port_number))

# binding server to specific port, then listens
sock.bind(server_address)
sock.listen(2)

serverDown = False

# User input functions, will run this on a different thread while the server is receiving connection and such
def user_input():
	global serverDown
	while not serverDown:
		user_input = input('')
		user_input = user_input.split(' ')
		if user_input[0] == 'terminate':
			exit()
		elif user_input[0] == 'w':
			window_size(user_input[1])
		else:
			print ('Invalid command, valid commands are [terminate, w (number)]')

def exit():
	print ('Prepare for server shut down')
	global serverDown
	serverDown = True 

def window_size(w):
	print ('Window size is now %s' % w)
# END user input functions

def download(connection):
	# receiving file name
	file_name = connection.recv(1024).decode()
	print ('file name: %s' % file_name)
	size = int(connection.recv(1024).decode())
	f = open(download_path+file_name, 'wb')
	print ('file opened')

	for x in range (0, size):
		data = connection.recv(1024)
		f.write(data)
		print ('Binaries received')

	f.close()
	print('File received')

def upload(connection):
	# receiving file name
	file_name = connection.recv(1024).decode()

	# getting size of the file 
	if os.path.exists(download_path+file_name):
		connection.sendall('FILE_EXISTS'.encode())
		statinfo = os.stat(download_path+file_name)
		byte_size = statinfo.st_size
		connection.sendall(str(int((byte_size/1024)+1)).encode())
		print ('Opening file')
		f = open(file_name, 'rb')
		print ('Reading file binaries')
		binary = f.read(1024)
		while binary:
			print ('Uploading file')
			connection.sendall(binary)
			print('Reading from file')
			binary = f.read(1024)
		print ('Upload complete')
	else:
		connection.sendall('FILE_DNE'.encode())

def client_closing(connection):
	connection.sendall('G2C'.encode())
	connection.close()
	connection = None
	return connection


def server():
	print ('Server started')
	global serverDown
	connection = None
	while not serverDown:
		if not isinstance(connection, socket.socket) and not isinstance(connection, RxpSocket):
			print ('Waiting for connection')
			connection, client_address = sock.accept()
			print ('Connection accepted')
		else:
			done = serverDown
			while not done:
				try: 
					instruction = connection.recv(1024).decode()
					print ('Instructions: |%s|' % instruction)
					if instruction == 'POST':
						download(connection)
						print ('File received')
					elif instruction == 'GET':
						upload(connection)
						print ('File sent')
					elif instruction == 'CLOSE':
						connection = client_closing(connection)
						print ('Connection closed')
				finally:
					print ('In finally')
					done = True


# starting thread for user_input function
threading.Thread(target=user_input).start()
server()