import sys
sys.path.append('../lib/')
import socket 
import re
import subprocess
import socketLib as sockTools
import system as sysTools

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
	while True:
		data = sock.recvfrom(1024)
		data = str(data)
		if data[0:10] == "discovered":
			information = data.split(":")
			break 
	return information


def receiveDiscoverPacket():
	"""
	this function receives the Discover packet and call the function that collect the relevant information on the worker side. 
	the function returns the information unparsed.
	"""
	ip = "0.0.0.0"
	port = 4444 
	sock = sockTools.create_socket(isTCP = False)
	sock.bind((ip, port))
	information = "discovered:"
	while True:
		data, addr = sock.recvfrom(1024)
		data = str(data) 
		if  (data.find("discover") != -1):
			information += sysTools.gatherInformation()
			sock.sendto(information, (addr, 4444))

def discoverWorkers(numberOfWorkers)
	currentWorkerNumber = 0
	workersInformation = dict()
	while currentWorkerNumber != numberOfWorkers:
		sendUDPPacket("discover")
		workersInformation[currentWorkerNumber] = receiveDiscoverInfo()
		print("Worker number {} discoverd info is {}".format(currentWorkerNumber,workersInformation[currentWorkerNumber]))
		currentNumberOfWorkers+=1