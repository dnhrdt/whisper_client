# Product Context
Version: 1.2
Timestamp: 2025-02-26 20:42 CET

## Core Purpose
- Real-time German speech recognition via WhisperLive
- Direct text output to active applications
- Reliable audio stream processing
- Task history tracking

Note: While the project documentation is in English for broader accessibility,
the primary focus is on German speech recognition. Test cases are maintained
in German to ensure accurate validation of the core functionality.

## Main Challenges

### 1. Stability
- Continuous audio processing
- Reliable WebSocket connection
- Precise timing control
- Error recovery

### 2. Integration
- Windows application interaction
- Text insertion methods
- Audio stream handling
- Server communication

### 3. User Experience
- Minimal latency
- Predictable behavior
- Clear status feedback
- Easy configuration

## Setup Requirements

### Audio Device
- Default: Poly BT700 (recommended)
- Device configuration via config.json
- Use list_devices.py to find your device:
  ```bash
  python list_devices.py
  # Shows all available audio devices with indices
  ```

### Server Setup
- WhisperLive Server required
- Default port: 9090
- Docker deployment recommended:
  ```bash
  # Server setup via Docker
  docker pull whisperlive
  docker run -p 9090:9090 whisperlive
  ```

### Keyboard Requirements
- Requires F13/F14 keys
- Recommended: Logitech G915
- Key Programming:
  * F13: Start/Stop Recording
  * F14: Exit Application
- Configure via Logitech G HUB

## System Architecture

### Main Components

1. **WebSocket Client**
   - Server connection management
   - Automatic reconnects
   - JSON message handling
   - Response processing

2. **Text Insertion**
   - Current: Clipboard + Ctrl+V
   - Planned: Windows SendMessage API
   - WM_CHAR/WM_SETTEXT methods
   - Memory-based buffering

3. **Audio Recording**
   - PyAudio implementation
   - Threaded recording
   - Float32 normalization
   - Buffer management

4. **Logging System**
   - File and console output
   - Daily log rotation
   - Structured error handling
   - Debug information

## Repository Structure
```
.
├── docs/
│   ├── project.md       # Main documentation
│   ├── roadmap.md      # Development roadmap
│   └── development.md  # Developer documentation
├── src/
│   ├── audio.py        # Audio recording
│   ├── websocket.py    # Server communication
│   ├── text.py         # Text processing
│   ├── logging.py      # Logging system
│   └── utils.py        # Helper functions
├── tests/              
│   ├── speech_test_cases.md     
│   ├── speech_test_progress.json
│   └── test_*.py       # Test modules
└── tools/
    └── list_devices.py  # Audio device listing
```

## System Requirements
- Python >=3.8
- Windows OS
- Audio device support
- Network connectivity
- See requirements.txt for packages

## Development Tools
- VS Code as primary IDE
- Python virtual environment
- Git for version control
- Docker for server deployment

## Core Workflows

### Audio Processing Flow
1. Microphone input capture
2. Buffer management
3. Data normalization
4. Stream to server

### Text Processing Flow
1. Server response handling
2. Text formatting
3. Window targeting
4. Output delivery

### Error Recovery Flow
1. Error detection
2. Automatic reconnection
3. Buffer clearing
4. State restoration
