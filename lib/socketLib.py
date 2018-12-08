import sys
sys.path.append('../lib/')
import fileManagementLib as fileM
import datetime
import os
import socket

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


def receiveFile(sock, filename):
    fileSize = recv_and_decode(sock)
    send_and_encode(sock, "File size is: " + fileSize + " Bytes "
     + "Tranferring file...")
    currentTime = datetime.datetime.now().strftime("%d-%m-%Y-%X") 
    storedFileName = "[" + filename + "]" + currentTime
    print("Saving file filename is {}".format(storedFileName))
    f = open("jobs/" + storedFileName, 'wb')
    data = sock.recv(2048)
    totalRecv = len(data) 
    f.write(data)
    while totalRecv < int(fileSize):
        data = sock.recv(2048)
        f.write(data)
        totalRecv += len(data) 
    print("File Transfer completed")
    send_and_encode(sock, "File transfer completed")
    return storedFileName


def sendFile(sock, filename):
    if os.path.isfile(filename):
        fileSize = os.path.getsize(filename)
        send_and_encode(sock, str(fileSize))
        response = recv_and_decode(sock)
        print(response)
        with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                while bytesToSend != '':
                    sock.send(bytesToSend) 
        response = recv_and_decode(sock)
        print(response)
    else:
        print("Filename doesn't exists")
    sock.close()

