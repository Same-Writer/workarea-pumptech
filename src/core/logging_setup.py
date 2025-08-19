"""
Logging configuration for the PumpTech system.
"""

import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Optional

from ..config import get_settings


def setup_logging(
    log_file: Optional[str] = None, log_level: Optional[str] = None
) -> None:
    """
    Set up logging configuration for the application.

    Args:
        log_file: Optional log file path. If None, uses settings.
        log_level: Optional log level. If None, uses settings.
    """
    settings = get_settings().logging

    # Use provided values or fall back to settings
    if log_level is None:
        log_level = settings.level
    if log_file is None:
        log_file = settings.file_path

    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create formatter
    formatter = logging.Formatter(settings.format)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(numeric_level)

    # Remove existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # File handler (if specified)
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=settings.max_file_size, backupCount=settings.backup_count
        )
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    # Set specific logger levels for third-party libraries
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("influxdb_client").setLevel(logging.WARNING)

    # Log the configuration
    logger = logging.getLogger(__name__)
    logger.info(f"Logging configured: level={log_level}, file={log_file}")
