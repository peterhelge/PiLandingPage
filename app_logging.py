import logging
import os
from logging.handlers import TimedRotatingFileHandler

from security import redact

# Credential files created later in this process should be owner-only.
os.umask(0o077)

LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)
try:
    if not os.path.islink(LOG_DIR):
        os.chmod(LOG_DIR, 0o700)
except OSError:
    pass
LOG_FILE = os.path.join(LOG_DIR, "app.log")


class RedactingFormatter(logging.Formatter):
    """Strips API keys and bearer tokens from the rendered log line, including tracebacks."""

    def format(self, record):
        return redact(logging.Formatter.format(self, record))


class _PrivateTimedRotatingFileHandler(TimedRotatingFileHandler):
    def _open(self):
        stream = super()._open()
        try:
            if not os.path.islink(self.baseFilename):
                os.chmod(self.baseFilename, 0o600)
        except OSError:
            pass
        return stream


logger = logging.getLogger("pilandingpage")
logger.setLevel(logging.INFO)

if not logger.handlers:
    # One log file per day, rotated at midnight; anything older than 30 days
    # gets deleted automatically by the handler itself.
    file_handler = _PrivateTimedRotatingFileHandler(
        LOG_FILE, when="midnight", backupCount=30, encoding="utf-8"
    )
    file_handler.suffix = "%Y-%m-%d"

    console_handler = logging.StreamHandler()

    fmt = RedactingFormatter("%(asctime)s %(levelname)s [%(name)s] %(message)s")
    file_handler.setFormatter(fmt)
    console_handler.setFormatter(fmt)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

# Library loggers that have no handler of their own end up on lastResort.
# Give that stream the same redaction so a token cannot land on stderr.
if logging.lastResort is not None and not isinstance(logging.lastResort.formatter, RedactingFormatter):
    logging.lastResort.setFormatter(RedactingFormatter("%(levelname)s:%(name)s:%(message)s"))
