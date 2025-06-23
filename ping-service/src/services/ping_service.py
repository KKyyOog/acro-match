import subprocess
import requests
from services.alert_service import AlertService
from utils.logger import setup_logger

logger = setup_logger("ping_service_logger")

logger.debug("PingService logger initialized")
logger.info("This is a test log entry from ping_service.py")

class PingService:
    def ping(self, host, timeout=5, count=1):
        if not host.strip():
            logger.error("Ping exception for host: Hostname is empty")
            return "Ping exception for host: Hostname is empty"
        try:
            logger.info(f"Executing ping command for host: {host}")
            command = ["ping", "-n", str(count), host]
            result = subprocess.run(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout
            )
            logger.info(f"Command executed successfully for host: {host}")
            logger.debug(f"Return code: {result.returncode}")
            logger.debug(f"Stdout: {result.stdout.strip()}")
            logger.debug(f"Stderr: {result.stderr.strip()}")

            if "Request timed out." in result.stdout:
                logger.warning(f"Detected timeout in stdout for host: {host}")
                return f"Ping timeout for host {host}"

            if result.returncode == 0:
                logger.info(f"Ping succeeded for host: {host}")
                return result.stdout
            else:
                logger.warning(f"Ping failed for host: {host}")
                return f"Ping failed for host {host}: {result.stderr.strip()}"
        except subprocess.TimeoutExpired as e:
            logger.error(f"TimeoutExpired exception caught -> {e}")
            return f"Ping timeout for host {host}"
        except Exception as e:
            logger.error(f"General exception caught -> {e}")
            return f"Ping exception for host {host}: {e}"

    def check_http(self, url, timeout=5):
        try:
            logger.info(f"Sending HTTP GET request to {url} with timeout={timeout}")
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                logger.info(f"HTTP request succeeded for {url}")
                return f"Server is reachable: {url}"
            else:
                logger.warning(f"HTTP request failed with status code {response.status_code} for {url}")
                AlertService().send_alert(f"Server returned status code {response.status_code}: {url}")
                return f"Server returned status code {response.status_code}: {url}"
        except requests.exceptions.Timeout:
            logger.error(f"HTTP timeout for {url}")
            AlertService().send_alert(f"HTTP timeout for server: {url}")
            return f"HTTP timeout for server: {url}"
        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP exception caught -> {e}")
            AlertService().send_alert(f"HTTP exception for server {url}: {e}")
            return f"HTTP exception for server {url}: {e}"
