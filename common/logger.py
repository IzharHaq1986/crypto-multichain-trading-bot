# common/logger.py

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

def setup_logger(name: str, log_dir="logs"):
    Path(log_dir).mkdir(exist_ok=True)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Do not add duplicate handlers if logger already initialized
    if logger.handlers:
        return logger

    log_path = Path(log_dir) / f"{name}.log"

    # Rotating Log Handler:
    # - maxBytes=1MB
    # - backupCount=5 (keeps 5 rotated logs)
    handler = RotatingFileHandler(
        filename=log_path,
        maxBytes=1_000_000,   # 1 MB
        backupCount=5,        # keep 5 old log files
        encoding="utf-8"
    )

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)

    logger.addHandler(handler)

    return logger
