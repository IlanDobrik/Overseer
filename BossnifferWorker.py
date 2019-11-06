#from scapy3k.all import *
#from scapy3k.layers.inet import IP, TCP, UDP
import sys
import json
import requests
import socket
import os
import re
from scapy.all import *
import time

# is this working?

#  text = json.dumps(data) - encodes
#  data = json.loads(text) - decodes

global summery_packets, LOCAL_IP, SERVER_ADDR, SERVER_PORT
summery_packets = []
LOCAL_IP = ""
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 1313


def spy(packet):
    return IP in packet and (TCP in packet or UDP in packet)

def set_globals():
    msg = IP(dst="8.8.8.8")
    LOCAL_IP = msg[IP].src

    for arg in sys.argv:
        # searching for port
        if type(arg) is int and 0 < arg < 65536:
            SERVER_PORT = arg
        # searching for server address
        else:
            result = re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", arg)  
            if type(arg) is str and result:
                SERVER_ADDR = result.group()



def checked_before(IP):
    # checking if IP has been checked before by the geo-location service
    # to reduce traffic
    for pack in summery_packets:
        if pack["dstIp"] == IP:
            return pack["locationIp"]

def get_location(IP):
    # cant show geo-location if ip is invalid
    if "192.168." in IP or "10." in IP:
        return "Private Network"

    # sending request to a geo-location service that returns a json
    checked = checked_before(IP)
    if not checked:
        response = requests.get("http://ip-api.com/json/"+IP)
        data = json.loads(response.text)
        if "country" in data:
            return data["country"]
        else:
            return "ERROR"

def send_data(msg):
    # Create a non-specific UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (SERVER_ADDR, SERVER_PORT)
    sock.connect(server_address)

    sock.sendto(msg.encode(), server_address)

    sock.close()

def get_program():
    # Returning dir of port-to-program from os
    ''' !!! Requires administrator rights !!! '''
    string = os.popen('netstat -nb').read()

    rx = re.compile(r'\[([^\[\]]+)\]')
    apps = [m.group(1) for m in rx.finditer(string)]

    rx = re.compile(r':\d{1,}')
    ports = [m.group(0) for m in rx.finditer(string)]

    ports = ports[0::2]
    fixed_ports = []

    for port in ports:
        fixed_ports.append(port[1:])

    dictionary = dict(zip(fixed_ports, apps))
    return dictionary

def summarize(packet):
    # setting size, dstip, and outorin
    size = len(packet)
    dst_ip = packet[IP].dst
    outOrIn = packet[IP].src == LOCAL_IP  # if incoming - False, outgoing - True

    # setting port and location
    if outOrIn:
        if TCP in packet:
            port = packet[TCP].dport
        else:
            port = packet[UDP].dport
        location = get_location(packet[IP].dst)
    else:
        if TCP in packet:
            port = packet[TCP].sport
        else:
            port = packet[UDP].sport
        location = get_location(packet[IP].src)
    
    # setting program
    try:
        prog = get_program()[port]
    except:
        prog = "Unknown"

    # appending summerized packet
    pack = {
        'prog': prog,  
        'dstIp': dst_ip,
        'locationIp': location,
        'outOrIn': outOrIn,
        'remotePort': port,
        'sizeOfPacket': size
        }
    summery_packets.append(pack)

def main():
    set_globals()
    sniff_count = 100


    while True:
        start = time.perf_counter()
        summery_packets = []
        packets = sniff(count=sniff_count, lfilter=spy)

        for packet in packets:
            summarize(packet)

        send_data(json.dumps(summery_packets))
        print("Sent {} summerized packets\nTook {} second(s)".format(sniff_count, time.perf_counter() - start))


if __name__ == '__main__':
    main()
