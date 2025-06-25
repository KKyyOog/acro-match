# app.py

from flask import Flask, jsonify
import threading
import time
import os
import sys
import requests
import logging
from datetime import datetime

print("🟢 LOADED app.py")

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
    "monitor_interval": None
}

def keep_alive_loop():
    target_url = os.environ.get("KEEP_ALIVE_URL", "https://acro-match.onrender.com")
    interval = int(os.environ.get("KEEP_ALIVE_INTERVAL", 300))
    status_data["keep_alive_url"] = target_url
    status_data["monitor_interval"] = interval
    logger.info(f"Starting keep-alive ping to {target_url} every {interval} seconds")
    while True:
        try:
            response = requests.get(target_url, timeout=10)
            status_data["last_ping"] = datetime.utcnow().isoformat()
            status_data["keep_alive_status"] = response.status_code
            if response.status_code == 200:
                logger.info(f"Keep-alive ping succeeded: {response.status_code}")
            else:
                logger.warning(f"Keep-alive ping returned status {response.status_code}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Keep-alive ping failed: {e}")
            status_data["keep_alive_status"] = str(e)
        time.sleep(interval)

@app.route("/")
def health_check():
    return "Monitor App is running", 200

@app.route("/status")
def get_status():
    return jsonify(status_data)

def start_monitoring():
    target_url = os.environ.get("TARGET_URL", "https://acro-match.onrender.com")
    interval = int(os.environ.get("MONITOR_INTERVAL", 5))  # in minutes
    monitor_service.start_monitoring(target_url, interval=interval)

if __name__ == "__main__":
    # Start both threads
    threading.Thread(target=start_monitoring, daemon=True).start()
    threading.Thread(target=keep_alive_loop, daemon=True).start()

    try:
        from gunicorn.app.base import BaseApplication

        class FlaskApplication(BaseApplication):
            def __init__(self, app, options=None):
                self.options = options or {}
                self.application = app
                super().__init__()

            def load_config(self):
                for key, value in self.options.items():
                    self.cfg.set(key, value)

            def load(self):
                return self.application

        options = {
            "bind": "0.0.0.0:5000",
            "workers": 1
        }
        FlaskApplication(app, options).run()
    except ImportError:
        print("Gunicorn not installed. Falling back to Flask dev server.")
        app.run(host="0.0.0.0", port=5000)
