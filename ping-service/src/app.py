# app.py

from flask import Flask
import threading
import time
import os
import sys

# Add src to path to import services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from services.monitor_service import MonitorService

app = Flask(__name__)
monitor_service = MonitorService()

@app.route("/")
def health_check():
    return "Monitor App is running", 200

def start_monitoring():
    target_url = os.environ.get("TARGET_URL", "https://acro-match.onrender.com")
    interval = int(os.environ.get("MONITOR_INTERVAL", 5))  # in minutes
    monitor_service.start_monitoring(target_url, interval=interval)

if __name__ == "__main__":
    # Start monitoring in background thread
    monitor_thread = threading.Thread(target=start_monitoring, daemon=True)
    monitor_thread.start()

    # Start Flask app
    app.run(host="0.0.0.0", port=5000)
