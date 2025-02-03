from scrape import request_di_values
from parse import extract_counts
from discover import scan_network
import json
import time
import os
from prometheus_client import start_http_server, Gauge
import random


#def clear_terminal():
#    os.system('cls' if os.name == 'nt' else 'clear')
#
#
#def code_a(ips_and_cookies, counters):
#    for device_data in ips_and_cookies:
#        di_values = request_di_values(device_data['ip'], device_data['cookie']['result'])
#        json_text = di_values.text
#        output = extract_counts(json_text)
#        clear_terminal()
#        print(output)
#        for i, value in enumerate(output):
#            counters[i].set(output[i])

#def code_b():
#    devices = scan_network()
#    found_devices = []
#    for device in devices:
#        found_devices.append(device['ip'])
#    ips_and_cookies = get_cookies(found_devices)
#    return ips_and_cookies
#
#def normal_loop(counters):
#    last_run_time = time.time()  # Track the last time Code B was run
#    interval = 1000  # Time interval for Code B (in seconds)
#    # code b
#    ips_and_cookies = code_b()
#    # code a
#    code_a(ips_and_cookies, counters)
#    try:
#        while True:
#            # Code A runs constantly
#
#            try:
#                code_a(ips_and_cookies, counters)
#            except Exception as e:
#                print("Timeout")
#                print(e)
#                time.sleep(5)
#
#            # Check if it's time to run Code B
#            current_time = time.time()
#            if current_time - last_run_time >= interval:
#                try:
#                    ips_and_cookies = code_b()
#                    print("check the network again")
#                except Exception as e:
#                    print("Timeout")
#                    print(e)
#                    time.sleep(5)
#                last_run_time = current_time  # Update last run time for Code B
#
#            # Add a small sleep to avoid excessive CPU usage
#            time.sleep(0.1)
#    except Exception as e:
#        print(f"\nProgram terminated {e}")
#    finally:
#        print("Cleanup (if needed). Goodbye!")


def increment_at_speed(speed):
    unlikely =      [0, 0, 0, 0, 0, 1, 0, 0, 0, 0]
    likely =        [0, 0, 0, 0, 1, 0, 1, 0, 0, 0]
    definite =      [0, 0, 0, 1, 0, 1, 0, 1, 0, 0]
    certain =       [0, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    guaranteed =    [0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    chance = [ unlikely, likely, definite, certain, guaranteed]
    random_number = random.randint(0, 4)
    result = chance[speed][random_number]
    return result
    

def generate_synthetic_data_loop(counters):
    while True:
        print("generating synthetic data")
        time.sleep(1)
        for i, counter in enumerate(counters):
            old = counter._value.get()
            print(f'counter_{i} : {old}')
            inc = increment_at_speed(i % 4)
            # set counter to 'old value' + 'random increment' where random increment can be zero
            counter.set(old + inc)

def main():
    counter_1 = Gauge('washer_1', 'Counter 1')
    counter_2 = Gauge('washer_2', 'Counter 2')
    counter_3 = Gauge('ironer_1', 'Counter 3')
    counter_4 = Gauge('ironer_2', 'Counter 4')
    counter_5 = Gauge('small_piece_folder_1', 'Counter 5')
    counter_6 = Gauge('small_piece_folder_2', 'Counter 6')
    counter_7 = Gauge('small_piece_folder_3', 'Counter 7')
    start_http_server(8000)

    counters = [counter_1, counter_2, counter_3, counter_4, counter_5, counter_6, counter_7]

    generate_synthetic_data_loop(counters)


if __name__ == "__main__":
    main()
