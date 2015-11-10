import socket
import sys
import argparse
import hashlib

# error codes
ERROR_CODES = ['USER DNE', 'FAILED']

challenge_length = 64

# python built in argument parser for cmd arg inputs
parser = argparse.ArgumentParser(description='TCP Client for bank')
parser.add_argument('-d', action='store_true', required=False, dest='debug', help='debugging option')
parser.add_argument('server_port', action='store', help='server and port as so [server name/ip]:[port number]')
parser.add_argument('user_name', action='store', help='username/login name')
parser.add_argument('password', action='store', help='user password')
parser.add_argument('method', action='store', help='withdraw or deposit')
parser.add_argument('amount', action='store', help='amount to withdraw / deposit')

args = parser.parse_args()
debug = args.debug
server_port = args.server_port
user_name = args.user_name
password = args.password
method = args.method
amount = args.amount
# end arg parser

# debug mode: prints out basic info
if debug:
	print ('server: %s, user: %s, pass: %s, method: %s, amount: $%s' % (server_port, user_name, password, method, amount))

# modification of arguments, to determine server and port
server_port = server_port.split(":")

server = server_port[0]
port = int(server_port[1])

# creating a TCP socket, it's TCP because it's STREAM of data
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (server, port)

# connecting to server
if debug:
	print ('connecting to %s port %s' % server_address)
sock.connect(server_address)

try:
	# sending username for initializing authentication
	print ('Authenticating...')
	if debug:
		print ('Sending username for initializing authentication')
	sock.sendall(user_name.encode())

	data = sock.recv(challenge_length)

	if data.decode() in ERROR_CODES:
		if debug:
			print ('ERROR: %s' % data.decode())
		print('Sorry, user does not exist')

	else:
		if debug:
			print ('No errors so far, proceed to authenticate using challenge response algo')

		# hashing is done using python's built in hash library (hashlib)
		auth_token = hashlib.md5()
		auth_token.update(user_name.encode())
		auth_token.update(password.encode())
		auth_token.update(data)
		sock.sendall(auth_token.hexdigest().encode())


	# checking to see if authentication was success or not, means if user gave the correct password or not
	data = sock.recv(64)
	if data.decode() == "AUTH_SUCCESS":
		print ('Authentication success, welcome %s' % user_name)
		data = method + " " + amount
		sock.sendall(data.encode())

		data = sock.recv(64)
		data = data.decode()
		data = data.split()
		if data[0] == "TRANSACTION_SUCCESS":
			print ('Your %s of %s was successful!' % (method, amount))
			print ('Your current account balance is $%s' % data[1])

	elif data.decode() == "AUTHENTICATION FAILED":
		if debug:
			print ('ERROR: %s' % data.decode())
		print ('Sorry, you have entered the wrong password')

finally:
	sock.close()
