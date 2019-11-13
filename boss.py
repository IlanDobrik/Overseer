from http.server import BaseHTTPRequestHandler, HTTPServer
from klein import run, route
import socket
import json
import datetime
import time
import threading

LISTEN_PORT = 1313
INCOMING = {}
OUTGOING = {}
ALERTS = {}
PAGE_EX = r"./template.html"
PAGE_OUT = r"./pages/"
data = []

def html_page():
    with open(PAGE_EX, 'r') as file:
        copy = file.read()
    # ------------ TIME -------------
    copy.replace("%%TIMESTAMP%%", str(time.asctime()), 1)
    # ------------- IN --------------
    copy.replace("%%AGENT_NAMES%%", str(INCOMING.keys()), 1)
    copy.replace("%%AGENTS_TRAFFIC_IN%%", str(INCOMING.values()), 1)
    # ------------- OUT -------------
    copy.replace("%%AGENT_NAMES%%", str(OUTGOING.keys()),1)
    copy.replace("%%AGENTS_TRAFFIC_OUT%%", str(OUTGOING.values()) , 1)
    # ---------- COUNTRIES ----------
    copy.replace("%%COUNTRIES_NAMES%%", country_traffic().keys(), 1)
    copy.replace("%%COUNTRIES_TRAFFIC%%", country_traffic().values(), 1)
    # ----------- DSTIP -------------
    copy.replace("%%IP_ADDERS%%", dstip_traffic().keys() , 1)
    copy.replace("%%IPS_VALUES%%", dstip_traffic().values() , 1)
    # ------------ PROG -------------
    copy.replace("%%APPS_NAMES%%", program_traffic().keys(), 1)
    copy.replace("%%APPS_VALUES%%", program_traffic().values(), 1)
    # ------------ PORTS ------------
    copy.replace("%%PORTS_NUMBERS%%", port_traffic().keys(), 1)
    copy.replace("%%PORTS_TRAFFIC%%", program_traffic().values(), 1)
    # ------------ ALERTS -----------
    copy.replace("%%ALERTS%%", str(ALERTS), 1)
    with open(PAGE_OUT + str(time.asctime()), 'w') as file:
        file.write(copy)

# site
@route('/')
def home(request):
    return "XD"

def country_traffic():
    l = {}
    for pack in data:
        if pack["locationIp"] == "None":
            print("ERROR: "+pack)
        if pack["locationIp"] not in l:
            l[pack["locationIp"]] = pack["sizeOfPacket"]
        else:
            l[pack["locationIp"]] += pack["sizeOfPacket"]
    return l

def dstip_traffic():
    l = {}
    for pack in data:
        if pack["dstIp"] not in l:
            l[pack["dstIp"]] = pack["sizeOfPacket"]
        else:
            l[pack["dstIp"]] += pack["sizeOfPacket"]
    return l

def program_traffic():
    l = {}
    for pack in data:
        if pack["program"] not in l:
            l[pack["program"]] = pack["sizeOfPacket"]
        else:
            l[pack["program"]] += pack["sizeOfPacket"]
    return l

def port_traffic():
    l = {}
    for pack in data:
        if pack["remotePort"] not in l:
            l[pack["remotePort"]] = pack["sizeOfPacket"]
        else:
            l[pack["remotePort"]] += pack["sizeOfPacket"]
    return l

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
        ALERTS[self.caddress] = "Disconnected"
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
        html_page()

if __name__ == '__main__':
    main()
