# Product Context
Version: 1.3
Timestamp: 2025-03-03 21:40 CET

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
   - Connection state tracking system with 11 distinct states
   - Multiple parallel connections prevention
   - Automatic reconnects with throttling
   - Thread-safe state transitions
   - Detailed logging for state changes
   - END_OF_AUDIO signal handling

2. **Text Insertion**
   - Windows SendMessage API implemented
   - Automatic fallback to clipboard if SendMessage fails
   - Memory-based buffering with TextBuffer class
   - Thread-safe text processing

3. **Audio Processing**
   - PyAudio implementation for recording
   - Tumbling Window with configurable size and overlap
   - Linear crossfading for smooth transitions
   - Thread-safe queue-based processing
   - AudioProcessor class for integration
   - Float32 normalization
   - Efficient buffer management

4. **Logging System**
   - File and console output
   - Daily log rotation
   - Structured error handling
   - Debug information

## Repository Structure
```
.
├── cline_docs/                  # Memory Bank documentation
│   ├── activeContext.md         # Current development state
│   ├── productContext.md        # Product overview and purpose
│   ├── progress.md              # Development progress tracking
│   ├── systemPatterns.md        # Development patterns and workflows
│   └── techContext.md           # Technical implementation details
├── docs/
│   ├── diagrams/               # System architecture diagrams
│   ├── investigations/         # Analysis of specific issues
│   ├── research/               # Research on related technologies
│   ├── testing/                # Test documentation
│   ├── roadmap.md              # Development roadmap
│   ├── websocket_protocol.md   # WebSocket protocol documentation
│   └── windows_sendmessage_api.md # SendMessage API documentation
├── logs/
│   ├── increments/             # Incremental development logs
│   ├── main.json               # Critical changes log
│   └── archive/                # Archived logs
├── src/
│   ├── audio.py                # Audio recording and processing
│   ├── websocket.py            # Server communication
│   ├── text.py                 # Text processing
│   ├── logging.py              # Logging system
│   ├── terminal.py             # Terminal management
│   ├── hotkeys.py              # Keyboard input handling
│   └── utils.py                # Helper functions
├── tests/
│   ├── integration/            # Integration tests
│   ├── timing/                 # Timing tests
│   ├── speech/                 # Speech recognition tests
│   ├── poc/                    # Proof of concept tests
│   ├── docs/                   # Test documentation
│   └── run_tests.py            # Test runner
└── tools/
    └── list_devices.py         # Audio device listing
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
2. Tumbling Window processing with overlap
3. Linear crossfading between windows
4. Queue-based buffer management
5. Float32 normalization
6. Stream to server via WebSocket

### Text Processing Flow
1. Server response handling
2. Text segmentation and buffering
3. Duplicate detection with temporal context
4. Sentence boundary detection
5. Window targeting with SendMessage API
6. Automatic fallback to clipboard if needed

### Error Recovery Flow
1. Error detection with specific error states
2. Automatic reconnection with throttling
3. Buffer clearing and resource management
4. State restoration with proper state transitions
5. Detailed logging for troubleshooting
6. Graceful degradation with fallback mechanisms
