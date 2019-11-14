from http.server import BaseHTTPRequestHandler, HTTPServer
from klein import run, route
import socket
import json
import datetime
import time
import threading

LISTEN_PORT = 1313
ALERTS = {}
PAGE_EX = r"./template.html"
PAGE_OUT = r"./pages/"
data = []

def html_page():
    with open(PAGE_EX, 'r') as file:
        copy = file.read()
    # ------------ TIME -------------
    copy = copy.replace(r"%%TIMESTAMP%%", str(time.asctime()), 1)
    # ------------- IN --------------
    tmp = agent_traffic()
    copy = copy.replace(r"%%AGENT_NAMES%%", str([key for key in tmp[0].keys()]), 1)
    copy = copy.replace(r"%%AGENTS_TRAFFIC_IN%%", str([value for value in tmp[0].values()]), 1)
    # ------------- OUT -------------
    copy = copy.replace(r"%%AGENT_NAMES%%", str([key for key in tmp[1].keys()]),1)
    copy = copy.replace(r"%%AGENTS_TRAFFIC_OUT%%", str([value for value in tmp[1].values()]) , 1)
    # ---------- COUNTRIES ----------
    tmp = country_traffic()
    copy = copy.replace(r"%%COUNTRIES_NAMES%%", str([key for key in tmp.keys()]), 1)
    copy = copy.replace(r"%%COUNTRIES_TRAFFIC%%", str([value for value in tmp.values()]), 1)
    # ----------- DSTIP -------------
    tmp = dstip_traffic()
    copy = copy.replace(r"%%IP_ADDERS%%", str([key for key in tmp.keys()]), 1)
    copy = copy.replace(r"%%IPS_VALUES%%", str([value for value in tmp.values()]), 1)
    # ------------ PROG -------------
    tmp = program_traffic()
    copy = copy.replace(r"%%APPS_NAMES%%", str([key for key in tmp.keys()]), 1)
    copy = copy.replace(r"%%APPS_VALUES%%", str([value for value in tmp.values()]), 1)
    # ------------ PORTS ------------
    tmp = port_traffic()
    copy = copy.replace(r"%%PORTS_NUMBERS%%", str([key for key in tmp.keys()]), 1)
    copy = copy.replace(r"%%PORTS_TRAFFIC%%", str([value for value in tmp.values()]), 1)
    # ------------ ALERTS -----------
    copy = copy.replace(r"%%ALERTS%%", str(ALERTS), 1)

    # creating page
    html_name =str(time.asctime()).replace(' ', '-').replace(':', ';')
    with open(PAGE_OUT + html_name + '.html', 'w+') as file:
        file.write(copy)
    # return new file name
    return html_name

# site
@route('/')
def home(request):
    return "XD"

def country_traffic():
    l = {}
    for pack in data:
        if pack["locationIp"] is None:
            continue
        elif pack["locationIp"] not in l:
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
        if pack["prog"] not in l:
            l[pack["prog"]] = pack["sizeOfPacket"]
        else:
            l[pack["prog"]] += pack["sizeOfPacket"]
    return l

def port_traffic():
    l = {}
    for pack in data:
        if pack["remotePort"] not in l:
            l[pack["remotePort"]] = pack["sizeOfPacket"]
        else:
            l[pack["remotePort"]] += pack["sizeOfPacket"]
    return l

def agent_traffic():
    incoming = {}
    outgoing = {}
    # fill
    return incoming, outgoing

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
                packs = self.csocket.recv(1024 * 100).decode()
                data += json.loads(packs)
            except Exception as e:
                print(e)
                break
        ALERTS[self.caddress] = "Disconnected"
        print(str(self.caddress) , "disconnected")

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
        data.clear()

        while len(data) < 200:
            time.sleep(1)
        print("Creating HTML report")
        print("Created: ", html_page())



if __name__ == '__main__':
    main()              
