import os
import socket
import json
import time
import threading
import subprocess

# global variables
ALERTS = {}
INCOMING = {}
OUTGOING = {}
data = []
# config
LISTEN_PORT = 1313
SNIFF_COUNT = 200
PAGES_FOLDER = r"./reports/"


def html_page():
    with open(r"./templates/template.html", 'r') as file:
        copy = file.read()

    save = [INCOMING, OUTGOING]
    # ------------ TIME -------------
    copy = copy.replace(r"``TIME``", str(time.asctime()), 1)
    # ------------- IN --------------
    copy = copy.replace(r"``AGENT_NAMES``", str([key for key in INCOMING.keys()]), 1)
    copy = copy.replace(r"``AGENT_TRAFFIC_IN``", str([value for value in INCOMING.values()]), 1)
    # ------------- OUT -------------
    copy = copy.replace(r"``AGENT_NAMES``", str([key for key in OUTGOING.keys()]),1)
    copy = copy.replace(r"``AGENT_TRAFFIC_OUT``", str([value for value in OUTGOING.values()]) , 1)
    # ---------- COUNTRIES ----------
    save.append(country_traffic())
    copy = copy.replace(r"``COUNTRIES_NAMES``", str([key for key in save[-1].keys()][:5]), 1)
    copy = copy.replace(r"``COUNTRIES_TRAFFIC``", str([value for value in save[-1].values()][:5]), 1)
    # ----------- DSTIP -------------
    save.append(dstip_traffic())
    copy = copy.replace(r"``IP_ADDERS``", str([key for key in save[-1].keys()][:5]), 1)
    copy = copy.replace(r"``IPS_VALUES``", str([value for value in save[-1].values()][:5]), 1)
    # ------------ PROG -------------
    save.append(program_traffic())
    copy = copy.replace(r"``APPS_NAMES``", str([key for key in save[-1].keys()]), 1)
    copy = copy.replace(r"``APPS_VALUES``", str([value for value in save[-1].values()]), 1)
    # ------------ PORTS ------------
    save.append(port_traffic())
    copy = copy.replace(r"``PORTS_NUMBERS``", str([key for key in save[-1].keys()][:5]), 1)
    copy = copy.replace(r"``PORTS_TRAFFIC``", str([value for value in save[-1].values()][:5]), 1)
    # ------------ ALERTS -----------
    copy = copy.replace(r"``ALERTS``", str(ALERTS), 1)

    # getting DB
    with open("DB.dat", "r") as file:
        db = json.loads(file.read())
    
    html_name = "Test"#str(time.asctime()).replace(' ', '-').replace(':', ';')    
    db.update({html_name: save})

    # writing results back to file
    with open("DB.dat", "w") as file:
        file.write(json.dumps(db))

    # creating page
    with open(PAGES_FOLDER + html_name + '.html', 'w+') as file:
        file.write(copy)

    return html_name

def country_traffic():
    l = {}
    for pack in data:
        if pack["locationIp"] is None:
            continue
        else:
            l.update({pack["locationIp"]:pack["sizeOfPacket"]})
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
    # issue ?
    l = {}
    for pack in data:
        if pack["remotePort"] not in l:
            l[pack["remotePort"]] = pack["sizeOfPacket"]
        else:
            l[pack["remotePort"]] += pack["sizeOfPacket"]
    return l

class ClientThread(threading.Thread):
    def __init__(self, clientAddress, clientsocket):
        threading.Thread.__init__(self, daemon=True)
        self.csocket = clientsocket
        self.caddress = clientAddress

    def run(self):
        global data, INCOMING, OUTGOING
        INCOMING[self.caddress[0]] = 0
        OUTGOING[self.caddress[0]] = 0
        print (self.caddress, "connected")

        while True:
            try:   
                # receiving data and adding it to data  
                packs = self.csocket.recv(1024 * 100).decode()
                data += json.loads(packs)

                # filling INCOMING and OUTGOING data size for each user
                for pack in json.loads(packs):
                    if pack['outOrIn']:
                        OUTGOING[self.caddress[0]] += pack['sizeOfPacket']
                    else:
                        INCOMING[self.caddress[0]] += pack['sizeOfPacket']
            except Exception as e:
                break
        
        # if agent disconnects, it will break the while loop.
        # notifying in ALERTS
        ALERTS[self.caddress] = "Disconnected"
        INCOMING.pop(self.caddress[0], None)
        OUTGOING.pop(self.caddress[0], None)
        print(self.caddress , "disconnected")

def listen4clients():
    # creating listen socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('', LISTEN_PORT))
    print("Server started")

    # creating client sockets    
    while True:
        server.listen(1)
        clientsock, clientAddress = server.accept()
        newthread = ClientThread(clientAddress, clientsock)
        newthread.start()

def main():
    t = threading.Thread(target=listen4clients, daemon=True)
    t.start()

    while True:
        data.clear()

        while len(data) < SNIFF_COUNT:
            time.sleep(1)
        print("Received {} packets".format(len(data)))
        print("Created: ", html_page())

if __name__ == '__main__':
    
    site = subprocess.Popen(r'python ./website.py ' + PAGES_FOLDER) # starting up the site
    try:
        main() # running main
    except KeyboardInterrupt:
        site.kill() # if main was manually closed due to KeyboardInterrupt. closing site
