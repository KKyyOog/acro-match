# src/utils/logger.py

import os
import logging
from logging.handlers import RotatingFileHandler, SysLogHandler

def setup_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.hasHandlers():
        return logger  # avoid duplicate handlers

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

    # File handler
    file_handler = RotatingFileHandler("monitor.log", maxBytes=5 * 1024 * 1024, backupCount=3)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Optional syslog handler via ENV
    log_host = os.environ.get("SYSLOG_HOST")
    log_port = int(os.environ.get("SYSLOG_PORT", 514))

    if log_host:
        try:
            syslog_handler = SysLogHandler(address=(log_host, log_port))
            syslog_handler.setFormatter(formatter)
            logger.addHandler(syslog_handler)
        except Exception as e:
            logger.warning(f"Syslog handler init failed: {e}")

    logger.debug("Logger '%s' initialized", name)
    return logger
