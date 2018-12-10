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
	- parameters: data, address::
	-data - data that should be sended through the socket
	-address - (default: broadcast) addresd that udp packet should be send to.
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
	"""
	this function receives the discover info from the worker after and parse it  
	this function returns the data in a list.
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
	this function receives the Discover packet and call the function that collect the relevant information on the worker side. 
	the function returns the information unparsed.
	"""
	ip = "0.0.0.0"
	port = 4444 
	sock = sockTools.create_socket(isTCP = False)
	sock.bind((ip, port))
	information = "discovered:{}".format(sysTools.gatherInformation())
	information = information.encode()
	Discovered = False
	managerAddress = ""
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
			print("Socket timed out, receiving again...")
	return managerAddress

def discoverWorkers(numberOfWorkers):
	currentWorkerNumber = 0
	workersInformation = dict()
	knownClients = []
	while currentWorkerNumber != numberOfWorkers:
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
		time.sleep(5)
	return workersInformation

def updateWorkersInDb(db, workersInformation):
	db.clean_table('hosts')
	for workerId,workerData in workersInformation.items():
		db.insert_to_db("hosts",workerData)
		
			
			
