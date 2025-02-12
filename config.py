"""
Zentrale Konfigurationsdatei für den Whisper-Client
"""

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

# Whisper-Einstellungen
WHISPER_LANGUAGE = "de"
WHISPER_TASK = "transcribe"
WHISPER_USE_VAD = True
WHISPER_BACKEND = "faster_whisper"

# Logging-Einstellungen
LOG_DIR = "logs"
LOG_LEVEL_FILE = "DEBUG"
LOG_LEVEL_CONSOLE = "DEBUG"  # Temporär auf DEBUG für Tests
LOG_FORMAT_FILE = "%(asctime)s - %(levelname)s - %(message)s"
LOG_FORMAT_CONSOLE = "%(message)s"

# Hotkey-Einstellungen
HOTKEY_TOGGLE_RECORDING = "f13"  # Kann auf G915 programmiert werden
HOTKEY_EXIT = "f14"  # Kann auf G915 programmiert werden

# Text-Verarbeitung
MIN_OUTPUT_INTERVAL = 0.2  # Minimaler Abstand zwischen Textausgaben in Sekunden
MAX_RECENT_TRANSCRIPTIONS = 10  # Anzahl der gespeicherten letzten Transkriptionen
MAX_SENTENCE_WAIT = 2.0  # Maximale Wartezeit auf Satzende in Sekunden
SENTENCE_END_MARKERS = ['.', '!', '?', '...']  # Satzende-Marker für Textausgabe
