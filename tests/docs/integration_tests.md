# Integration Tests

## Server Flow Tests
Tests the complete data flow from server to text processing.

### Key Components
1. **WebSocket Communication**
   ```python
   # Test WebSocket connection with server ready check
   def test_websocket_connection():
       ws = WhisperWebSocket()
       connected = ws.connect()
       assert ws.is_ready()
   ```

2. **Audio Transmission**
   ```python
   # Test audio transmission with server ready state
   def test_audio_transmission():
       # Server must be ready
       ws.server_ready = True
       audio_sent = ws.send_audio(test_audio)
       assert audio_sent
   ```

3. **END_OF_AUDIO Handling**
   ```python
   # Test END_OF_AUDIO signal and final text reception
   def test_end_of_audio():
       signal_sent = ws.send_end_of_audio()
       # Wait for final server response
       time.sleep(config.WS_FINAL_WAIT)
       assert signal_sent
   ```

## Text Processing Tests
Tests sentence processing and deduplication.

### Test Cases
1. **Normal Sentence Processing**
   - Complete sentences
   - Sentence boundaries
   - Punctuation

2. **Deduplication**
   - Overlapping segments
   - Partial duplicates
   - Complete duplicates

3. **Incomplete Sentences**
   - Timeout behavior
   - Forced output
   - Buffer management

## Prompt Output Tests
Tests text insertion into active windows.

### Critical Paths
1. **Window Detection**
   - Find target window
   - Verify window state
   - Handle missing windows

2. **Text Insertion**
   - Clipboard operations
   - Keyboard simulation
   - Timing delays

3. **Error Recovery**
   - Lost window focus
   - Clipboard failures
   - Input delays

## Test Configuration
```python
# Test timeouts and delays
TEST_SUITE_TIMEOUT = 120    # Full suite timeout
TEST_SERVER_READY = 0.5     # Server ready check
TEST_AUDIO_PROCESS = 0.5    # Audio processing
TEST_TEXT_OUTPUT = 1.0      # Text output verification
```

## Running Tests
```bash
# Run all integration tests
python -m pytest tests/integration/

# Run specific test category
python -m pytest tests/integration/test_server_flow.py
python -m pytest tests/integration/test_text_processing.py
python -m pytest tests/integration/test_prompt_output.py
```

## Common Issues & Solutions

### Server Connection
- Issue: Server not ready in time
- Solution: Increase TEST_SERVER_READY timeout
- Check: Server logs for initialization

### Audio Processing
- Issue: Missing final segments
- Solution: Extend WS_FINAL_WAIT
- Check: Audio buffer completeness

### Text Output
- Issue: Incomplete sentences
- Solution: Adjust MAX_SENTENCE_WAIT
- Check: Text completion timestamps

## Test Development Guidelines

1. **New Tests**
   - Add setup/teardown
   - Document timing assumptions
   - Include failure scenarios

2. **Modifying Tests**
   - Update timing constants
   - Verify backward compatibility
   - Document changes

3. **Test Dependencies**
   - Server must be running
   - Clean environment required
   - Proper window focus needed
