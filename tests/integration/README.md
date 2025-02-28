# Integration Tests
Version: 1.0
Timestamp: 2025-02-26 21:13 CET

## Purpose
This directory contains integration tests for the WhisperClient system, focusing on WebSocket communication, text processing, and system integration. These tests are Priority 2 in our test strategy, building on the foundation of stable timing tests.

## Documentation
Detailed documentation can be found in:
- [Test Architecture](../../docs/testing/test_architecture.md)
- [Integration Tests Documentation](../../docs/testing/integration_tests.md)

## Directory Structure
```
integration/
├── test_websocket.py    # Connection handling tests
├── test_text_proc.py    # Text processing tests
└── test_output.py       # Basic output tests
```

## Test Components

### WebSocket Tests
- Connection establishment
- Server ready checks
- Audio transmission
- END_OF_AUDIO handling
- Error recovery

### Text Processing Tests
- German sentence processing
- Deduplication handling
- Incomplete sentence handling
- Special character handling
- Compound word processing

### Output Tests
- Window detection
- Text insertion
- German character encoding
- Clipboard operations
- Error scenarios

## Running Tests
```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific test category
python -m pytest tests/integration/test_websocket.py
python -m pytest tests/integration/test_text_proc.py
python -m pytest tests/integration/test_output.py
```

## Test Configuration
```python
# Test timeouts and delays
TEST_SUITE_TIMEOUT = 120    # Full suite timeout
TEST_SERVER_READY = 0.5     # Server ready check
TEST_AUDIO_PROCESS = 0.5    # Audio processing
TEST_TEXT_OUTPUT = 1.0      # Text output verification

# German language settings
WHISPER_LANGUAGE = "de"     # German language model
GERMAN_CHARS = "äöüßÄÖÜ"    # Special German characters to test
```

## Success Criteria
1. Reliable WebSocket connections
2. Accurate German text processing
3. Proper text output handling
4. Error recovery functionality
5. German character support

## Current Status
- [ ] test_websocket.py - To be implemented
- [ ] test_text_proc.py - To be implemented
- [ ] test_output.py - To be implemented

## Next Steps
1. Implement WebSocket connection tests
2. Implement German text processing tests
3. Implement output handling tests
4. Document integration test results
5. Verify German language support

## Dependencies
- Stable timing test results
- Running WhisperLive server
- German language model loaded
- Proper test environment setup

## Test Environment Requirements
1. Clean system state
2. No conflicting applications
3. Proper window focus handling
4. UTF-8 encoding support
5. German keyboard layout support
