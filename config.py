"""
Central configuration file for the Whisper Client
"""

# Base Timing Constants
BASE_DELAY = 0.1        # Basic delay for polling/checks
BASE_TIMEOUT = 2.0      # Basic timeout for threads/operations
BASE_RETRY = 2.0        # Basic wait time for retries
BASE_WAIT = 1.0         # Basic wait time for message processing

# Thread Management
THREAD_TIMEOUT = BASE_TIMEOUT          # Default thread timeout
WS_THREAD_TIMEOUT = THREAD_TIMEOUT     # WebSocket thread timeout
AUDIO_THREAD_TIMEOUT = THREAD_TIMEOUT  # Audio thread timeout
HOTKEY_THREAD_TIMEOUT = THREAD_TIMEOUT # Hotkey thread timeout
TERMINAL_THREAD_TIMEOUT = THREAD_TIMEOUT # Terminal thread timeout

# Polling and Checks
POLL_INTERVAL = BASE_DELAY             # Default polling interval
MAIN_POLL_INTERVAL = POLL_INTERVAL     # Main loop polling interval
WS_POLL_INTERVAL = POLL_INTERVAL       # WebSocket connection check
HOTKEY_POLL_INTERVAL = POLL_INTERVAL   # Hotkey check
TERMINAL_MONITOR_INTERVAL = BASE_DELAY * 100  # Terminal monitoring (10 seconds)

# Retry Mechanisms
RETRY_DELAY = BASE_RETRY               # Default retry delay
WS_RETRY_DELAY = RETRY_DELAY           # WebSocket reconnect delay
WS_RECONNECT_DELAY = RETRY_DELAY * 1.5 # Wait time before reconnect
WS_MAX_RETRY_DELAY = RETRY_DELAY * 15  # Maximum wait time (30 seconds)

# Wait Times for Message Processing
MESSAGE_WAIT = BASE_WAIT               # Default message processing
WS_MESSAGE_WAIT = MESSAGE_WAIT         # WebSocket message processing
WS_FINAL_WAIT = BASE_WAIT * 30        # Wait time for final texts

# Connection Timeouts
WS_CONNECT_TIMEOUT = BASE_TIMEOUT * 2.5  # Timeout for connection establishment
WS_READY_TIMEOUT = BASE_TIMEOUT * 5      # Timeout for server-ready signal

# Keyboard and Clipboard
KEY_PRESS_DELAY = BASE_DELAY * 0.5     # Delay between key presses
CLIPBOARD_TIMEOUT = BASE_WAIT          # Timeout for clipboard operations

# Error Handling
ERROR_DELAY = BASE_DELAY               # Wait time after errors
HOTKEY_ERROR_DELAY = ERROR_DELAY       # Hotkey error delay
HOTKEY_SHUTDOWN_WAIT = ERROR_DELAY     # Wait time for hotkey shutdown

# Text Processing
MIN_OUTPUT_INTERVAL = BASE_WAIT * 0.5  # Minimum interval between outputs
MAX_SENTENCE_WAIT = BASE_TIMEOUT       # Maximum wait time for sentence end

# Terminal Management
TERMINAL_INACTIVITY_TIMEOUT = 300      # Timeout for inactive terminals (5 minutes)

# Test Timeouts and Delays
TEST_SUITE_TIMEOUT = 120    # Timeout for test suite in seconds
TEST_SERVER_READY_DELAY = 0.5  # Wait time until server ready (seconds)
TEST_AUDIO_PROCESS_DELAY = 0.5  # Wait time for audio processing (seconds)

# WebSocket Settings
WS_HOST = "localhost"
WS_PORT = 9090
WS_URL = f"ws://{WS_HOST}:{WS_PORT}"

# Audio Settings
AUDIO_CHUNK = 4096
AUDIO_FORMAT = "paInt16"  # converted to pyaudio.paInt16 in audio.py
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
AUDIO_DEVICE_INDEX = 1  # Poly BT700 index
AUDIO_BUFFER_SECONDS = 1.0  # Seconds of audio per buffer

# Whisper Settings
WHISPER_LANGUAGE = "de"
WHISPER_TASK = "transcribe"
WHISPER_USE_VAD = True
WHISPER_BACKEND = "faster_whisper"

# Logging Settings
LOG_DIR = "logs"
LOG_LEVEL_FILE = "DEBUG"
LOG_LEVEL_CONSOLE = "DEBUG"  # Temporarily set to DEBUG for testing

# Special Logging Settings for Regression Investigation
REGRESSION_LOG_FILE = "logs/regression_investigation.log"
REGRESSION_LOG_FORMAT = {
    'default': "%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s",
    'connection': "%(asctime)s.%(msecs)03d - CONN - %(message)s",
    'audio': "%(asctime)s.%(msecs)03d - AUDIO - %(message)s [size=%(size)d bytes]",
    'text': "%(asctime)s.%(msecs)03d - TEXT - %(message)s",
    'error': "%(asctime)s.%(msecs)03d - ERROR - %(message)s\n%(stack)s"
}

# Logging Formats for Different Events
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

# Hotkey Settings
HOTKEY_TOGGLE_RECORDING = "f13"  # Can be programmed on G915
HOTKEY_EXIT = "f14"  # Can be programmed on G915

# Text Processing
MAX_RECENT_TRANSCRIPTIONS = 10  # Number of stored recent transcriptions
SENTENCE_END_MARKERS = ['.', '!', '?', '...']  # Sentence end markers for text output

# Output Settings
class OutputMode:
    """Available output modes"""
    CLIPBOARD = "clipboard"  # Text to clipboard + Ctrl+V
    PROMPT = "prompt"       # Direct prompt integration
    SENDMESSAGE = "sendmessage"  # Windows SendMessage API
    BOTH = "both"          # Both modes simultaneously

# Active output mode
OUTPUT_MODE = OutputMode.SENDMESSAGE  # Using SendMessage API for best performance

# Prompt Integration
PROMPT_WINDOW_TITLE = "Visual Studio Code"  # Window title for prompt detection
PROMPT_INPUT_DELAY = BASE_DELAY * 3         # Delay between characters in prompt input
PROMPT_SUBMIT_DELAY = BASE_DELAY * 5        # Delay after Enter key
