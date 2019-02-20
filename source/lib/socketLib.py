import sys
sys.path.append('../lib/')
import datetime
import os
import socket
import re

def send_and_encode(sock, data):
	"""This function encode a string to bytes and sends the data through the socket.
	
	Args:
		sock (class): socket to send the data with. 
		data (string): data that should be sent. 
	"""

	encodedData = data.encode()
	sock.send(encodedData)


def create_and_bind_socket(host, port):
	"""This function creates a TCP socket and bind the socket 
	
	Args:
		host (string): host for the socket. 
		port (int): port for the socket. 
	
	Returns:
		[class]: socket handler. 
	"""

	sock = create_socket(isTCP = True)
	sock.bind((host, port))
	return sock


def create_socket(isTCP):
	"""This function creates a socket 
	
	Args:
		isTCP (bool): define if the socket is TCP socket or UDP socket. 
	
	Returns:
		[class]: socket handler.
	"""

	if isTCP:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	else:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(5)
	return sock
	

def recv_and_decode(sock):
	"""This function receives a bytes thorugh socket and decode the bytes back to string.
	
	Args:
		sock (class): socket for receiving the data. 

	Returns:
		[string] - decoded data from the socket.
	"""

	data = sock.recv(1024)
	decodedData = data.decode()
	decodedData = decodedData.strip()
	return decodedData


def receiveFile(sock):
	"""This function is used for receiving a file by a socket.
	
	Args:
		sock (class): socket handler. 
	
	Returns:
		[string]: file name of the received file. 
	"""

	fileName = recv_and_decode(sock)
	print("Saving file, filename is: {}".format(fileName))
	send_and_encode(sock, fileName)
	f = open("jobs/" + fileName, 'wb')
	data = sock.recv(1024)
	while data:
		f.write(data)
		data = sock.recv(1024)
	print("File Transfer completed")
	send_and_encode(sock, "File transfer completed")
	sock.close()
	return fileName


def sendFile(sock, filename, fileFolder = "jobs/"):
	"""This function is used for sending a file through a socket.
	
	Args:
		sock (class): socket handler. 
		filename (string): file name that should be sent.
		fileFolder (str, optional): Defaults to "jobs/". folder to send file from. 
	"""

	realFileLocation = fileFolder + filename
	if not(os.path.isfile(realFileLocation)):
		print("Filename doesn't exists")
	else:	
		send_and_encode(sock, filename)
		response = recv_and_decode(sock)
		with open(realFileLocation, 'rb') as f:
			sock.sendfile(f,0)
	sock.close()