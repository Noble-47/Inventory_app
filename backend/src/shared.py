from logging.handlers import RotatingFileHandler
from functools import partial
from datetime import datetime
from pathlib import Path
import logging
import pytz
import os
import json

TIMEZONE = pytz.timezone("Africa/Lagos")

datetime_now_func = partial(datetime.now, tz=pytz.timezone("Africa/Lagos"))

LOG_DIR = Path(__file__).parent.parent / "log"


def get_rotating_logger(logger_name: str, log_filename: str) -> logging.Logger:
    """
    Returns a logger with a RotatingFileHandler that writes to log/log_filename at the project root.
    """
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = LOG_DIR / log_filename

    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        handler = RotatingFileHandler(log_file, maxBytes=2 * 1024 * 1024, backupCount=5)
        formatter = logging.Formatter("[%(asctime)s] %(levelname)s %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

        # Stream handler for logging to the console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    return logger


def load_payload(payload):
    payload = json.loads(payload)
    if "time" in payload:
        payload["time"] = datetime.fromtimestamp(payload["time"])
    return payload
