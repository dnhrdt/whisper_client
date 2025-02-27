"""
Whisper Client Package
Version: 1.0
Timestamp: 2025-02-27 17:13 CET

This is the main package for the Whisper Client.
It initializes the logger and exports it for use by other modules.
"""
import sys

# Disable stdout buffering
sys.stdout.reconfigure(line_buffering=True)

# Logging is configured in src/logging.py
from .logging import logger, get_logger

# Initialize logger
logger = get_logger()

# Export logger for other modules
__all__ = ['logger']
