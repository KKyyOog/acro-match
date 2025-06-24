# keep_alive.py

import time
import requests
import logging
import os
from dotenv import load_dotenv

# Load .env config
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("keep_alive")

# Target URL and interval from environment or defaults
TARGET_URL = os.environ.get("KEEP_ALIVE_URL", "https://acro-match.onrender.com")
INTERVAL_SECONDS = int(os.environ.get("KEEP_ALIVE_INTERVAL", 300))  # default 5 minutes

def keep_alive_loop():
    logger.info(f"Starting keep-alive ping to {TARGET_URL} every {INTERVAL_SECONDS} seconds")
    while True:
        try:
            response = requests.get(TARGET_URL, timeout=10)
            if response.status_code == 200:
                logger.info(f"Keep-alive ping succeeded: {response.status_code}")
            else:
                logger.warning(f"Keep-alive ping returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Keep-alive ping failed: {e}")
        time.sleep(INTERVAL_SECONDS)

if __name__ == "__main__":
    keep_alive_loop()
