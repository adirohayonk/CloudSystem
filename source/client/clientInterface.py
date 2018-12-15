#!/usr/bin/python
"""
This Interface used by the client in order to receive jobs results send the job files, receive results file and add new worker.
"""
import sys
sys.path.append('../lib/')
import socket
import sys
import socketLib as sockTools
import argparse
import databaseLib
import prettytable
import time
import system
import subprocess
from configparser import ConfigParser


def main():
	"""Main used to parse the arguments and call the relevant method accordingly. 
	"""
	config = ConfigParser()
	config.read('config.ini')

	parser = argparse.ArgumentParser(description='Provides many options for controlling and managing jobs on CloudSystem.') 
	parser.add_argument('-f', '--file', metavar='[File]',
		help="File name contains the script to upload to the server")
	parser.add_argument('-n', '--newWorker', default=False, action="store_true",
		help="Add this machine as a new worker")
	parser.add_argument('-l', '--listOfJobs', default=False, 
	action="store_true",
		help="Receive list of status jobs from the manager")
	parser.add_argument('-j', '--jobInfo', metavar='JobID',
		help="Receive job information for specific job")
	parser.add_argument('-st', '--status', metavar='STATUS',
		help="configure specific status for listOfJobs")
	parser.add_argument('-s', '--server', metavar='ServerIP',
		help="Ip address of the manager (default: from config.ini)")
	parser.add_argument('-p', '--port', metavar='PORT',
		help="Port of the manager (default: from config.ini)")
	parser.add_argument('-g', '--getResults', metavar='JobID',
		help="get job result file")
	arguments = parser.parse_args()

	if not arguments.server:
		arguments.server = config.get('server','ip') 
	if not arguments.port:
		arguments.port = int(config.get('server','port'))

	if arguments.listOfJobs or arguments.jobInfo:
		db = databaseLib.DbController(arguments.server) #get controller for the db
		pp = prettytable.PrettyTable(["JobID", "fileName", "hostname", "status"])
	else:
		sock = create_manager_connection(arguments)

	if arguments.listOfJobs:
		print_list_of_jobs(arguments, db, pp)
	elif arguments.jobInfo:
		jobData = db.get_job_data(arguments.jobInfo)
		pp.add_row(jobData)
		print(pp)
	elif arguments.newWorker:
		add_new_worker(sock)
	elif arguments.file:
		send_file_to_server(arguments, sock)
	elif arguments.getResults:
		get_results_file(sock, arguments)

	if 'sock' in locals():
		sock.close()


def add_new_worker(sock):
	"""This function adds the specific machine that uses it as a new worker by sending newWorker message to server than pass the information and run the workerservice.
	
	Args:
		sock (class): The socket that used for transferring the messages and information. 
	
	Raises:
		SystemExit: Raises when the user wants to become a worker than the service replace the interface. 
	"""
	
	sockTools.send_and_encode(sock, "newWorker")
	workerInformation = system.gatherInformation()
	sockTools.send_and_encode(sock, workerInformation)
	response = sockTools.recv_and_decode(sock)
	print(response)
	if response[:3] == "new":
			print("Running worker service")
			try:
					subprocess.call(["python","../worker/workerService.py"])
					raise SystemExit()
			except KeyboardInterrupt:
					print("Quit")


def create_manager_connection(arguments):
	"""This function creates a connection to the server.
	
	Args:
		arguments (dict): all arguments from command line. 
	
	Returns:
		[class]: Socket handler. 
	"""

	sock = sockTools.create_socket(isTCP = True)
	sock.connect((arguments.server, arguments.port))
	return sock


def get_results_file(sock, arguments):
	"""This function request the results file from the server prompt the user for the downloading and store the results file in jobs folder.
	
	Args:
		sock (class): socket that file should be transfer on. 
		arguments (dict): all arguments from the command line. 
	"""

	sockTools.send_and_encode(sock, "receiveResults")
	response = sockTools.recv_and_decode(sock)
	if response[:6] == "please":
			sockTools.send_and_encode(sock, arguments.getResults)
	response = sockTools.recv_and_decode(sock)
	print(response)
	a = input()
	if a[:1] == "y":
			sockTools.send_and_encode(sock, a)
			sockTools.receiveFile(sock)


def print_list_of_jobs(arguments, db, pp):
	"""This function print list of jobs based on status if no status specified prints the entiere list.
	
	Args:
		arguments (dict): All arguments from command line. 
		db (class): db class handler for database operations. 
		pp (class): pretty print handler for printing results. 
	"""

	if not arguments.status:
			jobData = db.get_jobs_data("status")
	else:
			jobData = db.get_jobs_data("'{}'".format(arguments.status))
	for data in jobData:
			pp.add_row(data)
	print(pp)


def send_file_to_server(arguments, sock):
	"""This function sends the file to the server.
	
	Args:
		arguments (dict): All arguments from command line. 
		sock (class): socket that file should be transfer on. 
	"""

	print("Sending {} to manager: {}"
			.format(arguments.file, arguments.server))
	sockTools.send_and_encode(sock, "sendFile")
	jobID = sockTools.recv_and_decode(sock)
	print("Your jobID is {}".format(jobID))
	sockTools.sendFile(sock, arguments.file, "./")


if __name__ == "__main__":
	main()