"""
Whisper-Client Package
"""
import sys

# Disable stdout buffering
sys.stdout.reconfigure(line_buffering=True)

# Logging wird in src/logging.py konfiguriert
from .logging import logger, get_logger

# Initialisiere Logger
logger = get_logger()

# Exportiere den Logger für andere Module
__all__ = ['logger']
