import logging
import sys
from typing import Any
from app.core.config import settings


class RequestIdFilter(logging.Filter):
    """Filter that injects request_id into log records if present."""

    def filter(self, record: logging.LogRecord) -> bool:
        if not hasattr(record, "request_id"):
            record.request_id = "-"
        return True


def setup_logging() -> logging.Logger:
    """Configures application logging with a clean, standardized format."""
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO

    logger = logging.getLogger("vizmind")
    logger.setLevel(log_level)

    # Avoid duplicate handlers if setup is called multiple times
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(log_level)

        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(request_id)s] | %(name)s.%(module)s:%(lineno)d - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        handler.setFormatter(formatter)
        handler.addFilter(RequestIdFilter())
        logger.addHandler(handler)

    return logger


logger = setup_logging()
