"""
Whisper Client Package
Version: 1.1
Timestamp: 2025-03-08 23:10 CET

This is the main package for the Whisper Client.
It initializes the logger and exports it for use by other modules.
"""

import sys

from .logging import get_logger

# Disable stdout buffering
sys.stdout.reconfigure(line_buffering=True)  # type: ignore [attr-defined]

# Initialize logger
logger = get_logger()

# Export logger for other modules
__all__ = ["logger"]
