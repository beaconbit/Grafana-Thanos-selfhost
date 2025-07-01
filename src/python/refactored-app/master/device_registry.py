# global/device_registry.py

import threading
from utils.logging import setup_logger
from typing import Optional



logger = setup_logger(__name__)

_lock_type = type(threading.Lock())

class DeviceRegistry:
    def __init__(self, lock: threading.Lock, config: dict):
        if not (hasattr(lock, "acquire") and callable(lock.acquire) and
                hasattr(lock, "release") and callable(lock.release)):
            raise TypeError(f"Expected lock to be a Lock-like object, got {type(lock).__name__}")
        if not isinstance(config, dict):
            raise TypeError(f"Expected config to be dict, got {type(config).__name__}")

        self._devices = {}  # key: mac, value: device dict
        self._lock = lock
        self._config = config

    def get_config(self):
        return self._config

    def add_or_update_device(self, mac, ip):
        with self._lock:
            if mac not in self._devices:
                self._devices[mac] = {
                    'mac': mac,
                    'ip': ip,
                    'valid': True,
                    'failures': 0,
                    'username': None,
                    'password': None,
                    'cookie': None,
                    'cookie_expires': None,
                    'last_data': None,
                    'last_seen': None,
                }
                logger.info(f"Added new device: {mac} @ {ip}")
            else:
                self._devices[mac]['ip'] = ip
                logger.debug(f"Updated device IP: {mac} -> {ip}")

    def mark_invalid(self, mac):
        with self._lock:
            if mac in self._devices:
                self._devices[mac]['valid'] = False
                logger.warning(f"Device marked invalid: {mac}")

    def get_all_devices_copy(self):
        with self._lock:
            return list(self._devices.values())

    def get_device(self, mac):
        with self._lock:
            return self._devices.get(mac)

    def update_device_field(self, mac, field, value):
        with self._lock:
            if mac in self._devices:
                self._devices[mac][field] = value
                logger.debug(f"Device {mac} updated: {field} = {value}")

    def remove_device(self, mac):
        with self._lock:
            if mac in self._devices:
                del self._devices[mac]
                logger.info(f"Removed device: {mac}")

# This handles the singleton situation 
def set_registry(instance: DeviceRegistry):
    global registry
    registry = instance

def get_registry() -> DeviceRegistry:
    if registry is None:
        raise RuntimeError("DeviceRegistry has not been initialized yet. Call set_registry() first.")
    return registry

# this needs to be a singleton
registry: Optional[DeviceRegistry] = None
