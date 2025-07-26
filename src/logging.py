"""
Logging Module for the Whisper Client
Version: 1.6
Timestamp: 2025-04-20 16:33 CET

This module provides logging functionality for the Whisper Client.
It configures loggers, formatters, and handlers for different types of logs
and provides specialized logging functions for different components.
"""

import logging
import os
from datetime import datetime

import config

# Basis-Logger erstellen
logger = logging.getLogger("WhisperClient")
logger.setLevel(logging.DEBUG)


class WhisperFormatter(logging.Formatter):
    """Formatter that uses different formats based on log type."""

    def __init__(self, formats=None):
        super().__init__()
        self.formats = formats or config.LOG_FORMAT_FILE

    def format(self, record):
        # Choose format based on log type
        if hasattr(record, "log_type"):
            format_str = self.formats.get(record.log_type, self.formats["default"])
        else:
            format_str = self.formats["default"]

        # Set format and format record
        self._style._fmt = format_str
        return super().format(record)


def log_connection(logger, message, *args, **kwargs):
    """Log for connection events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.info(message, extra={"log_type": "connection"})


def log_audio(logger, message, *args, **kwargs):
    """Log for audio events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs

    if isinstance(message, str) and "bytes" in message:
        try:
            size = int(message.split()[1])
            logger.info(message, extra={"log_type": "audio", "size": size})
        except (ValueError, IndexError) as e:
            log_debug(logger, "Error parsing audio message size: %s", e)
            logger.info(message, extra={"log_type": "audio", "size": 0})
    else:
        logger.info(message, extra={"log_type": "audio", "size": 0})


def log_text(logger, message, *args, **kwargs):
    """Log for text events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.info(message, extra={"log_type": "text"})


def log_info(logger, message, *args, **kwargs):
    """Log for info events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.info(message, extra={"log_type": "info"})


def log_warning(logger, message, *args, **kwargs):
    """Log for warning events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.warning(message, extra={"log_type": "warning"})


def log_debug(logger, message, *args, **kwargs):
    """Log for debug events."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.debug(message, extra={"log_type": "debug"})


def log_error(logger, message, *args, **kwargs):
    """Log for errors."""
    logger = logging.getLogger(logger.name)
    if args or kwargs:
        message = message % args if args else message % kwargs
    logger.error(
        message,
        extra={
            "log_type": "error",
            "stack": getattr(message, "stack", ""),
            "size": getattr(message, "size", 0),
        },
    )


def get_logger():
    """Returns the global logger instance."""
    print("Initializing logger...")  # Debug output

    # Remove existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)

    # Create logs directory
    log_dir = os.path.dirname(config.REGRESSION_LOG_FILE)
    os.makedirs(log_dir, exist_ok=True)

    try:
        # Console Handler with UTF-8
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL_CONSOLE))
        console_formatter = WhisperFormatter(config.LOG_FORMAT_CONSOLE)
        console_handler.setFormatter(console_formatter)
        console_handler.stream.reconfigure(encoding="utf-8")  # type: ignore [attr-defined]
        logger.addHandler(console_handler)

        # Create logs directory
        log_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.LOG_DIR
        )
        os.makedirs(log_dir, exist_ok=True)
        print(f"Log directory: {log_dir}")  # Debug output

        # Log filename with local date
        current_date = datetime.now()
        print(f"Current date: {current_date}")  # Debug output
        log_file = os.path.join(log_dir, f"whisper_client_{current_date.strftime('%Y%m%d')}.log")
        print(f"Logging to: {log_file}")  # Debug output

        # File Handler with UTF-8 and special formatter
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL_FILE))
        file_formatter = WhisperFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

        # Regression Investigation Handler with detailed format
        regression_handler = logging.FileHandler(
            config.REGRESSION_LOG_FILE, encoding="utf-8", mode="w"
        )
        regression_handler.setLevel(logging.DEBUG)
        regression_formatter = WhisperFormatter(config.REGRESSION_LOG_FORMAT)
        regression_handler.setFormatter(regression_formatter)
        logger.addHandler(regression_handler)
        logger.info(
            "Regression Investigation Logger activated",
            extra={
                "log_type": "default",
                "details": "Server logs available at /home/michael/appdata/whisperlive/logs (WSL)",
            },
        )

    except Exception as e:
        print(f"Error initializing logger: {e}")
        # Fallback Console Handler without UTF-8
        fallback_handler = logging.StreamHandler()
        fallback_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(fallback_handler)

    return logger
