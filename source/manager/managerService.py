#!/usr/bin/python
"""
	this class is a service for the manager server.
	this service should run in the background, unless debugging output is needed.
"""	
import sys
sys.path.append('../lib/')
import socket
import threading
import socketLib as sockTools
import discover
import system
import databaseLib
import operator
import traceback
import os
import argparse

def main():
	"""Main used to parse the arguments and run the service. 
	"""
	parser = argparse.ArgumentParser(description='Options for running managerService') 
	parser.add_argument('-d', '--discoverWorkers', default=False,action="store_true",
	help="Enable broadcast discover method")
	parser.add_argument('-p', '--port', metavar='PORT', default=4444,
	help="Port of the system (default: 4444)")
	parser.add_argument('-n', '--numberOfWorkers', metavar='NUM', 
	help="Number of workers that should be discovered")
	arguments = parser.parse_args()


	manager = managerService('0.0.0.0', arguments.port)
	manager.setupWorkersData(arguments)
	manager.listen()


class managerService(object):
	"""
	Arguments:
		host (str) : the host that socket should listen on.
		port (int) : port for the socket.
		 
	this class will create the socket and store it on mySocket variable.
	after running the class user should call listen function for server to start listening.
	"""
	def __init__(self, host, port):
		self.host = host
		self.port = port
		self.mySocket = sockTools.create_and_bind_socket(self.host, self.port)
		self.db = databaseLib.DbController(system.getSystemIp()) #get controller for the db
		self.currentJobID = self.db.get_next_jobid()
		system.createEnv() #create environment folders
		
	def setupWorkersData(self, arguments):
		"""This function start the discover process if arguments.discoverWorkers in on.
		if so the function will take the number of workers that should be discovered from the arguments as well.
		if discoverWorkers is off workers data will be collected from the database.

		Arguments:
			arguments (dict) : command line arguments 

		"""

		if arguments.discoverWorkers:
			if not(arguments.numberOfWorkers):
				print("Please provide how many workers should be discovered?")
				exit(1)
			workersInformation = discover.discoverWorkers(arguments.numberOfWorkers) #get workers information 
			discover.updateWorkersInDb(self.db,workersInformation)
		self.workersList = self.db.get_workers_list() #store workers list for local use
		self.numberOfWorkers = len(self.workersList)


	def listen(self):
		"""
		This function is waiting for incoming connections.
		when a connection arrive to the server socket.
		socket is assigned to this connection and a new thread is created so connections could occurs simultaniously.
		then the thread calls listen_to_client function.
		
		"""
		self.mySocket.listen(5)
		print("Manager service started")
		while True:
			client_socket, address = self.mySocket.accept() #accept on incoming connetion
			threading.Thread(target=self.listen_to_client, args=(client_socket, address)).start() # creating new thread for the connection 

	def listen_to_client(self, client_socket, address):
		"""
		This function listen to client waiting to receive new information and act accordingly.

		Arguments:
			client_socket (class) : the socket that transfers the client data.
			address (tuple) : client address for filenames and debugging.
		 
		Important:
			client/workers can sends several words through socket for various functions.

			**sendFile** : when this word is received the manager start receiving the job file.

			**newWorker** : when this word is received the manager calls the udpPacket methods and worker will send the discover packet.

			**receiveResults** : when this word is received the manager sends the results file to the client.
		"""
		action = True
		while action:
			try:
				data_from_client = sockTools.recv_and_decode(client_socket) #recv message from client
				if data_from_client == "":
					print("{} Disconnected".format(address))
					client_socket.close()
					return False
				if data_from_client == "sendFile":
					self.receive_file_from_client(client_socket, address)
				if data_from_client == "newWorker":
					self.add_new_worker(client_socket, address)
				if data_from_client == "receiveResults":
					self.receive_results(client_socket)
				action = False
			except socket.error:
				print("{} Disconnected".format(address))
				print(traceback.format_exc())
				client_socket.close()
				return False

	def receive_file_from_client(self, client_socket, address):
		"""
		This function receives files from the client/worker by sending the phrase and then start receiving process by calling receive_file method from sockTools library.

		Arguments:
			client_socket (class) : the socket that transfers the client data.
			address (tuple): client address for filenames and debugging.
		 """
		sockTools.send_and_encode(client_socket, str(self.currentJobID))
		fileName = sockTools.receiveFile(client_socket) #receive the file from client 
		nextFreeWorker = self.evaluteWorkers() #find the worker with least jobs
		newFileName = str(self.currentJobID) + "." + fileName
		os.rename("jobs/" + fileName, "jobs/" + newFileName) 
		self.writeJobToDB(newFileName, nextFreeWorker)
		self.send_file_to_worker(nextFreeWorker, newFileName)

	def writeJobToDB(self, filename, hostname):
		"""This function writes the job data to the database by storing relevant info in list and call insert_to_db on this list.
		
		Args:
			filename (string): fileName of the job.
			hostname (string): hostname that runs the job. 
		"""

		jobData = [self.currentJobID, filename, hostname, "ACCEPTED"] 
		self.db.insert_to_db("jobs", jobData) 
		self.currentJobID += 1

	def send_file_to_worker(self, workerHostname, filename):
		"""This function resolves the worker ip and then open a socket between the manager and the worker and send the file to the worker.
		
		Arguments:
			workerHostname (string): The hostname of the worker that should run the job 
			filename (string): fileName of the job. 
		"""

		workerIP = (self.db.get_host_data(workerHostname, "ipaddr"))[0] 
		print("\nSelected {} ,worker ip is: {}".format(workerHostname, workerIP))
		print("Sending job file to {}".format(workerHostname))
		worker_socket = sockTools.create_socket(isTCP = True) 
		worker_socket.connect((workerIP, 4444))
		sockTools.send_and_encode(worker_socket,"sendFile")	
		response = sockTools.recv_and_decode(worker_socket)
		sockTools.sendFile(worker_socket, filename) #send the file to worker

	def add_new_worker(self, client_socket, address):
		"""
		this function add new worker to the system and to the database if worker already exists the function sends an ERROR"

		Arguments:
			client_socket (class) : the socket that transfers the client data. 
		"""
		print("New worker request accepted")
		sockTools.send_and_encode(client_socket, "please send your info")
		newWorkerInformation = sockTools.recv_and_decode(client_socket)
		workerInformationList = newWorkerInformation.split(":")
		print("New worker information is: {}".format(workerInformationList))
		dbResult = self.db.get_host_data_by_ip(address[0])	
		if dbResult:
			sockTools.send_and_encode(client_socket,"{} is already a worker".format(address[0]))
		else:
			self.db.insert_to_db('hosts', workerInformationList)
			sockTools.send_and_encode(client_socket,"new worker has been added info is:{}".format(workerInformationList))
			self.workersList = self.db.get_workers_list() #store workers list for local use
			self.numberOfWorkers += 1
		

	def receive_results(self, client_socket):
		"""This function sends the results file to the client by receiving the jobID from the client get the worker ip that runs this job create a connection to this worker download the results file and send it to the client
		
		Args:
			client_socket (class): socket of the client that request the results file. 
		"""

		sockTools.send_and_encode(client_socket, "please provide job ID")
		requestedJobID = sockTools.recv_and_decode(client_socket)
		jobStatus = (self.db.get_job_data(requestedJobID, "status"))[0]
		if jobStatus not in ["COMPLETED", "ERROR"]:
			sockTools.send_and_encode(client_socket,"Your job is still in progress")
		else:
			worker_socket = sockTools.create_socket(isTCP = True) 
			workerHostname = (self.db.get_job_data(requestedJobID,"hostname"))[0]	
			workerIP = (self.db.get_host_data(workerHostname, "ipaddr"))[0] 
			worker_socket.connect((workerIP, 4444))
			sockTools.send_and_encode(worker_socket, "receiveFile")
			response = sockTools.recv_and_decode(worker_socket)
			if response[:5] == "going":
				sockTools.send_and_encode(worker_socket, requestedJobID)
			resultsFile = sockTools.receiveFile(worker_socket)
			if jobStatus == "ERROR":
				sockTools.send_and_encode(client_socket,"You job has failed do you want to download err log(y/n)")	
				response = sockTools.recv_and_decode(client_socket)
			else:
				sockTools.send_and_encode(client_socket, "Are you ready to download the results file(y/n)")
				response = sockTools.recv_and_decode(client_socket)
			print("Going to send {} to client".format(resultsFile))
			if response[:1] == "y":
				sockTools.sendFile(client_socket, resultsFile)
		
		
	def evaluteWorkers(self):
		""" This function finds the worker with least jobs by collection all jobs information and evalutae the number of IN-PROGRESS jobs for each worker and than order that list.
		
		Returns:
			[String] : most available worker 
		"""

		workersJobsNum = dict() #workers jobs number will by stored in dictionary
		print("Number of jobs for each worker:")
		for worker in self.workersList:
			workerJobsInProg = self.db.get_worker_jobs(worker, 'IN-PROGRESS') #get only IN-PROGRESS jobs from db
			workersJobsNum[worker] = len(workerJobsInProg) #store number of jobs
			print("{} - {}".format(worker,workersJobsNum[worker]),end=",")
		workersJobsNum = sorted(workersJobsNum.items(), key = lambda kv: kv[1])# sort workers by number of jobs
		nextFreeWorker = workersJobsNum[0][0] # store the worker with least jobs
		return nextFreeWorker


if __name__ == "__main__":
	main()