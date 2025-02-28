# Technical Context
Version: 1.2
Timestamp: 2025-02-26 20:42 CET

## Core Technologies

### Audio Stack
- PyAudio for microphone access
  * 4-Chunk buffer (1 second total)
  * float32 normalization (-1 to 1)
  * Device availability checks
  * Thread-safe management
- Default device: Poly BT700
- Device configuration via config.json
- Device listing via list_devices.py

### Server Communication
- WebSocket-client for server communication
- Default port: 9090
- Reconnection strategy:
  * Unlimited reconnection attempts (-1)
  * 3s delay between attempts
  * 5s connection timeout

### Windows Integration
- pywin32 for Windows API
- Text input methods:
  * Current: Clipboard + Ctrl+V
  * Planned: SendMessage API (WM_CHAR/WM_SETTEXT)
  * Memory-based buffering

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
BASE_DELAY = 0.1        # Basic delay for polling/checks  
BASE_TIMEOUT = 2.0      # Basic timeout for threads/operations
BASE_RETRY = 2.0        # Basic wait time for retries
BASE_WAIT = 1.0         # Basic wait time for message processing

THREAD_TIMEOUT = BASE_TIMEOUT          # Default thread timeout
WS_THREAD_TIMEOUT = THREAD_TIMEOUT     # WebSocket thread timeout
AUDIO_THREAD_TIMEOUT = THREAD_TIMEOUT  # Audio thread timeout
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
