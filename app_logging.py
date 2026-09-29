import logging
import os
from logging.handlers import TimedRotatingFileHandler

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
LOG_FILE = os.path.join(LOG_DIR, "app.log")

logger = logging.getLogger("pilandingpage")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # One log file per day, rotated at midnight; anything older than 30 days
    # gets deleted automatically by the handler itself.
    file_handler = TimedRotatingFileHandler(LOG_FILE, when="midnight", backupCount=30, encoding="utf-8")
    file_handler.suffix = "%Y-%m-%d"

    console_handler = logging.StreamHandler()

    fmt = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
