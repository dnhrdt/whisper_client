# WhisperClient

A Python-based client for real-time speech recognition using WhisperLive.

## 🎯 Features

- Real-time audio recording and streaming
- WebSocket-based communication with WhisperLive
- Automatic text output to active applications
- Configurable hotkey control (F13/F14)
- Robust error handling and reconnect logic

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/yourusername/whisper_client.git
cd whisper_client

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Start client
python main.py
```

## 📋 Prerequisites

- Python 3.12+
- WhisperLive Server
- Windows (for keyboard simulation)
- Microphone

## 🔧 Configuration

Configuration is managed through `config.json`:
- Audio settings (format, rate, buffer)
- WebSocket parameters (host, port, timeouts)
- Hotkey definitions
- Logging options

## 🎛️ Timing System

The project uses a sophisticated timing system for optimal performance:

```mermaid
flowchart TD
    A[Audio Recording] -->|1.0s Buffer| B[WebSocket]
    B -->|5.0s Timeout| C[Server]
    C -->|30.0s Final Wait| D[Text Output]
```

Detailed diagrams and documentation:
- [System Architecture](docs/diagrams/architecture/system_modules.md)
- [Sequence Flow](docs/diagrams/sequence/audio_processing.md)
- [Timing Overview](docs/diagrams/timing/system_timings.md)

## 🧪 Tests

```bash
# Run timing tests
python run_tests.py
```

The tests analyze:
- Audio streaming performance
- WebSocket communication
- Text processing times
- Error scenarios

## 📚 Documentation

Our documentation follows the Memory Bank structure for comprehensive project understanding:

- **Product Context** - Core purpose and system architecture
- **System Patterns** - Development standards and architectural patterns
- **Technical Context** - Core technologies and configuration
- **Active Context** - Current development focus and recent changes
- **Progress** - Task tracking and development status

Additional documentation:
- [Roadmap](docs/roadmap.md)
- [Test Specifications](tests/speech_test_cases.md)

## 🤝 Contributing

We welcome contributions! Current focus areas:

1. **Server Integration**
   - Understanding WhisperLive server parameters
   - Timing optimization
   - Protocol documentation

2. **Performance**
   - Audio streaming optimization
   - Latency minimization
   - Resource efficiency

3. **User Experience**
   - GUI development
   - Configuration interface
   - Installation wizard

### Development Workflow

1. Create/select an issue
2. Create branch: `feature/name` or `fix/name`
3. Make changes following project standards
4. Create pull request
5. Await code review

## 📝 License

[MIT](LICENSE)

## 🙏 Acknowledgments

- [WhisperLive](https://github.com/whisperlive) for the server
- [OpenAI Whisper](https://github.com/openai/whisper) for the speech model
- All contributors and testers

## 📞 Support

- GitHub Issues for bugs and features
- Discussions for questions and ideas
- [Regression Investigation Log](docs/investigations/regression_20250214.md) for known issues
