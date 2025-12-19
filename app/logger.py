import logging
import sys
from typing import Optional


def get_logger(name: Optional[str] = None, level: int = logging.INFO, logfile: str = "server.log"):
    """Create or return a configured logger.

    - Logs to stdout (so `nohup`/uvicorn captures it) and to `server.log` file.
    - Idempotent: if handlers already attached, returns existing logger.
    """
    logger_name = name or "spikeai"
    logger = logging.getLogger(logger_name)
    if logger.handlers:
        return logger

    logger.setLevel(level)
    fmt = "%(asctime)s %(levelname)s [%(name)s] %(message)s"
    formatter = logging.Formatter(fmt)

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(formatter)
    logger.addHandler(sh)

    try:
        fh = logging.FileHandler(logfile)
        fh.setFormatter(formatter)
        logger.addHandler(fh)
    except Exception:
        # If file cannot be opened, continue with stdout only
        logger.debug("Could not attach file handler")

    return logger
