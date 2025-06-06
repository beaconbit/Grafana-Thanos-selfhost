from scapy.all import ARP, Ether, srp
from bs4 import BeautifulSoup
import requests 
import socket
import netifaces
import logging

def get_ip(interface):
    logging.debug('running get_ip')
    addrs = netifaces.ifaddresses(interface)
    if netifaces.AF_INET in addrs:
        return addrs[netifaces.AF_INET][0]['addr']
    return None

def get_local_ip():
    logging.debug('running get_local_ip')
    try:
        #local_ip = get_ip("enx72b1b1c1c8da")
        local_ip = get_ip("eno1")
        logging.debug(f'local ip: {local_ip}')
        return local_ip
    except Exception as e:
        return f"Error: {e}"

def scan_network():
    my_ip = get_local_ip()
    ip_range = my_ip + "/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, iface="eno1", timeout=3, verbose=False)[0]


    # Extract IP and MAC addresses from the response
    devices = {}
    for sent, received in result:
        logging.debug(f'Host: {received.psrc} MAC: {received.hwsrc}')
        devices[received.hwsrc] = received.psrc
    return devices
