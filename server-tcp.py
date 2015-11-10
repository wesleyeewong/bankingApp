import socket
import sys
import random
import string
import hashlib
import argparse

address = 'localhost'

parser = argparse.ArgumentParser(description='TCP server for bank')
parser.add_argument('-d', action='store_true', required=False, dest='debug', help='debugging option')
parser.add_argument('server_port', action='store', help='port number for server')

args = parser.parse_args()
debug = args.debug
port = int(args.server_port)

# error codes
USER_DNE = "USER DNE"
AUTH_FAILED = "AUTHENTICATION FAILED"

# challenge string length
challenge_length = 64
# function that returns a random string of length [challenge_string]
# string.ascii_letters represents letters a-Z
# string.digits represents 0-9
# string.punctuation represents all the punctuation characters
def random_string(length):
	output = ""
	for x in range(0, length):
		output += random.choice(string.ascii_letters+string.digits+string.punctuation)
	return output

# usernames and passwords stored as python dictionary 
user_pass = {
	"wwong30": "networking101", 
	"wwong33": "networking102", 
	"wwong36": "networking103"
}

# usernames and account credit stored as python dictionary
# NOTE: once server restarts, it'll default back to these values
user_cred = {
	"wwong30": 10.00,
	"wwong33": 15.00,
	"wwong36": 20.00
}

# creating TCP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = (address, port)

# binding server to specific port, then listens
sock.bind(server_address)

sock.listen(2)

while True:
	user = ''
	print ('waiting for a connection')
	connection, client_address = sock.accept()

	try:
		print ('connection from', client_address)
		while True:

			# receiving initial authentication request, should be just the user name
			print ('waiting to receive username...')
			data = connection.recv(64)
			print ('Received! username: "%s"' % data.decode())

			# check if username exists, if not break and close connection
			if data.decode() in user_pass:
				print ('user exists, proceed to authentication...')
				user = data.decode()

				if debug:
					print ('Creating random string to be sent to client')

				rand_string = random_string(challenge_length)
				connection.sendall(rand_string.encode())

				if debug:
					print ('Random string sent to client')

			else:
				print ('ERROR: User does not exist!')
				connection.sendall(USER_DNE.encode())
				break

			if debug:
				print ('Creating md5 hash to be compared to client md5')

			# creating challenge response string using python's built in hash library
			auth_token = hashlib.md5()
			auth_token.update(data)
			auth_token.update(user_pass[data.decode()].encode())
			auth_token.update(rand_string.encode())

			# receiving authentication md5 hash from client
			data = connection.recv(len(auth_token.hexdigest()))
			auth_token_received = data

			# check if hash from client matches hash from server
			if auth_token_received.decode() == auth_token.hexdigest():
				connection.sendall('AUTH_SUCCESS'.encode())


				if debug:
					print ('Carry out banking duties')

				data = connection.recv(64)
				data = data.decode()
				data = data.split()
				if data[0] == 'deposit':
					print ('deposit success!')
					user_cred[user] += float(data[1])
				else:
					print ('withdrawal success!')
					user_cred[user] -= float(data[1])

				success_message = 'TRANSACTION_SUCCESS ' + str(user_cred[user])
				connection.sendall(success_message.encode())

			else: 
				connection.sendall(AUTH_FAILED.encode())
				print ('authentication failed')
	finally:
		print ('closing connection')
		connection.close()
