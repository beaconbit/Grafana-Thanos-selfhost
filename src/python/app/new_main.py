from authenticate import get_cookie
from scrape import request_di_values
from discover import scan_network
from parse import extract_counts
from prometheus_client import start_http_server, Gauge
import threading
import time
from collections import defaultdict
import logging
import sys


# Configure logging to print to stdout with no buffering
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(message)s', stream=sys.stdout)

class Colour:
    """Class to provide ANSI escape codes for colors."""
    def __init__(self):
        self._codes = {
            'blue': '\033[94m',    # Blue
            'green': '\033[92m',   # Green
            'yellow': '\033[93m',  # Yellow
            'red': '\033[91m',     # Red
            'magenta': '\033[95m', # Magenta
            'reset': '\033[0m',    # Reset
        }
    @property
    def blue(self):
        return self._codes['blue']

    @property
    def green(self):
        return self._codes['green']

    @property
    def yellow(self):
        return self._codes['yellow']

    @property
    def red(self):
        return self._codes['red']

    @property
    def magenta(self):
        return self._codes['magenta']

    @property
    def reset(self):
        return self._codes['reset']
colour = Colour()

# Shared data structures
mac_to_ip = {}      # a dict { '43:cb:7d:71:27:74' : '10.0.0.3', 'ff:cb:7d:ff:27:ff' : '10.0.0.23' }
ip_to_cookie = {}   # a dict {'10.0.0.3', cookie}
mac_to_count = {}   # a dict {'43:cb:7d:71:27:74', [0,0,0,0,0,0,0,0]}
mac_to_gauges = {}  # a dict {'43:cb:7d:71:27:74': [Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge]}
blacklist = []
blacklist_ttl = 1200
refresh_blacklist_counter = blacklist_ttl

# Lock for shared data
lock = threading.Lock()

# working
def scanner():
    global mac_to_ip
    #logging.debug(f'{colour.green}Scanner: starting{colour.reset}')
    while True:
        new_active_ips = scan_network() # returns a dict { '43:cc:ff:aa:23:45': '10.0.0.2', ... }
        logging.debug(f'{colour.green} scan found: {new_active_ips}{colour.reset}')
        with lock:
            mac_to_ip.update(new_active_ips)
            #logging.debug(f'{colour.green}Scanner: mac_to_ip = {mac_to_ip}{colour.reset}')
        time.sleep(1) 

def cookie_monster():
    global ip_to_cookie
    global mac_to_ip 
    global ip_to_cookie
    global blacklist
    global refresh_blacklist_counter 
    global blacklist_ttl
    while True:

        with lock:
            refresh_blacklist_counter -= 1
            logging.debug(f'{colour.yellow}Blacklist ttl value {refresh_blacklist_counter}{colour.reset}')
            if refresh_blacklist_counter == 0:
                logging.debug(f'{colour.blue}{blacklist}{colour.reset}')
                blacklist = []
                mac_to_ip = {}
                ip_to_cookie = {}
                logging.debug(f'{colour.blue}Blacklist reset{colour.reset}')
                logging.debug(f'{colour.blue}{blacklist}{colour.reset}')
                refresh_blacklist_counter = blacklist_ttl
                logging.debug(f'{colour.blue}Blacklist ttl value {refresh_blacklist_counter}{colour.reset}')

        # Step 1: Copy the shared map under lock
        with lock:
            # shallow copy, blacklisted mac's filtered out
            mac_to_ip_copy = {k: v for k, v in mac_to_ip.items() if k not in blacklist}
        # Step 2: Work on the copy without holding the lock
        for mac, ip in mac_to_ip_copy.items():
            with lock:
                if ip in ip_to_cookie:
                    continue  # already have cookie
            # Step 3: Fetch cookie (can be slow)
            #logging.debug(f'Cookie Monster: fetching cookie for {ip}')
            result = get_cookie(ip)
            # Step 4: Store result back under lock
            with lock:
                if result['error'] is None:
                    ip_to_cookie[ip] = result['value']
                else:
                    if ip in ip_to_cookie:
                        del ip_to_cookie[ip]
                    err = result['error']
                    logging.debug(f'{colour.red}{err}{colour.reset}')
                    # get mac and add it to the blacklist
                    if mac not in blacklist:
                        blacklist.append(mac)
        # Step 5: Clean up invalid cookies under lock
        with lock:
            ip_to_cookie = {key: value for key, value in ip_to_cookie.items() if value is not None}
            #logging.debug(f'Cookie Monster: ip_to_cookie = {ip_to_cookie}')

        time.sleep(1)

