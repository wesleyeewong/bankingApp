Name:	Wesley Wong
E-mail:	wwong30@gatech.edu
CS3251 Section A
9/25/2015
Sockets programming assignment 1

Python version: 3.3.5
OS: Windows 8

Instructions on running program:
	- After obtaining python 3.3.5, open command line and cd to file directory.
	- To run the server, type in 'server-tcp.py [port number]' or 'server-udp.py [port number]' in the command line
	- Similarly, to run the client, type in 'remotebank-tcp.py [server:port] [username] [password] [deposit/withdraw] [amount]'.
	Like wise for remotebank-udp.py
	- '-d' (debugging) option for server and client are available
	- '-h' (help) option is also available

	NOTE: To change server address (not port), you must go into the source code and change it there. Look for server_address,
	it represents a tuple of (string, int) => (address, port).


TCP Client/Server interaction
Client protocol:
	- When running the program from the command line and stating all the arguments, program will automatically parse the
	arguments, and set up the server address, and TCP socket to establish connection. So the only thing to make sure is to
	have the correct server address, port number, and valid username and password.
		NOTE: Server will handle if no such user exists, or invalid password.
	- First thing the server will be expecting to receive is the username. So send the username to the server.
	- After sending the username to the server, the server will then reply with some data. The data received will be either 
	the challenge string for authentication, or error codes.
	- The possible error codes client will receive are 'USER DNE' and 'FAILED'. Check for these 2 error codes before proceeding.
	- If there are no errors, then the data received will be the random challenge string.
	- Server uses built in python hash library (hashlib) to create an md5 checksum. Example how to create one:
		auth_token = hashlib.md5()
	Simple as that!
	- Concatenate the username, password, and challenge string together with that order. NOTE: Do not add any space or characters in between them.
	- Then call .update on the concatenated string. For example:
		auth_token.update(concatenated_string)
	- Send the hexdigest to the server
	- After that, server will be replying with either a 'AUTH_SUCCESS' or 'AUTHENTICATION FAILED'
	- If it is a success you may send a string to determine the amount to deposit or withdraw. Format it as so: '<deposit/withdraw? <amount>'
	- Make sure to have a space between the method and the amount.
	- Server will reply with a string like so 'TRANSACTION_SUCCESS <balance in account>'


UDP Client/Server interaction
Client protocol:
	- When running the program from the command line and stating all the arguments, program will automatically parse the
	arguments, and set up the server address, and UDP socket to establish connection. So the only thing to make sure is to
	have the correct server address, port number, and valid username and password.
		NOTE: Server will handle if no such user exists, or invalid password.
		NOTE: Since this program runs on UDP, we will be responsible for handling errors like drop packages. In my code,
		if the connection is timed out, it'll retry up to a specified amount of times.
	- This UDP server identifies different packages by the prefixed keywords in the package, these keywords are 'IDENTIFICATION',
	'AUTHENTICATION', and 'JUSTDOIT'. We will go into what these keyword mean and when to use it. Format for sending data to 
	the server goes as follows => '<KEYWORD> <data_one> <data_two> <so on...>' NOTE: They are separated by spaces!
	- First things first, the server needs to check if the user exists. This is where 'IDENTIFICATION' comes in, send a message 
	to the server with the keyword 'IDENTIFICATION' plus the username. ex: 'IDENTIFICATION wwong30'
	- Server will then reply with either 'USER DNE' or a challenge string.
	- If there are no errors, then the data received will be the random challenge string.
	- Server uses built in python hash library (hashlib) to create an md5 checksum. Example how to create one:
		auth_token = hashlib.md5()
	Simple as that!
	- Concatenate the username, password, and challenge string together with that order. NOTE: Do not add any space or characters in between them.
	- Then call .update on the concatenated string. For example:
		auth_token.update(concatenated_string)
	- Send the hexdigest to the server with the prefix keyword of 'AUTHENTICATION' => 'AUTHENTICATION <md5 hashed hexdigest>'
	- Server will reply message of either 'AUTH_SUCCESS' or 'AUTHENTICATION FAILED'
	- If success, proceed to send the message 'JUSTDOI <method> <amount>' to the server. It will then process your request.
	- After that, server will reply with a message that looks like 'TRANSACTION_SUCCESS <balance on account>'


Limitations, bugs, etc:
	TCP:
	- I was not able to properly test when multiple clients simultaneously connect to the server.
	- Message size is limited to the fixed receive byte size I set in the code.
	- Only tested the app on localhost, but not on multiple machines.
	- Bank balances can get to as high or as low as you want.

	UDP:
	- May not be able to catch all errors on packet lost or dropped.
	- Time out implementation was not tested extensively.
	- Bank balances can get to as high or as low as you want.
