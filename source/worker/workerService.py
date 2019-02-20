#!/usr/bin/python
"""
	this class is a service for the worker server.
	this service should run in the background, unless debugging output is needed.
"""
import sys
sys.path.append('../lib/')
import socket
import threading
import socketLib as sockTools
import discover
import databaseLib
import system
import argparse
import traceback
from configparser import ConfigParser

def main():
	"""Main used to parse the arguments and run the service. 
	"""
	config = ConfigParser()
	config.read('config.ini')

	parser = argparse.ArgumentParser(description='Options for running workerService') 
	parser.add_argument('-s', '--server', metavar='ServerIP',
	help="Ip address of the manager (default: from config.ini)")
	parser.add_argument('-p', '--port', metavar='PORT',
	help="Port of the manager (default: from config.ini)")
	parser.add_argument('-d', '--discoverWorker', default=False,action="store_true",
	help="Enable broadcast discover method")
	arguments = parser.parse_args()

	if not arguments.server:
		arguments.server = config.get('server','ip') 
	if not arguments.port:
		arguments.port = int(config.get('server','port'))

	worker = workerService('0.0.0.0', arguments.port)
	if arguments.discoverWorker:
		worker.discoverWorker()
	else:
		worker.discoverWorker(arguments.server)
	worker.listen()


class workerService(object):
	"""
	Arguments:
		host (string) : the host that socket should listen on.
		port (int) : port for the socket.
		 
	this class will create the socket and store it on mySocket variable.
	after running the class user should call listen function for server to start listening.
	"""
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.mySocket = sockTools.create_and_bind_socket(self.host, self.port)
		system.createEnv()

	def discoverWorker(self, managerIP = ""):
		"""This function start the discovering process if managerIP is empty.

		Keyword Arguments:
			managerIP (str, optional): Defaults to "". [description]
		"""

		if not(managerIP):
			print("Starting worker in discovery mode")
			self.managerAddress = discover.receiveDiscoverPacket()
		else:
			self.managerAddress = managerIP
		self.db = databaseLib.DbController(self.managerAddress)


	def listen(self):
		"""
		This function is waiting for incoming connections.
		when a connection arrive to the server socket.
		socket is assigned to this connection and a new thread is created
		so connections could occurs simultaniously.
		then the thread calls listen_to_server function.    
		"""
		self.mySocket.listen(5)
		print("Worker service started")
		while True:
			server_socket, address = self.mySocket.accept()
			threading.Thread(target=self.listen_to_server, args=(server_socket, address)).start()

	def listen_to_server(self, server_socket, address):
		"""
		this functions listen to server waiting to receive new information and act accordingly.
		
		Arguments:
			server_socket (class) : the socket that transfers the server data.
			address (tuple) : server address for filenames and debugging.
			

		Important:
			server can send several words through socket for various functions.

			**sendFile** : when this word is received the worker start receiving the job file.

			**receiveFile** : when this word is received the worker sends the results file to the manager. 
		"""
		while True:
			try:
				data_from_server = sockTools.recv_and_decode(server_socket)
				if data_from_server == "":
					print("{} Disconnected".format(address))
					server_socket.close()
					return False
				if data_from_server == "sendFile":
					self.receive_file_from_server(server_socket, address)
				if data_from_server == "receiveFile":
					self.send_requested_file(server_socket)
			except socket.error:
				print("{} Disconnected".format(address))
				server_socket.close()
				return False

	def receive_file_from_server(self, server_socket, address):
		"""
		this functions receives files from the server by sending the phrase and then start receiving process by calling receive_file method from sockTools library stores fileName and then execute the job.

		Arguments:
			server_socket (class) : the socket that transfers the server data.
			address (tuple) : server address for filenames and debugging.
		"""
		sockTools.send_and_encode(server_socket, "Please send the file")
		fileName = sockTools.receiveFile(server_socket)
		outputFileName = system.run_file(fileName, self.db)

	def send_requested_file(self, server_socket):
		"""This function sends the results file to the manager by receiving the jobID from the manager get the filename from the database and sends the relevant result file.
		
		Arguments:
			server_socket (class): The socket that the results file should be transfer by 
		"""

		sockTools.send_and_encode(server_socket, "going to send Results file")
		requestedJobID = sockTools.recv_and_decode(server_socket)
		requestedFileName = (self.db.get_job_data(requestedJobID, "fileName"))[0]
		filename = "results-" + requestedFileName
		sockTools.sendFile(server_socket, filename)
		server_socket.close()
		

if __name__ == "__main__":
	main()
