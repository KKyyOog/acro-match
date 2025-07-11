# app.py

from flask import Flask, jsonify, request, abort
import threading
import time
import os
import sys
import requests
import logging
from datetime import datetime
from collections import deque

# Logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger("app")

# Add src to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), ".")))

from services.monitor_service import MonitorService

app = Flask(__name__)
monitor_service = MonitorService()

# Shared status dict
status_data = {
    "last_ping": None,
    "keep_alive_url": None,
    "keep_alive_status": None,
    "monitor_interval": None,
    "recent_logs": deque(maxlen=3)
}

# Optional auth token to protect /status
STATUS_TOKEN = os.environ.get("STATUS_TOKEN")

def keep_alive_loop():
    target_url = os.environ.get("KEEP_ALIVE_URL", "https://acro-match.onrender.com")
    interval = int(os.environ.get("KEEP_ALIVE_INTERVAL", 300))
    status_data["keep_alive_url"] = target_url
    status_data["monitor_interval"] = interval
    logger.info(f"Starting keep-alive ping to {target_url} every {interval} seconds")
    while True:
        try:
            response = requests.get(target_url, timeout=10)
            timestamp = datetime.utcnow().isoformat()
            status_data["last_ping"] = timestamp
            status_data["keep_alive_status"] = response.status_code
            status_data["recent_logs"].appendleft({"time": timestamp, "status": response.status_code})
            if response.status_code == 200:
                logger.info(f"Keep-alive ping succeeded: {response.status_code}")
            else:
                logger.warning(f"Keep-alive ping returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            timestamp = datetime.utcnow().isoformat()
            logger.error(f"Keep-alive ping failed: {e}")
            status_data["keep_alive_status"] = str(e)
            status_data["last_ping"] = timestamp
            status_data["recent_logs"].appendleft({"time": timestamp, "status": str(e)})
        time.sleep(interval)

@app.before_first_request
def start_background_threads():
    threading.Thread(target=start_monitoring, daemon=True).start()
    threading.Thread(target=keep_alive_loop, daemon=True).start()
    logger.info("Started background threads for monitoring and keep-alive")

@app.route("/")
def health_check():
    return "Monitor App is running", 200

@app.route("/status")
def get_status():
    if STATUS_TOKEN:
        token = request.args.get("token")
        if token != STATUS_TOKEN:
            abort(403)
    output = status_data.copy()
    output["recent_logs"] = list(status_data["recent_logs"])
    return jsonify(output)

def start_monitoring():
    target_url = os.environ.get("TARGET_URL", "https://acro-match.onrender.com")
    interval = int(os.environ.get("MONITOR_INTERVAL", 5))  # in minutes
    monitor_service.start_monitoring(target_url, interval=interval)

if __name__ == "__main__":
    # Fallback for local dev server
    app.run(host="0.0.0.0", port=5000)
