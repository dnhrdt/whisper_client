# WhisperClient (Alpha)

A Python-based client for real-time German speech recognition using [WhisperLive](https://github.com/collabora/WhisperLive). This project is currently in **Alpha** stage.

## 🎯 Features

- Real-time audio recording and streaming
- WebSocket-based communication with WhisperLive
- Automatic text output to active applications via Windows SendMessage API
- Configurable hotkey control (F13/F14)
- Robust error handling and reconnect logic
- Optimized for German speech recognition
- Tumbling Window approach for audio processing

## ⚠️ Alpha Status Notice

This project is currently in **Alpha** stage. While the core functionality is implemented and working, you may encounter issues or limitations:

- Some error handling may be incomplete
- Documentation is still being improved
- Performance optimizations are ongoing
- Test coverage is not yet comprehensive

We welcome feedback and contributions to help improve the project!

## 🚀 Quick Start

```bash
# 1. Set up WhisperLive server first
# Follow instructions at: https://github.com/collabora/WhisperLive

# 2. Clone this repository
git clone https://github.com/dnhrdt/whisper_client.git
cd whisper_client

# 3. Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# 4. Install dependencies
pip install -r requirements.txt

# 5. Configure audio device in config.json if needed
# Default is "Poly BT700" - use list_devices.py to find your device

# 6. Start client
python main.py
```

## 📋 Prerequisites

- Python 3.12+
- [WhisperLive Server](https://github.com/collabora/WhisperLive)
- Windows (for keyboard simulation)
- Microphone

## 🔧 Configuration

Configuration is managed through `config.json`:
```json
{
  "audio": {
    "device": "Poly BT700",
    "format": "paInt16",
    "channels": 1,
    "rate": 16000,
    "chunk_size": 4096,
    "silence_threshold": 300
  },
  "server": {
    "url": "ws://localhost:9090",
    "reconnect": {
      "attempts": -1,
      "delay_ms": 3000,
      "timeout_ms": 5000
    }
  },
  "text": {
    "output_mode": "sendmessage",
    "prompt_settings": {
      "delay_between_chars_ms": 5,
      "delay_between_words_ms": 10,
      "use_win32_api": true
    }
  },
  "hotkeys": {
    "start_stop": "F13",
    "exit": "F14"
  }
}
```

## 🎛️ Audio Processing

The project uses a Tumbling Window approach for audio processing:

- Configurable window size (default: 2048 samples) and overlap (default: 25%)
- Linear crossfading for smooth transitions between windows
- Thread-safe queue-based processing
- Average latency of 130ms
- Float32 normalization for optimal audio quality

Detailed technical documentation:
- [System Architecture](docs/diagrams/architecture/system_modules.md)
- [Audio Processing Flow](docs/diagrams/sequence/audio_processing.md)
- [System Timing Parameters](docs/diagrams/timing/system_timings.md)

## 🧪 Tests

The project includes several test categories:

```bash
# Run all tests
python run_tests.py

# Run specific test categories
python run_tests.py --category timing
python run_tests.py --category integration
python run_tests.py --category speech
```

Current test coverage includes:
- WebSocket connection state tracking
- Audio processing with Tumbling Window
- Text processing and buffering
- SendMessage API performance
- Error handling and recovery

## 📚 Documentation

Our documentation follows the Memory Bank structure for comprehensive project understanding:

- **[Product Context](cline_docs/productContext.md)** - Core purpose and system architecture
- **[System Patterns](cline_docs/systemPatterns.md)** - Development standards and architectural patterns
- **[Technical Context](cline_docs/techContext.md)** - Core technologies and configuration
- **[Active Context](cline_docs/activeContext.md)** - Current development focus and recent changes
- **[Progress](cline_docs/progress.md)** - Task tracking and development status

Additional documentation:
- [Alpha Release Notes](docs/alpha_release_notes.md)
- [WebSocket Protocol](docs/websocket_protocol.md)
- [WebSocket Message Format](docs/websocket_message_format.md)

## 🤝 Contributing

We welcome contributions! See our [Contributing Guidelines](CONTRIBUTING.md) for details.

Current focus areas:

1. **Core Stability & Performance**
   - Long-running session reliability
   - Audio timing optimization (130ms latency advantage)
   - WebSocket connection robustness
   - Memory and resource management

2. **API Integration & Extensibility**
   - OpenAI-compatible API server mode
   - Docker containerization support
   - Cross-platform compatibility research
   - Backend flexibility for different transcription services

3. **Community & Ecosystem**
   - Integration with existing transcription UIs
   - Developer-friendly core library
   - Comprehensive documentation and examples
   - Performance benchmarking and comparison tools

## 📝 License

[MIT](LICENSE)

## 🙏 Acknowledgments

This project builds upon the excellent work of:

- [WhisperLive by Collabora](https://github.com/collabora/WhisperLive) - The server component that powers our speech recognition
- [OpenAI Whisper](https://github.com/openai/whisper) - The underlying speech recognition model
- [faster-whisper](https://github.com/guillaumekln/faster-whisper) - Optimized Whisper implementation
- All contributors and testers who have provided valuable feedback

WhisperClient is an independent project that integrates with WhisperLive but is not officially affiliated with Collabora or OpenAI.

## 📞 Support

- GitHub Issues for bugs and features
- Discussions for questions and ideas
