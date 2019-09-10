from scapy3k.all import *
from scapy3k.layers.inet import IP, TCP, UDP
import json
import requests
import socket
import os
import re


#  text = json.dumps(data) - encodes
#  data = json.loads(text) - decodes


summery_packets = []
LOCAL_IP = ""
SERVER_ADDR = "192.168.8.172"
SERVER_PORT = 1313
# config file ^


def get_program():
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


def checked_before(IP):
    global summery_packets
    for pack in summery_packets:
        if pack["dstIp"] == IP:
            return pack["locationIp"]


def set_local_ip():
    global LOCAL_IP

    msg = IP(dst="8.8.8.8")
    LOCAL_IP = msg[IP].src


def get_location(IP):
    if "192.168." in IP or "10." in IP:
        return "Private Network"

    checked = checked_before(IP)
    if not checked:
        response = requests.get("http://ip-api.com/json/"+IP)
        data = json.loads(response.text)
        if "country" in data:
            return data["country"]
        else:
            print(data)
            return "ERROR"


def spy(packet):
    return IP in packet and (TCP in packet or UDP in packet)


def summarize(packet):
    global LOCAL_IP
    global summery_packets

    outOrIn = packet[IP].src == LOCAL_IP  # if incoming - False, outgoing - True
    dst_ip = packet[IP].dst

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
    size = len(packet)

    pack = {
        'dstIp': dst_ip,
        'locationIp': location,
        'outOrIn': outOrIn,
        'remotePort': port,
        'sizeOfPacket': size
    }
    summery_packets.append(pack)


def send_data(msg):
    # Create a non-specific UDP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    server_address = (SERVER_ADDR, SERVER_PORT)
    sock.connect(server_address)

    sock.sendto(msg.encode(), server_address)

    sock.close()


def main():
    global summery_packets

    get_prog()

    set_local_ip()

    while True:
        summery_packets = []
        packets = sniff(count=100, lfilter=spy)

        for packet in packets:
            summarize(packet)

        text = json.dumps(summery_packets)

        send_data(text)


if __name__ == '__main__':
    main()


"""
{
    'prog': discord.exe 
    'dstIp': 'a string',
    'locationIp': 'a string',
    'outOrIn': True,  # or false
    'remotePort': 99,  # a number
    'sizeOfPacket': 95  # a number
}
"""
