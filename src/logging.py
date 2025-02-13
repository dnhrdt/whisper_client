"""
Logging-Modul für den Whisper-Client
"""
import os
from datetime import datetime
import logging
import config

# Basis-Logger erstellen
logger = logging.getLogger("WhisperClient")
logger.setLevel(logging.DEBUG)

class WhisperFormatter(logging.Formatter):
    """Formatter der verschiedene Formate basierend auf Log-Typ verwendet"""
    
    def __init__(self, formats=None):
        super().__init__()
        self.formats = formats or config.LOG_FORMAT_FILE
    
    def format(self, record):
        # Wähle Format basierend auf Log-Typ
        if hasattr(record, 'log_type'):
            format_str = self.formats.get(record.log_type, self.formats['default'])
        else:
            format_str = self.formats['default']
            
        # Setze Format und formatiere Record
        self._style._fmt = format_str
        return super().format(record)

def log_connection(logger, message):
    """Log für Verbindungsereignisse"""
    logger = logging.getLogger(logger.name)
    logger.info(message, extra={'log_type': 'connection'})

def log_audio(logger, message):
    """Log für Audio-Ereignisse"""
    logger = logging.getLogger(logger.name)
    logger.info(message, extra={'log_type': 'audio'})

def log_text(logger, message):
    """Log für Text-Ereignisse"""
    logger = logging.getLogger(logger.name)
    logger.info(message, extra={'log_type': 'text'})

def log_error(logger, message):
    """Log für Fehler"""
    logger = logging.getLogger(logger.name)
    logger.error(message, extra={'log_type': 'error'})

def get_logger():
    """Gibt die globale Logger-Instanz zurück"""
    print("Initialisiere Logger...")  # Debug-Ausgabe
    
    # Entferne existierende Handler
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    try:
        # Console Handler mit UTF-8
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, config.LOG_LEVEL_CONSOLE))
        console_formatter = WhisperFormatter(config.LOG_FORMAT_CONSOLE)
        console_handler.setFormatter(console_formatter)
        console_handler.stream.reconfigure(encoding='utf-8')
        logger.addHandler(console_handler)
        
        # Logs-Verzeichnis erstellen
        log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), config.LOG_DIR)
        os.makedirs(log_dir, exist_ok=True)
        print(f"Log-Verzeichnis: {log_dir}")  # Debug-Ausgabe
        
        # Log-Dateiname mit lokalem Datum
        current_date = datetime.now()
        print(f"Aktuelles Datum: {current_date}")  # Debug-Ausgabe
        log_file = os.path.join(log_dir, f"whisper_client_{current_date.strftime('%Y%m%d')}.log")
        print(f"Logging to: {log_file}")  # Debug-Ausgabe
        
        # File Handler mit UTF-8 und speziellem Formatter
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(getattr(logging, config.LOG_LEVEL_FILE))
        file_formatter = WhisperFormatter()
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Zusätzlicher Handler für _whisperlive_logs.txt
        test_handler = logging.FileHandler('_whisperlive_logs.txt', encoding='utf-8', mode='a')
        test_handler.setLevel(logging.INFO)
        test_handler.setFormatter(WhisperFormatter())
        logger.addHandler(test_handler)
        
    except Exception as e:
        print(f"Fehler bei Logger-Initialisierung: {e}")
        # Fallback Console Handler ohne UTF-8
        fallback_handler = logging.StreamHandler()
        fallback_handler.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(fallback_handler)
    
    return logger
