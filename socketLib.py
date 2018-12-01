import fileManagementLib as fileM
import datetime
import os

def send_and_encode(sock, data):
    encodedData = data.encode()
    sock.send(encodedData)


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
    f = open("clients_jobs/" + storedFileName, 'wb')
    data = sock.recv(2048)
    totalRecv = len(data) 
    f.write(data)
    while totalRecv < int(fileSize):
        data = sock.recv(2048)
        f.write(data)
        totalRecv += len(data) 
    print("File Transfer completed")


def sendFile(sock, filename):
    if os.path.isfile(filename):
        fileSize = os.path.getsize(filename)
        send_and_encode(sock, str(fileSize))
        response = recv_and_decode(sock)
        print(response)
        with open(filename, 'rb') as f:
                bytesToSend = f.read(1024)
                sock.send(bytesToSend)
                while bytesToSend != "":
                    bytesToSend = f.read(1024)
                    sock.send(bytesToSend)
    else:
        print("Filename doesn't exists")
    sock.close()
