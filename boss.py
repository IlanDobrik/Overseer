from http.server import BaseHTTPRequestHandler, HTTPServer
from klein import run, route
import socket
import json
import datetime
import time
import threading

LISTEN_PORT = 1313
SETTINGS = r"C:\Users\magshimim\Desktop\settings.dat"
INCOMING = {}
OUTGOING = {}
data = []

# site related
@route('/')
def home(request):
    return "XD"

def country_traffic():
    dict = {}
    for pack in data:
        if pack["locationIp"] == "None":
            print("ERROR: "+pack)
        if pack["locationIp"] not in dict:
            dict[pack["locationIp"]] = pack["sizeOfPacket"]
        else:
            dict[pack["locationIp"]] += pack["sizeOfPacket"]
    print(dict)

def dstip_traffic():
    dict = {}
    for pack in data:
        if pack["dstIp"] not in dict:
            dict[pack["dstIp"]] = pack["sizeOfPacket"]
        else:
            dict[pack["dstIp"]] += pack["sizeOfPacket"]
    print(dict)

def program_traffic():
    dict = {}
    for pack in data:
        if pack["program"] not in dict:
            dict[pack["program"]] = pack["sizeOfPacket"]
        else:
            dict[pack["program"]] += pack["sizeOfPacket"]
    print(dict)

def port_traffic():
    dict = {}
    for pack in data:
        if pack["remotePort"] not in dict:
            dict[pack["remotePort"]] = pack["sizeOfPacket"]
        else:
            dict[pack["remotePort"]] += pack["sizeOfPacket"]
    print(dict)

def agent_traffic(worker):
    byte_sum = 0
    for pack in data:
        if pack["outOrIn"]:
            byte_sum += pack["sizeOfPacket"]
    if worker not in OUTGOING:
        OUTGOING[worker] = byte_sum
    else:
        OUTGOING[worker] += byte_sum
    byte_sum = 0
    for pack in data:
        if not pack["outOrIn"]:
           byte_sum += pack["sizeOfPacket"]
    if worker not in INCOMING:
        INCOMING[worker] = byte_sum
    else:
        INCOMING[worker] += byte_sum

def get_msg_UDP():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', LISTEN_PORT)
    sock.bind(server_address)
    client_msg, client_addr = sock.recvfrom(1024)

    # Closing the socket
    sock.close()
    return client_msg.decode(), client_addr

class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self)
        self.csocket = clientsocket
        self.caddress = clientAddress

    def run(self):
        global data
        print (self.caddress, "connected")

        while True:
            try:     
                packs = self.csocket.recv(2048).decode()
                data += json.loads(packs)
            except Exception as e:
                print(e)
                break
        print (self.caddress , "disconnected")

def listen4clients():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', LISTEN_PORT))
    print("Server started")
    
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()

def main():
    #run("localhost", 80)
    t = threading.Thread(target=listen4clients, daemon=True)
    t.start()

    while True:
        INCOMING.clear()
        OUTGOING.clear()
        data.clear()

        while len(data) < 5:
            time.sleep(1)
        print("Writing")
        with open("./output.txt", 'w') as f:
            f.write(json.dumps(data))
        #upload to site    

if __name__ == '__main__':
    main()
