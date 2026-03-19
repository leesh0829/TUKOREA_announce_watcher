from __future__ import annotations

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

from announce_watcher.models import LoggingConfig


def configure_logging(config: LoggingConfig) -> logging.Logger:
    log_path = Path(config.path)
    log_path.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("announce_watcher")
    logger.setLevel(getattr(logging, config.level.upper(), logging.INFO))
    logger.handlers.clear()

    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")

    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=config.max_bytes,
        backupCount=config.backup_count,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    return logger
