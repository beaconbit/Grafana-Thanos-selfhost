from authenticate import get_cookies
from scrape import request_di_values
from parse import extract_counts
from discover import scan_network
import json
import time
import os
from prometheus_client import start_http_server, Gauge


def clear_terminal():
    os.system('cls' if os.name == 'nt' else 'clear')


def code_a(ips_and_cookies, counters):
    for device_data in ips_and_cookies:
        di_values = request_di_values(device_data['ip'], device_data['cookie']['result'])
        json_text = di_values.text
        output = extract_counts(json_text)
        clear_terminal()
        print(output)
        for i, value in enumerate(output):
            counters[i].set(output[i])

def code_b():
    devices = scan_network()
    found_devices = []
    for device in devices:
        found_devices.append(device['ip'])
    ips_and_cookies = get_cookies(found_devices)
    return ips_and_cookies


def main():
    counter_1 = Gauge('count_1', 'Counter 1')
    counter_2 = Gauge('count_2', 'Counter 2')
    counter_3 = Gauge('count_3', 'Counter 3')
    counter_4 = Gauge('count_4', 'Counter 4')
    counter_5 = Gauge('count_5', 'Counter 5')
    counter_6 = Gauge('count_6', 'Counter 6')
    counter_7 = Gauge('count_7', 'Counter 7')
    counter_8 = Gauge('count_8', 'Counter 8')
    start_http_server(8000)


    last_run_time = time.time()  # Track the last time Code B was run
    interval = 1000  # Time interval for Code B (in seconds)
    ips_and_cookies = code_b()

    counters = [counter_1, counter_2, counter_3, counter_4, counter_5, counter_6, counter_7 , counter_8]

    try:
        while True:
            # Code A runs constantly

            try:
                code_a(ips_and_cookies, counters)
            except Exception as e:
                print("Timeout")
                print(e)
                time.sleep(5)

            # Check if it's time to run Code B
            current_time = time.time()
            if current_time - last_run_time >= interval:
                try:
                    ips_and_cookies = code_b()
                    print("check the network again")
                except Exception as e:
                    print("Timeout")
                    print(e)
                    time.sleep(5)
                last_run_time = current_time  # Update last run time for Code B

            # Add a small sleep to avoid excessive CPU usage
            time.sleep(0.1)
    except Exception as e:
        print(f"\nProgram terminated {e}")
    finally:
        print("Cleanup (if needed). Goodbye!")


if __name__ == "__main__":
    main()
