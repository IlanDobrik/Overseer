import sys
import json
import requests
import socket
import os
import re
from scapy.all import *
import time

summarized_packets = []
LOCAL_IP = ""
SERVER_ADDR = "127.0.0.1"
SERVER_PORT = 1313
SIZE = 100

def spy(packet):
    return IP in packet and (TCP in packet or UDP in packet)

def set_globals():
    global LOCAL_IP, SERVER_ADDR, SERVER_PORT, SIZE
    msg = IP(dst="8.8.8.8")
    LOCAL_IP = msg[IP].src

    # check if any of the args appears more than one time
    if not all([sys.argv.count("-l") < 2,  sys.argv.count("-s") < 2, sys.argv.count("-i") < 2]):
        print("Invalid args")
        os._exit(-1)

    try:
        # port
        if "-l" in sys.argv and 0 < sys.argv[sys.argv.index("-l") + 1] < 65535:
            LISTEN_PORT = sys.argv[sys.argv.index("-l") + 1]
        # size
        if "-s" in sys.argv and int(sys.argv[sys.argv.index("-s") + 1]) > 0:
            pass
        # server ip
        if "-i" in sys.argv:
            if result := re.match(r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}$", sys.argv[sys.argv.index("-s") + 1]): # a kinda close regex to a valid ip
                SERVER_ADDR = result.group()
    except:
        print("Invalid args")
        os._exit(-1)

def checked_before(IP):
    # checking if IP has been checked before by the geo-location service
    # to reduce traffic
    global summarized_packets
    for pack in summarized_packets:
        if pack["dstIp"] == IP:
            return pack["locationIp"]

def get_location(IP):
    # cant show geo-location if ip is invalid
    if "192.168." in IP or "10." in IP:
        return "Private Network"

    # sending request to a geo-location service that returns a json
    checked = checked_before(IP)
    if not checked:
        try:
            response = requests.get("http://ip-api.com/json/"+IP)
            data = json.loads(response.text)
            return data["country"]
        except:
            return "ERROR"

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
    global summarized_packets
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
    summarized_packets.append(pack)

def main():
    set_globals()

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_ADDR, SERVER_PORT))
    
    print("Collecting packets...")

    while True:
        start = time.perf_counter()
        summarized_packets.clear()
        packets = sniff(count=SIZE, lfilter=spy)

        for packet in packets:
            summarize(packet)

        try:
            s.sendall(json.dumps(summarized_packets).encode())
            print("Sent {} summarized packets\nTook {} second(s)".format(SIZE, time.perf_counter() - start))
        except Exception as e:
            print(e)
            print(SERVER_ADDR, "not responding")
            break

if __name__ == '__main__':
    main()
