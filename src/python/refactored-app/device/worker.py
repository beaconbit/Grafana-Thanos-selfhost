# device/worker.py
import threading
import logging
import time

logger = logging.getLogger(__name__)

class DeviceWorker(threading.Thread):
    def __init__(self, device: dict):
        super().__init__()
        self.device = device
        self.daemon = True
        self.running = True

    def run(self):
        mac = self.device.get("mac", "unknown")
        logger.info(f"Starting worker thread for device {mac}")
        while self.running:
            # TODO: add device-specific auth, session, scraping logic here
            logger.debug(f"Working on device {mac}")
            time.sleep(5)  # simulate periodic work

    def stop(self):
        self.running = False
        logger.info(f"Stopping worker thread for device {self.device.get('mac', 'unknown')}")


