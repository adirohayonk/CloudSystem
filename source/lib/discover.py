import sys
sys.path.append('../lib/')
import socket 
import re
import subprocess
import socketLib as sockTools
import system as sysTools
import databaseLib
import time

def sendUDPPacket(data, address = None):
	"""
	this function sends simple UDPPacket to specific address or broadcast address by default with data specified by:
	creating a socket using create socket method, extracting broadcast address if needed and than send the message to the address.

	Arguments:
		data (string): data that should be sended through the socket
		address (string): (default: broadcast) addresd that udp packet should be send to.
	"""
	sock = sockTools.create_socket(isTCP = False)
	#extracting broadcast address
	if not address:
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
		unparsedIpOutput = subprocess.check_output(["ip", "a"])
		splitted = re.findall( r'brd [\d.-]+ scope', str(unparsedIpOutput))
		broadCastAddress = splitted[0].split()[1]
		address = broadCastAddress
	port = 4444
	data = data.encode()
	sock.sendto(data, (address, port))


def receiveDiscoverInfo():
	"""This function receives the discover info from the worker and parse it.
	
	Returns:
		(list, tuple): tuple with machine information and address. 
	"""

	ip = "0.0.0.0"
	port = 4444
	sock = sockTools.create_socket(isTCP = False)
	sock.bind((ip, port))
	informationList = list() 
	while True:
		try:
			data, addr = sock.recvfrom(1024)
			data = data.decode()
			if data[0:10] == "discovered":
				informationList = data.split(":")
				informationList = informationList[1:]
				break
		except socket.timeout:
			return None, None
	return informationList, addr


def receiveDiscoverPacket():
	"""
	this function receives the Discover packet and call the function that collect the relevant information the information transferred to the manager address. 

	Returns:
		[tuple]: manager address
	"""
	ip = "0.0.0.0"
	port = 4444 
	sock = sockTools.create_socket(isTCP = False)
	sock.bind((ip, port))
	information = "discovered:{}".format(sysTools.gatherInformation())
	information = information.encode()
	Discovered = False
	managerAddress = str() 
	while not Discovered:
		try:
			data, addr = sock.recvfrom(1024)
			data = str(data) 
			if  (data.find("discover") != -1):
				sock.sendto(information, (addr[0], 4444))
			if  (data.find(sysTools.getSystemIp()) != -1):
				print("Worker Discovered")
				managerAddress = addr[0]
				Discovered = True	
		except socket.timeout:
			Discovered = False
	return managerAddress

def discoverWorkers(numberOfWorkers):
	"""This function keep sending the discover packet in intervals of 5 sec until all workers are discovered
	
	Arguments:
		numberOfWorkers (int): Number of workers that should be discovered. 
	
	Returns:
		[dict]: All workers information. 
	"""

	currentWorkerNumber = 0
	workersInformation = dict()
	knownClients = []
	print("Starting discover process search for {} workers".format(numberOfWorkers))
	while currentWorkerNumber < int(numberOfWorkers):
		sendUDPPacket("discover")
		information, addr = receiveDiscoverInfo()	
		if information:
			if addr[0] in knownClients:
				sendUDPPacket("{} Discovered")
			else:
				workersInformation[currentWorkerNumber] = information 
				print("{} discoverd info is {}".format(information[0],information))
				sendUDPPacket("{} Discovered".format(str(addr)),addr[0])
				currentWorkerNumber+=1
				knownClients.append(addr[0])
		time.sleep(2)
	return workersInformation

def updateWorkersInDb(db, workersInformation):
	"""This function update workers information in the database.
	
	Arguments:
		db (class): handler for database used for database operations  
		workersInformation (dict): All the workers information. 
	"""

	db.clean_table('hosts')
	for workerId,workerData in workersInformation.items():
		db.insert_to_db("hosts",workerData)