import sys
sys.path.append('../lib/')
import datetime
import os
import socket
import re

def send_and_encode(sock, data):
	encodedData = data.encode()
	sock.send(encodedData)


def create_and_bind_socket(host, port):
	sock = create_socket(isTCP = True)
	sock.bind((host, port))
	return sock


def create_socket(isTCP):
	if isTCP:
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	else:
		sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.settimeout(5)
	return sock
	

def recv_and_decode(sock):
	data = sock.recv(1024)
	decodedData = data.decode()
	decodedData = decodedData.strip()
	return decodedData


def receiveFile(sock):
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
	realFileLocation = fileFolder + filename
	if not(os.path.isfile(realFileLocation)):
		print("Filename doesn't exists")
	else:	
		send_and_encode(sock, filename)
		response = recv_and_decode(sock)
		with open(realFileLocation, 'rb') as f:
			sock.sendfile(f,0)
	sock.close()