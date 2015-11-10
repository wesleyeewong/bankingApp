import socket
import sys
import random
import string
import hashlib
import argparse

timeout_length = 3
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

# dictionary to store the state of each client
# key: server:port
# value: [username, rand_string, auth_success]
state = {}

# create a UDP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

server_address = (address, port)
print ('server starting up on %s port %s' % server_address)
sock.bind(server_address)

# Identifies if the user name client sent is in the system
# If it is return a random challenge string to client
def identify_user(user, client_address):
	if user in user_pass:
		print('User exists, proceed to authentication...')

		if debug:
			print ('Creating random string to be sent to client')

		rand_string = random_string(challenge_length)
		sent = sock.sendto(rand_string.encode(), client_address)

		if debug:
			print ('Random string sent to client')

		print ('Sent %s bytes back to %s' % (sent, client_address))
		client = client_address[0] + ":" + str(client_address[1])
		state[client] = [user, rand_string]
	else: 
		print ('ERROR: User does not exist!')
		sent = sock.sendto(USER_DNE.encode(), client_address)
		print ('Sent %s bytes back to %s' % (sent, client_address))

# Receives the MD5 hash from user and checks it with the server's MD5
# Authenticates the user
def authenticate_user(client_hash, client_address):
	if debug:
		print ('Checking client info: %s on port %s' % client_address)
		print ('Creating md5 hash to be compared to clients md5 hash')
	client = client_address[0] + ":" + str(client_address[1])
	auth_token = hashlib.md5()
	user_name = state[client][0]
	rand_string = state[client][1]
	auth_token.update(user_name.encode())
	auth_token.update(user_pass[user_name].encode())
	auth_token.update(rand_string.encode())

	if client_hash == auth_token.hexdigest():
		print ('Sending authentication success message to client')
		state[client].append('auth_success')
		sent = sock.sendto('AUTH_SUCCESS'.encode(), client_address)
		print ('Sent %s bytes back to %s' % (sent, client_address))
	else: 
		print ('Sending authentication failed message to client')
		state.pop(client)
		sent = sock.sendto(AUTH_FAILED.encode(), client_address)
		print ('Sent %s bytes back to %s' % (sent, client_address))

# Actual transactions 
def just_do_it(method, amount, client_address):
	if debug:
		print ('Checking client info: %s on port %s' % client_address)
		print ('Carry out banking duties')
	client = client_address[0] + ":" + str(client_address[1])
	user_name = state[client][0]
	if method == 'deposit':
		print ('deposit success!')
		user_cred[user_name] += float(amount)
	else:
		print ('withdrawal success!')
		user_cred[user_name] -= float(amount)

	success_message = 'TRANSACTION_SUCCESS ' + str(user_cred[user_name])
	sent = sock.sendto(success_message.encode(), client_address)

while True:
	print ('waiting to receive data...')
	# sock.settimeout(None)
	data, client_address = sock.recvfrom(4096)
	data = data.decode()
	data = data.split()

	# Checks what data is being received and process it accordingly
	if data[0] == 'IDENTIFICATION':
		if debug:
			print ('identifying user')
		identify_user(data[1], client_address)
	if data[0] == 'AUTHENTICATION':
		if debug:
			print ('authenticating user')
		authenticate_user(data[1], client_address)
	if data[0] == 'JUSTDOIT':
		if debug:
			print ('banking user account')
		just_do_it(data[1], data[2], client_address)