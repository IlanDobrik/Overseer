from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import json
import datetime
import time
import threading

global LISTEN_PORT,  SETTINGS, INCOMING, OUTGOING, ALERTS
LISTEN_PORT = 1313
SETTINGS = r"C:\Users\magshimim\Desktop\settings.dat"
INCOMING = {}
OUTGOING = {}
ALERTS = []

# site related
class Site(BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200)
		self.wfile.write("Hey", "utf-8")

def run_site():
    hostName = ""
    hostPort = 80

    # running server
    site = HTTPServer((hostName, hostPort), Site)
    print(time.asctime(), "Website Starts - %s:%s" % (hostName, hostPort))
    try:
        site.serve_forever()
    except:
        pass
    
    # closing server
    site.server_close()
    print(time.asctime(), "Website Stops - %s:%s" % (hostName, hostPort))

def alerts(data, worker):
    blacklist = set_blacklist()
    for pack in data:
        if pack['dstIp'] in blacklist:
            pass

def set_blacklist():
    blacklist = {}
    with open(SETTINGS, "r") as file:
        text = file.read()
    text = text[text.find("BLACKLIST = ") + len("BLACKLIST = "):]
    sperated = text.split(",")
    for item in sperated:
        item = item.split(":")
        blacklist[item[0]] = item[1]

    return blacklist

def country_traffic(data):
    dict = {}
    for pack in data:
        if pack["locationIp"] == "None":
            print("ERROR: "+pack)
        if pack["locationIp"] not in dict:
            dict[pack["locationIp"]] = pack["sizeOfPacket"]
        else:
            dict[pack["locationIp"]] += pack["sizeOfPacket"]
    print(dict)

def dstip_traffic(data):
    dict = {}
    for pack in data:
        if pack["dstIp"] not in dict:
            dict[pack["dstIp"]] = pack["sizeOfPacket"]
        else:
            dict[pack["dstIp"]] += pack["sizeOfPacket"]
    print(dict)

def program_traffic(data):
    dict = {}
    for pack in data:
        if pack["program"] not in dict:
            dict[pack["program"]] = pack["sizeOfPacket"]
        else:
            dict[pack["program"]] += pack["sizeOfPacket"]
    print(dict)

def port_traffic(data):
    dict = {}
    for pack in data:
        if pack["remotePort"] not in dict:
            dict[pack["remotePort"]] = pack["sizeOfPacket"]
        else:
            dict[pack["remotePort"]] += pack["sizeOfPacket"]
    print(dict)

def agent_traffic(data, worker):
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

def get_msg():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = ('', LISTEN_PORT)
    sock.bind(server_address)
    client_msg, client_addr = sock.recvfrom(1024 * 10)

    # Closing the socket
    sock.close()
    return client_msg.decode(), client_addr

def main():
    # starting website
    t = threading.Thread(target=run_site, daemon=True)
    t.start()

    while True:
        INCOMING = {}
        OUTGOING = {}
        data = []

        while len(data) < 5:
            client_msg, client_addr = get_msg()
            data += json.loads(client_msg)
            agent_traffic(json.loads(client_msg), client_addr[0])

        print(OUTGOING)
        print(INCOMING)
        #print(data)

if __name__ == '__main__':
    main()
