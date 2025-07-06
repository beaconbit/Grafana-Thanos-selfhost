from device.utils.auth_flow_registry import auth_flow_registry
from device.utils.scraper_registry import scraper_registry
from utils.logging import setup_logger

logger = setup_logger(__name__)

def brute_force(device: dict) -> bool:
    logger.info(f"Brute forcing device {device.get('mac')}")
    return ["ubuntu", "root", "spindle_device", "spindle_device"]
