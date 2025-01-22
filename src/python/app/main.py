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
known_devices = {}  # a dict { '43:cb:7d:71:27:74' : device, 'ff:cb:7d:ff:27:ff' : device_2 }
ip_to_cookie = {}   # a dict {'10.0.0.3', cookie}
cookie_ttl = {}
cookie_to_refresh = []
delete_me = []
blacklist = []

# Lock for shared data
lock = threading.Lock()


# working
class Device:
    def __init__(self, mac, gauge_name, gauge_description):
        self.mac = mac
        self.gauge = Gauge(gauge_name, gauge_description)

# working
def device_factory():
    """Factory function that returns a function for creating devices."""
    next_id = 1  # Variable to keep track of the next available integer
    def create_device(mac):
        nonlocal next_id  # Access and modify the outer variable
        gauge_name = f"count_{next_id}"
        next_id += 1
        return Device(mac, gauge_name, mac)
    return create_device

                

def count_query(ip):
    global ip_to_cookie
    logging.debug(f'{colour.yellow}Count Query: count_query {ip}{colour.reset}')
    logging.debug(f'{colour.yellow}Count Query: {ip_to_cookie}{colour.reset}')
    result = { 'error': 'no cookie', 'value': None }
    if ip in ip_to_cookie:
        logging.debug(f'{colour.yellow}Count Query: cookie: {ip_to_cookie[ip]}{colour.reset}')
        response = request_di_values(ip, ip_to_cookie[ip])
        if response['error'] is None:
            json_text = response['value'].text
            result = { 'error': None, 'value': extract_counts(json_text) }
        else: 
            result = { 'error': response['error'], 'value': None }
    else:
        result = { 'error': 'no cookie', 'value': None }
    return result


def count_updater():
    global delete_me
    global mac_to_ip
    global blacklist

    while True:
        with lock:
            for mac, ip in mac_to_ip.items():
                if ip not in ip_to_cookie and ip not in delete_me:
                    delete_me.append(ip)
                else:
                    result = count_query(ip)
                    if result['error'] is None:
                        count = result['value']
                        logging.debug(f'{colour.magenta}Counter: device {ip} : {mac} new count {count}{colour.reset}')
                    else:
                        delete_me.append(ip)
        time.sleep(5) 
            


def clean_up():
    global delete_me
    global mac_to_ip
    while True:
        with lock:
            logging.debug(f'{colour.yellow}Clean Up: running clean up on {delete_me}{colour.reset}')
            for bad_ip in delete_me:
                if bad_ip in mac_to_ip.values() and bad_ip not in ip_to_cookie:
                    for mac, ip in list(mac_to_ip.items()):
                        if ip == bad_ip:
                            logging.debug(f'{colour.yellow}Clean Up: Deleting {mac} from mac_to_ip{colour.reset}')
                            del mac_to_ip[mac]
                            blacklist.append(mac)
                            break
            # reset the kill list
            delete_me = []
        time.sleep(240) 

# working
def scanner():
    global mac_to_ip
    global blacklist
    logging.debug(f'{colour.green}Scanner: starting{colour.reset}')
    while True:
        new_active_ips = scan_network() # returns a dict { '43:cc:ff:aa:23:45': '10.0.0.2', ... }
        not_blacklisted = {}
        with lock:
            for mac, ip in new_active_ips.items():
                if mac not in blacklist:
                    not_blacklisted[mac] = ip
            mac_to_ip.update(not_blacklisted)
            logging.debug(f'{colour.green}Scanner: mac_to_ip = {mac_to_ip}{colour.reset}')
        time.sleep(15) 

# working
def device_manager():
    logging.debug(f'{colour.magenta}Device Manager: starting{colour.reset}')
    global mac_to_ip
    global known_devices
    create_device = device_factory()
    while True:
        with lock:
            for mac, ip in mac_to_ip.items():
                if mac not in known_devices:
                    new_device = create_device(mac)
                    known_devices[mac] = new_device
            logging.debug(f'{colour.magenta}Device Manager: known_devices = {known_devices}{colour.reset}')
        time.sleep(1) 

# working
def cookie_monster():
    logging.debug("cookie monster started")
    global ip_to_cookie
    global mac_to_ip 
    global cookie_ttl
    global cookie_to_refresh
    while True:
        # need to drop the lock to let the count_query use it
        with lock:
            for mac, ip in mac_to_ip.items():
                # pass ip to cookie getter
                if ip not in ip_to_cookie or ip_to_cookie[ip] in cookie_to_refresh:
                    logging.debug(f'Cookie Monster: fetching cookie for {ip}')
                    result = get_cookie(ip)
                    if result['error'] is None:
                        ip_to_cookie[ip] = result['value']
                        cookie_ttl[result['value']] = 300
                    else:
                        ip_to_cookie[ip] = None
                        err = result['error']
                        logging.debug(f'{colour.red}Error: {err}{colour.reset}')
            # clean up all the invalid cookies
            ip_to_cookie = {key: value for key, value in ip_to_cookie.items() if value is not None}
            logging.debug(f'Cookie Monster: ip_to_cookie = {ip_to_cookie}')
        time.sleep(420) 

def lifetime_manager():
    global cookie_to_refresh
    global cookie_ttl
    while True:
        with lock:
            for cookie, ttl in cookie_ttl.items():
                # decrement time to live
                if ttl > 0:
                    cookie_ttl[cookie] = ttl - 1
                # when time to live gets below 10, add it to the refresh list
                if ttl < 10:
                    cookie_to_refresh.append(cookie)
        time.sleep(1) 

def main():
    # Create threads
    thread1 = threading.Thread(target=scanner, daemon=True)
    thread2 = threading.Thread(target=count_updater, daemon=True)
    thread3 = threading.Thread(target=device_manager, daemon=True)
    thread4 = threading.Thread(target=cookie_monster, daemon=True)
    thread5 = threading.Thread(target=clean_up, daemon=True)

    # Start threads
    thread1.start()
    thread2.start()
    thread3.start()
    thread4.start()
    thread5.start()

    # counter_1 = Gauge('count_1', 'Counter 1')
    # counter_2 = Gauge('count_2', 'Counter 2')
    start_http_server(8000)

    try:
        while True:
            time.sleep(1)  # Sleep to prevent high CPU usage
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()

