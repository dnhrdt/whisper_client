"""
Logging-Modul für den Whisper-Client
"""
import os
import logging
from datetime import datetime
import sys
import config

class WhisperLogger:
    def __init__(self, name="WhisperClient"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.DEBUG)
        self._setup_handlers()
        
    def _setup_handlers(self):
        """Logger-Handler einrichten"""
        # Logs-Verzeichnis erstellen
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.LOG_DIR)
        os.makedirs(log_dir, exist_ok=True)
        
        # Log-Dateiname mit Datum
        log_file = os.path.join(log_dir, f"whisper_client_{datetime.now().strftime('%Y%m%d')}.log")
        
        # File Handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL_FILE))
        file_formatter = logging.Formatter(config.LOG_FORMAT_FILE)
        file_handler.setFormatter(file_formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL_CONSOLE))
        console_formatter = logging.Formatter(config.LOG_FORMAT_CONSOLE)
        console_handler.setFormatter(console_formatter)
        
        # Handler hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def debug(self, msg, **kwargs):
        """Debug-Level Log"""
        self.logger.debug(msg, **kwargs)
    
    def info(self, msg, **kwargs):
        """Info-Level Log"""
        self.logger.info(msg, **kwargs)
    
    def warning(self, msg, **kwargs):
        """Warning-Level Log"""
        self.logger.warning(msg, **kwargs)
    
    def error(self, msg, **kwargs):
        """Error-Level Log"""
        self.logger.error(msg, **kwargs)
    
    def critical(self, msg, **kwargs):
        """Critical-Level Log"""
        self.logger.critical(msg, **kwargs)

# Globale Logger-Instanz
logger = WhisperLogger()

def get_logger():
    """Gibt die globale Logger-Instanz zurück"""
    return logger
