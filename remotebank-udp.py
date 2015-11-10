import socket
import sys
import argparse
import hashlib

# error codes
ERROR_CODES = ['USER DNE', 'FAILED']

challenge_length = 64
timeout_length = 3
max_retry_count = 3

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

# parsing of arguments, to determine server and port
server_port = server_port.split(":")

server = server_port[0]
port = int(server_port[1])

# creating UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# binding socket to a port
server_address = (server, port)

done = False
user_exists = True
correct_pass = True
retry_count = 0
while not done:
	if debug:
		if retry_count == 0:
			print ('First try')
		else: 
			print ('Retry count: %i' % retry_count)
	try: 
		# sending username for initializing authentication
		print ('Authenticating')
		identification_inquiry = 'IDENTIFICATION ' + user_name
		sent = sock.sendto(identification_inquiry.encode(), server_address)
		if debug:
			print ('Sending username for initializing authentication')
			print ('Sent %s bytes to %s' % (sent, server_address))

		sock.settimeout(timeout_length)
		data, address = sock.recvfrom(4096)

		if data.decode() in ERROR_CODES:
			if debug:
				print ('ERROR: %s' % data.decode())
			print ('Sorry, user does not exist')
			done = True
			break

		else:

			if debug:
				print ('No errors so far, proceed to authenticate using challenge response algo')

			# hashing is done using python's built in hash library (hashlib)
			auth_token = hashlib.md5()
			auth_token.update(user_name.encode())
			auth_token.update(password.encode())
			auth_token.update(data)
			authentication_inquiry = 'AUTHENTICATION ' + auth_token.hexdigest()
			sock.sendto(authentication_inquiry.encode(), server_address)

		sock.settimeout(timeout_length)
		data, address = sock.recvfrom(4096)
		if data.decode() == 'AUTH_SUCCESS':
			print ('Authentication success, welcome %s' % user_name)
			data = 'JUSTDOIT ' + method + " " + amount
			sock.sendto(data.encode(), server_address)

			sock.settimeout(timeout_length)
			data, address = sock.recvfrom(4096)
			data = data.decode()
			data = data.split()
			if data[0] == 'TRANSACTION_SUCCESS':
				print ('Your %s of %s was successful!' % (method, amount))
				print ('Your current account balance is $%s' % data[1])
				done = True

		elif data.decode() == 'AUTHENTICATION FAILED':
			if debug:
				print ('ERROR: %s' % data.decode())
			print ('Sorry, you have entered the wrong password')
			done = True

	except socket.timeout:
		print ('TIMEDOUT')
		retry_count += 1
		if retry_count < max_retry_count and user_exists and correct_pass:
			print ('Attempting to resend information')
		else:
			done = True


	# finally:
	# 	print ('closing socket')
	# 	sock.close()
print ('closing socket')
sock.close()