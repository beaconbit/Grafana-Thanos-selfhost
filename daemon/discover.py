from scapy.all import ARP, Ether, srp
from bs4 import BeautifulSoup
import requests 
import socket

def get_local_ip():
    try:
        # Connect to a public server to determine the local IP
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  # Google's public DNS server
            local_ip = s.getsockname()[0]
        return local_ip
    except Exception as e:
        return f"Error: {e}"

def scan_network():
    my_ip = get_local_ip()
    ip_range = my_ip + "/24"
    arp = ARP(pdst=ip_range)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    print(ether)
    print(arp)
    packet = ether / arp
    print(packet)
    result = srp(packet, timeout=2, verbose=False)[0]

    # Extract IP and MAC addresses from the response
    devices = []
    for sent, received in result:
        print(sent)
    for sent, received in result:
        try:
            # check which ones are WISE 4051
            url = f'http://{received.psrc}/config'
            response = requests.get(url)
            if response.status_code == 200:
                html_response = response.text
                soup = BeautifulSoup(html_response, 'html.parser')
                seeddata_input = soup.find('input', {'name': 'seeddata'})
                if seeddata_input:
                    devices.append({'ip': received.psrc, 'mac': received.hwsrc})
                    print(f"devices: {devices}")
        except Exception as e:
            print(f'{received.psrc} is not a known device')
            print(f'{e}')
    return devices
