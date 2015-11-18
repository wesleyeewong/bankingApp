import socket
import sys
import argparse
import hashlib
import os

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

done = False

while not done:
	print ('waiting for connection')
	connection, client_address = sock.accept()

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


	# while connection:
	# 	# receiving initial file
	# 	data = connection.recv(1024)
	# 	print ('receiving file binaries')
	# 	# transferDone = False
	# 	# while not transferDone:
	# 	# 	f.write(data)
	# 	# 	print ('file written')
	# 	# 	data = connection.recv(1024)
	# 	# 	if data.decode() == 'EOF':
	# 	# 		transferDone = True
	# 	f.write(data)
	# 	f.close()
	# 	print ('File received')
	# 	file_num += 1