import socket
import sys
import argparse
import hashlib
import os
import threading

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
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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

# starting thread for user_input function
threading.Thread(target=user_input).start()

while not serverDown:

	if serverDown:
		print ('serverDown boolean is True')
	print ('Server started')
	print ('waiting for connection')
	connection, client_address = sock.accept()

	done = False

	while not done:

		try:
			file_name = connection.recv(1024).decode()
			size = int(connection.recv(1024).decode())
			f = open(download_path+file_name, 'wb')
			print ('file opened')
			for x in range(0,size):
				data = connection.recv(1024)
				f.write(data)
				print ('Binaries received')

			f.close()
			print('File received')
		except socket.error:
			print ('No data to receive yet')

		finally:
			done = True
			# connection.close()