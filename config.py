"""
Zentrale Konfigurationsdatei für den Whisper-Client
"""

# WebSocket-Einstellungen
WS_HOST = "localhost"
WS_PORT = 9090
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# WebSocket-Timing
WS_CONNECT_TIMEOUT = 5.0   # Timeout für Verbindungsaufbau
WS_READY_TIMEOUT = 10.0    # Timeout für Server-Ready Signal
WS_RETRY_DELAY = 2.0       # Initiale Wartezeit zwischen Reconnects
WS_FINAL_WAIT = 30.0       # Wartezeit auf letzte Texte nach Aufnahme-Ende
WS_THREAD_TIMEOUT = 5.0    # Timeout für Thread-Join
WS_MAX_RETRY_DELAY = 30.0  # Maximale Wartezeit zwischen Reconnects
WS_POLL_INTERVAL = 0.1     # Intervall für Verbindungsprüfung
WS_MESSAGE_WAIT = 1.0      # Wartezeit auf letzte Nachrichten nach Audio-Ende

# Audio-Einstellungen
AUDIO_CHUNK = 4096
AUDIO_FORMAT = "paInt16"  # wird in audio.py zu pyaudio.paInt16 konvertiert
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
AUDIO_DEVICE_INDEX = 1  # Poly BT700 Index

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
MIN_OUTPUT_INTERVAL = 0.5  # Minimaler Abstand zwischen Textausgaben in Sekunden
MAX_RECENT_TRANSCRIPTIONS = 10  # Anzahl der gespeicherten letzten Transkriptionen
MAX_SENTENCE_WAIT = 2.0  # Maximale Wartezeit auf Satzende in Sekunden
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
PROMPT_INPUT_DELAY = 0.3        # Verzögerung zwischen Zeichen bei Prompt-Eingabe
PROMPT_SUBMIT_DELAY = 0.5       # Verzögerung nach Enter-Taste
