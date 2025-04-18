# Technical Context
Version: 1.3
Timestamp: 2025-03-03 21:42 CET

## Core Technologies

### Audio Stack
- PyAudio for microphone access
  * 4-Chunk buffer (1 second total)
  * float32 normalization (-1 to 1)
  * Device availability checks
  * Thread-safe management
- Tumbling Window implementation
  * Configurable window size and overlap
  * Linear crossfading for smooth transitions
  * 130ms average latency
  * Thread-safe queue-based processing
- AudioProcessor class for integration
  * Callback chain for processed audio
  * Clean start/stop functionality
  * Test mode support
- Default device: Poly BT700
- Device configuration via config.json
- Device listing via list_devices.py

### Server Communication
- WebSocket-client for server communication
- Server connection details:
  * Default port: 9090
  * WebSocket URL: ws://localhost:9090/client
  * JSON message format
- Connection state tracking system
  * 11 distinct states (DISCONNECTED, CONNECTING, CONNECTED, etc.)
  * Thread-safe state transitions with connection_lock
  * Detailed logging for state changes
- Multiple parallel connections prevention
  * Client and session ID tracking
  * Class-level instance tracking with _active_instances dictionary
  * Connection throttling to prevent rapid reconnection attempts
  * cleanup_all_instances class method
- END_OF_AUDIO signal handling
- Reconnection strategy:
  * Unlimited reconnection attempts (-1)
  * Throttled reconnection with configurable delay
  * Connection timeout with proper error states

### Windows Integration
- pywin32 for Windows API
- Text input methods:
  * Windows SendMessage API implemented (WM_CHAR/WM_SETTEXT)
  * Automatic fallback to clipboard if SendMessage fails
  * VS Code-specific window and control detection
  * 99% performance improvement over clipboard method
- Memory-based text buffering
  * TextBuffer class with configurable size and age limits
  * TextSegment dataclass for structured segment storage
  * Automatic cleanup of old segments
  * Improved duplicate detection with temporal context
  * Thread-safe implementation with proper locking

## Configuration System

### Audio Settings
```python
AUDIO_DEVICE = "Poly BT700"
AUDIO_FORMAT = "paInt16"
AUDIO_CHANNELS = 1
AUDIO_RATE = 16000
AUDIO_CHUNK = 4096
SILENCE_THRESHOLD = 300
```

### Timing Constants
```python
# Base timing constants
BASE_DELAY = 0.1        # Basic delay for polling/checks
BASE_TIMEOUT = 2.0      # Basic timeout for threads/operations
BASE_RETRY = 2.0        # Basic wait time for retries
BASE_WAIT = 1.0         # Basic wait time for message processing

# Thread timeouts
THREAD_TIMEOUT = BASE_TIMEOUT          # Default thread timeout
WS_THREAD_TIMEOUT = THREAD_TIMEOUT     # WebSocket thread timeout
AUDIO_THREAD_TIMEOUT = THREAD_TIMEOUT  # Audio thread timeout

# WebSocket specific timing
WS_RECONNECT_DELAY = 3.0               # Delay between reconnection attempts
WS_CONNECT_TIMEOUT = 5.0               # Timeout for connection establishment
WS_READY_TIMEOUT = 5.0                 # Timeout for ready state
WS_FINAL_WAIT = 20.0                   # Wait time for final text after END_OF_AUDIO
WS_MESSAGE_WAIT = 0.2                  # Wait time between message processing

# Audio processing timing
TUMBLING_WINDOW_SIZE = 4096            # Window size in samples
TUMBLING_WINDOW_OVERLAP = 0.5          # Overlap ratio (0.0-1.0)
AUDIO_PROCESSOR_QUEUE_SIZE = 10        # Maximum queue size for audio processor
```

### System Runtime Logging
Note: This section describes technical system logging during runtime. For development change tracking, see system_patterns.md.

- Log paths:
  * Server: `/home/michael/appdata/whisperlive/logs/server.log` (W:\)
  * Client: `d:\dev\whisper_client\logs\whisper_client_[DATE].log`
- Log formats:
 ```python
  LOG_FORMAT = {
      'default': "%(asctime)s - %(levelname)s - %(message)s",
      'connection': "%(asctime)s - CONNECTION: %(message)s",
      'audio': "%(asctime)s - AUDIO: %(message)s",
      'text': "%(asctime)s - TEXT: %(message)s",
      'error': "%(asctime)s - ERROR: %(message)s"
  }
  ```

### Whisper Integration
```python
WHISPER_LANGUAGE = "de"
WHISPER_TASK = "transcribe"
WHISPER_USE_VAD = True
WHISPER_BACKEND = "faster_whisper"
```

## Technical Constraints

### Server Constraints
- Internal buffer size unknown
- Processing triggers not documented
- Batch processing strategy unclear
- Buffer optimization pending research

### Whisper Configuration Constraints
- Model parameters need documentation
- Segmentation logic requires clarification
- VAD settings to be determined
- Performance impact analysis pending

### System Requirements
- Windows OS (pywin32 dependency)
- Python >=3.8
- Audio device compatibility
- Network connectivity needs

## Development Setup

### VS Code Configuration
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "files.eol": "\n",
  "files.insertFinalNewline": true
}
```

### Line Ending Configuration
- .gitattributes controls line endings:
  ```
  * text=auto
  *.py text eol=lf
  *.md text eol=lf
  *.txt text eol=lf
  *.json text eol=lf
  *.bat text eol=crlf
  *.cmd text eol=crlf
  *.ps1 text eol=crlf
  ```

### Required Extensions
- Python
- Pylance
- Black Formatter
- Git History
- GitLens

### Build System
- PyInstaller for executable creation
- Build scripts in deployment/
- Autostart configuration options
- Installation procedures
- Line endings preserved in builds
