"""
Zentrale Konfigurationsdatei für den Whisper-Client
"""

# Basis-Timing-Konstanten
BASE_DELAY = 0.1        # Grundlegende Verzögerung für Polling/Checks
BASE_TIMEOUT = 2.0      # Grundlegender Timeout für Threads/Operationen
BASE_RETRY = 2.0        # Grundlegende Wartezeit für Retries
BASE_WAIT = 1.0        # Grundlegende Wartezeit für Nachrichten/Verarbeitung

# Thread-Management
THREAD_TIMEOUT = BASE_TIMEOUT          # Standard Thread-Timeout
WS_THREAD_TIMEOUT = THREAD_TIMEOUT     # WebSocket Thread-Timeout
AUDIO_THREAD_TIMEOUT = THREAD_TIMEOUT  # Audio Thread-Timeout
HOTKEY_THREAD_TIMEOUT = THREAD_TIMEOUT # Hotkey Thread-Timeout
TERMINAL_THREAD_TIMEOUT = THREAD_TIMEOUT # Terminal Thread-Timeout

# Polling und Checks
POLL_INTERVAL = BASE_DELAY             # Standard Polling-Intervall
WS_POLL_INTERVAL = POLL_INTERVAL       # WebSocket Verbindungsprüfung
HOTKEY_POLL_INTERVAL = POLL_INTERVAL   # Hotkey-Prüfung
TERMINAL_MONITOR_INTERVAL = BASE_DELAY * 100  # Terminal-Überwachung (10 Sekunden)

# Retry-Mechanismen
RETRY_DELAY = BASE_RETRY               # Standard Retry-Delay
WS_RETRY_DELAY = RETRY_DELAY           # WebSocket Reconnect-Delay
WS_RECONNECT_DELAY = RETRY_DELAY * 1.5 # Wartezeit vor Reconnect
WS_MAX_RETRY_DELAY = RETRY_DELAY * 15  # Maximale Wartezeit (30 Sekunden)

# Wartezeiten für Nachrichten/Verarbeitung
MESSAGE_WAIT = BASE_WAIT               # Standard Nachrichtenverarbeitung
WS_MESSAGE_WAIT = MESSAGE_WAIT         # WebSocket Nachrichtenverarbeitung
WS_FINAL_WAIT = BASE_WAIT * 30        # Wartezeit auf letzte Texte

# Verbindungs-Timeouts
WS_CONNECT_TIMEOUT = BASE_TIMEOUT * 2.5  # Timeout für Verbindungsaufbau
WS_READY_TIMEOUT = BASE_TIMEOUT * 5     # Timeout für Server-Ready Signal

# Tastatur und Clipboard
KEY_PRESS_DELAY = BASE_DELAY * 0.5     # Verzögerung zwischen Tastendrücken
CLIPBOARD_TIMEOUT = BASE_WAIT          # Timeout für Clipboard-Operationen

# Fehlerbehandlung
ERROR_DELAY = BASE_DELAY               # Wartezeit nach Fehlern
HOTKEY_ERROR_DELAY = ERROR_DELAY       # Hotkey Fehler-Delay
HOTKEY_SHUTDOWN_WAIT = ERROR_DELAY     # Wartezeit für Hotkey-Shutdown

# Text-Verarbeitung
MIN_OUTPUT_INTERVAL = BASE_WAIT * 0.5  # Minimaler Abstand zwischen Ausgaben
MAX_SENTENCE_WAIT = BASE_TIMEOUT       # Maximale Wartezeit auf Satzende

# Terminal-Management
TERMINAL_INACTIVITY_TIMEOUT = 300      # Timeout für inaktive Terminals (5 Minuten)

# WebSocket-Einstellungen
WS_HOST = "localhost"
WS_PORT = 9090
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# Audio-Einstellungen
AUDIO_CHUNK = 4096
AUDIO_FORMAT = "paInt16"  # wird in audio.py zu pyaudio.paInt16 konvertiert
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
AUDIO_DEVICE_INDEX = 1  # Poly BT700 Index
AUDIO_BUFFER_SECONDS = 1.0  # Sekunden Audio pro Puffer

# Whisper-Einstellungen
WHISPER_LANGUAGE = "de"
WHISPER_TASK = "transcribe"
WHISPER_USE_VAD = True
WHISPER_BACKEND = "faster_whisper"

# Logging-Einstellungen
LOG_DIR = "logs"
LOG_LEVEL_FILE = "DEBUG"
LOG_LEVEL_CONSOLE = "DEBUG"  # Temporär auf DEBUG für Tests

# Spezielle Logging-Einstellungen für Regression-Untersuchung
REGRESSION_LOG_FILE = "logs/regression_investigation.log"
REGRESSION_LOG_FORMAT = {
    'default': "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    'connection': "%(asctime)s.%(msecs)03d - CONN - %(message)s",
    'audio': "%(asctime)s.%(msecs)03d - AUDIO - %(message)s [size=%(size)d bytes]",
    'text': "%(asctime)s.%(msecs)03d - TEXT - %(message)s",
    'error': "%(asctime)s.%(msecs)03d - ERROR - %(message)s\n%(stack)s"
}

# Logging-Formate für verschiedene Ereignisse
LOG_FORMAT_FILE = {
    'default': "%(asctime)s - %(levelname)s - %(message)s",
    'connection': "%(asctime)s - CONNECTION: %(message)s",
    'audio': "%(asctime)s - AUDIO: %(message)s",
    'text': "%(asctime)s - TEXT: %(message)s",
    'error': "%(asctime)s - ERROR: %(message)s"
}
LOG_FORMAT_CONSOLE = {
    'default': "%(message)s",
    'connection': "🔌 %(message)s",
    'audio': "🎤 %(message)s",
    'text': "📝 %(message)s",
    'error': "❌ %(message)s"
}

# Hotkey-Einstellungen
HOTKEY_TOGGLE_RECORDING = "f13"  # Kann auf G915 programmiert werden
HOTKEY_EXIT = "f14"  # Kann auf G915 programmiert werden

# Text-Verarbeitung
MAX_RECENT_TRANSCRIPTIONS = 10  # Anzahl der gespeicherten letzten Transkriptionen
SENTENCE_END_MARKERS = ['.', '!', '?', '...']  # Satzende-Marker für Textausgabe

# Ausgabe-Einstellungen
class OutputMode:
    """Verfügbare Ausgabemodi"""
    CLIPBOARD = "clipboard"  # Text in Zwischenablage + Strg+V
    PROMPT = "prompt"       # Direkte Prompt-Integration
    BOTH = "both"          # Beide Modi gleichzeitig

# Aktiver Ausgabemodus
OUTPUT_MODE = OutputMode.BOTH

# Prompt-Integration
PROMPT_WINDOW_TITLE = "Visual Studio Code"  # Fenstertitel für Prompt-Erkennung
PROMPT_INPUT_DELAY = BASE_DELAY * 3        # Verzögerung zwischen Zeichen bei Prompt-Eingabe
PROMPT_SUBMIT_DELAY = BASE_DELAY * 5       # Verzögerung nach Enter-Taste