def count_query(ip):
    global ip_to_cookie
    result = { 'error': 'no cookie', 'value': None }
    with lock:
        #logging.debug(f'{colour.yellow}{ip_to_cookie}{colour.reset}')
        ip_to_cookie_copy = dict(ip_to_cookie)  # shallow copy
    if ip in ip_to_cookie_copy:
        cookie = ip_to_cookie_copy[ip]
        if cookie is not None:
            #logging.debug(f'{colour.yellow}Count Query: cookie: {ip_to_cookie[ip]}{colour.reset}')
            try:
                response = request_di_values(ip, cookie)
                if response['error'] is None:
                    json_text = response['value'].text
                    #logging.debug(f'{colour.yellow}{json_text}{colour.reset}')
                    result = { 'error': None, 'value': extract_counts(json_text) }
                else: 
                    with lock:
                        result = { 'error': response['error'], 'value': None }
                        ip_to_cookie[ip] = None
            except Exception as e:
                with lock:
                    # delete ip to cookie, delete mac to ip
                    logging.debug(f'{colour.red}Counter: deleting cookie and ip {ip}{colour.reset}')
                    if ip in ip_to_cookie:
                        del ip_to_cookie[ip]
        else:
            result = { 'error': 'no cookie', 'value': None }
    else:
        result = { 'error': 'no cookie', 'value': None }
    return result

def create_gauge_list(mac):
    # implement
    gauges = []
    for i in range(8):
        description = f"unknown device {i}"
        safe_mac = mac.replace(":", "_")
        name = f"device_{safe_mac}_count_{i}"
        gauge = Gauge(name, description)
        gauges.append(gauge)
    return gauges


def count_updater():
    global mac_to_ip
    global ip_to_cookie
    global mac_to_count  # a dict {'43:cb:7d:71:27:74', [0,0,0,0,0,0,0,0]}
    global mac_to_gauges # a dict {'43:cb:7d:71:27:74': [Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge]}
    while True:
        with lock:
            mac_to_ip_copy = dict(mac_to_ip)  # shallow copy
        for mac, ip in mac_to_ip_copy.items():
            try:
                result = count_query(ip)
            except Exception as e:
                # delete mac to ip
                with lock:
                    logging.debug(f'{colour.red}Counter: deleting ip and mac pair {ip} : {mac}{colour.reset}')
                    if mac in mac_to_ip:
                        del mac_to_ip[mac]
            if result['error'] is None:
                count = result['value']
                # check if mac_to_count exists, check if mac_to_gauges exists
                with lock:
                    if mac not in mac_to_count:
                        mac_to_count[mac] = count
                    if mac not in mac_to_gauges:
                        mac_to_gauges[mac] = create_gauge_list(mac)
                    # update the count
                    if mac in mac_to_count:
                        mac_to_count[mac] = count
                logging.debug(f'{colour.magenta}Counter: device {ip} : {mac} new count {count}{colour.reset}')
            else:
                # delete ip to cookie, delete mac to ip
                logging.debug(f'{colour.red}Counter: need to delete cookie or reset ip and mac {ip} : {mac}{colour.reset}')
                # delete mac to ip, and ip to cookie
                with lock:
                    logging.debug(f'{colour.red}Counter: deleting everything, ip and mac and cookie {colour.reset}')
                    logging.debug(f'{colour.magenta}Blacklist: {blacklist}{colour.reset}')
                    if mac in mac_to_ip:
                        del mac_to_ip[mac]
                    if ip in ip_to_cookie:
                        del ip_to_cookie[ip]
        time.sleep(1) 

def update_gauges():
    global mac_to_count   # a dict {'43:cb:7d:71:27:74', [0,0,0,0,0,0,0,0]}
    global mac_to_gauges  # a dict {'43:cb:7d:71:27:74': [Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge, Gauge]}
    while True:
        with lock:
        # iterate through mac_to_counts
        # for each count iterate through mac_to_gauges[mac] and update them
            logging.debug(f'{colour.green} {mac_to_count} {colour.reset}')
            for mac, counts in mac_to_count.items():
                current_gauges = mac_to_gauges[mac]
                for i, count in enumerate(counts):
                    current_gauges[i].set(count)
            logging.debug(f'{colour.green}counts: {mac_to_count} {colour.reset}')
        time.sleep(1) 

def main():
    # Create threads
    thread1 = threading.Thread(target=scanner, daemon=True)
    thread2 = threading.Thread(target=cookie_monster, daemon=True)
    thread3 = threading.Thread(target=count_updater, daemon=True)
    thread4 = threading.Thread(target=update_gauges, daemon=True)

    # Start threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()


    start_http_server(8000)

    try:
        while True:
            time.sleep(1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()

