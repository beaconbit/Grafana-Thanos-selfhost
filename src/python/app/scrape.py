import requests 
import sys
import logging

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


def request_di_values(ip, cookie):
    url = f'http://{ip}/di_value/slot_0'
    logging.debug(f'{colour.yellow}{url}{colour.reset}')

    headers = {'Cookie': f'adamsessionid={cookie}'}
    response = requests.get(url, headers=headers)
    logging.debug(f'{colour.yellow}{response}{colour.reset}')
    return { "error": None, "value": response }

