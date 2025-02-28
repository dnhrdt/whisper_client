# Integration Tests
Version: 1.0
Timestamp: 2025-02-26 21:11 CET

## Server Flow Tests
Tests the complete data flow from server to text processing, with focus on German text handling.

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
Tests German sentence processing and deduplication.

### Test Cases
1. **Normal Sentence Processing**
   - Complete German sentences
   - German sentence boundaries
   - German punctuation rules
   - Umlauts and special characters

2. **Deduplication**
   - Overlapping German segments
   - Partial duplicates
   - Complete duplicates
   - German compound word handling

3. **Incomplete Sentences**
   - Timeout behavior
   - Forced output
   - Buffer management
   - German sentence completion

## Prompt Output Tests
Tests German text insertion into active windows.

### Critical Paths
1. **Window Detection**
   - Find target window
   - Verify window state
   - Handle missing windows
   - Unicode text support

2. **Text Insertion**
   - Clipboard operations with German text
   - Keyboard simulation for German characters
   - Timing delays
   - UTF-8 encoding handling

3. **Error Recovery**
   - Lost window focus
   - Clipboard failures
   - Input delays
   - Character encoding issues

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
- Verify: German model loading

### Audio Processing
- Issue: Missing final segments
- Solution: Extend WS_FINAL_WAIT
- Check: Audio buffer completeness
- Monitor: German word boundary detection

### Text Output
- Issue: Incomplete sentences
- Solution: Adjust MAX_SENTENCE_WAIT
- Check: Text completion timestamps
- Verify: German character encoding

### German Text Processing
- Issue: Compound word splitting
- Solution: Adjust word boundary detection
- Check: Sentence segmentation rules
- Monitor: Umlaut handling

## Test Development Guidelines

1. **New Tests**
   - Add setup/teardown
   - Document timing assumptions
   - Include failure scenarios
   - Test German language specifics

2. **Modifying Tests**
   - Update timing constants
   - Verify backward compatibility
   - Document changes
   - Maintain German test cases

3. **Test Dependencies**
   - Server must be running
   - Clean environment required
   - Proper window focus needed
   - German language model loaded

## German Language Considerations

1. **Text Processing**
   - Handle compound words
   - Respect German capitalization rules
   - Process Umlauts correctly
   - Maintain sentence structure

2. **Character Encoding**
   - UTF-8 for all text operations
   - Proper handling of German special characters
   - Clipboard encoding verification
   - Input method compatibility

3. **Test Cases**
   - Include common German phrases
   - Test compound word recognition
   - Verify punctuation rules
   - Check number formatting

4. **Error Handling**
   - German character encoding errors
   - Compound word segmentation issues
   - Sentence boundary detection
   - Special character validation
