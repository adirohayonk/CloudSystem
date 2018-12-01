def send_and_encode(data, sock):
    encodedData = data.encode()
    sock.send(encodedData)


def recv_and_decode(sock):
    data = sock.recv(1024)
    decodedData = data.decode()
    decodedData = decodedData.strip()
    return decodedData


def receive_file(sock, filename):
    if filename != 'q':
        send_and_encode(filename, sock)
        data = recv_and_decode(sock)
        if data[:6] == 'EXISTS':
            filesize = data[6:]
            message = input("File Exists, " + str(filesize)+"Bytes, download? (Y/N)? ->")
            if message == 'y':
                send_and_encode("OK", sock)
                f = open('new_'+filename, 'wb')
                data = sock.recv(1024)
                totalRecv = len(data)
                f.write(data)
                while totalRecv < int(filesize):
                    data = sock.recv(1024)
                    totalRecv += len(data.decode())
                    f.write(data)
                    print("{0:.2f}".format((totalRecv/float(filesize))*100)+" %Done")
                print("Download Complete!")
        else:
            print("File does not Exist!")
    sock.close()
