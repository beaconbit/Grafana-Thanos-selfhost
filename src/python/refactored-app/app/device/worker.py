# device/worker.py
import threading
import logging
import time
from device.utils.auth_flow_registry import auth_flow_registry
from device.utils.scraper_registry import scraper_registry
from device.utils.brute_force import brute_force
from utils.logging import setup_logger

logger = setup_logger(__name__)

class DeviceWorker(threading.Thread):
    def __init__(self, device: dict, validate, invalidate, update_device_field):
        super().__init__()
        self.device = device
        self.validate = validate
        self.invalidate = invalidate
        self.update_device_field = update_device_field
        self.daemon = True
        self.running = True

    def run(self):
        mac = self.device.get("mac", "unknown")
        logger.info(f"Starting worker thread for device {mac}")
        while self.running:
            if self.device.get('failures') > 5:
                logger.debug(f"LOTS OF FAILURES: {self.device.get('failures')}")
                self.invalidate()
            try:
                if self.device.get("cookie_expires", -1) < int(time.time()):
                    logger.critical(f"Refreshing cookie")
                    self.device["cookie"] = self.get_cookie()
                    self.reset_cookie_expiration()
                    logger.critical(f"Refreshed cookie: {self.device.get('cookie')}")
                logger.info(f"About to check cookie: {self.device.get('cookie')}")
                if self.device.get("cookie", False):
                    logger.info(f"About to scraped zee data")
                    data = self.scrape()
                    logger.info(f"Finished scraping le daataa: {data}")
                    logger.critical(f"data: {data}")
                # TODO after scraping data expose it to an endpoint so prometheus can scrape it
                else:
                    # brute_force will throw an error if all the auth flows fail
                    password, username, auth_flow, scraper = brute_force(self.device)
                    logger.critical(f"Brute force returned password:{password} username:{username} auth_flow:{auth_flow} scraper:{scraper}")
                    self.device['password'] = password
                    self.device['username'] = username
                    self.device['auth_flow'] = auth_flow
                    self.device['scraper'] = scraper
                    self.device['cookie_expires'] = -1
                    self.validate(password, username, auth_flow, scraper)
                    self.update_device_field(password=password, username=username, auth_flow=auth_flow, scraper=scraper)
            except Exception as e:
                logger.error(f"Device {self.device['mac']} failed: {e}")
                self.device['failures'] += 1
                logger.error(f"Incrementing device failure count {self.device.get('failures')}")

            logger.debug(f"Working on device {mac}")
            time.sleep(5)  # simulate periodic work

    def stop(self):
        self.running = False
        logger.info(f"Stopping worker thread for device {self.device.get('mac', 'unknown')}")

    def reset_cookie_expiration(self):
        expires_at = int(time.time()) + (20 * 60)  # 20 minutes from now
        self.device['cookie_expires'] = expires_at

    def get_cookie(self):
        auth_flow = self.device['auth_flow'] 
        logger.debug(f"Using auth_flow: {auth_flow}")
        if auth_flow is None:
            return None
        get_cookie_fn = auth_flow_registry.get(auth_flow)
        data = get_cookie_fn(self.device)
        return data

    def scrape(self):
        scraper = self.device['scraper']
        logger.debug(f"Using scraper: {scraper}")
        if scraper is None:
            return None
        scraper_fn = scraper_registry.get(scraper)
        data = scraper_fn(self.device)
        return data


