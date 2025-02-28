# Test Inventory
Version: 1.2
Timestamp: 2025-02-26 23:04 CET

## Language Policy
- Documentation in English for broader accessibility
- German docstrings preserved in source code
- Test output messages and logs in English
- German speech test cases preserved (core functionality)

## Document Purpose
This document provides a comprehensive inventory of all existing tests, their purposes, dependencies, and migration targets to support the test framework restructuring.

## Test Categories

### 1. Timing Tests (Priority 1)

#### test_server_flow.py
- **Current Location**: tests/test_server_flow.py
- **Migration Target**: tests/timing/test_server_flow.py
- **Purpose**: Tests data flow from server to text processing
- **Dependencies**: 
  * src.text.TextManager
  * src.websocket.WhisperWebSocket
  * src.logging
  * config
- **Key Functions**:
  * test_server_flow(): Tests server to text processing flow
  * test_websocket_connection(): Tests WebSocket connection with server-ready-check
- **Test Coverage**:
  * Server message handling
  * WebSocket connection management
  * Text processing flow
  * Connection state verification

#### timing_tests.py
- **Current Location**: tests/timing_tests.py
- **Migration Target**: tests/timing/timing_tests.py
- **Purpose**: Systematic tests for timing system
- **Dependencies**:
  * src.websocket.WhisperWebSocket
  * src.audio.AudioManager
  * src.text.TextManager
  * config
- **Key Classes**:
  * TimingTest: Framework for timing tests with logging
- **Key Functions**:
  * test_complete_text_capture(): Tests complete text reception
  * test_quick_stop_handling(): Tests text reception with quick stop
- **Test Coverage**:
  * Audio recording timing
  * Server processing timing
  * Text output timing
  * Event logging

### 2. Integration Tests (Priority 2)

#### test_text_processing.py
- **Current Location**: tests/test_text_processing.py
- **Migration Target**: tests/integration/test_text_processing.py
- **Purpose**: Tests text processing functionality
- **Dependencies**:
  * src.text.TextManager
  * src.logging
  * config
- **Test Coverage**:
  * Text segment processing
  * Deduplication handling
  * Sentence completion
  * Punctuation handling

#### test_prompt_output.py
- **Current Location**: tests/test_prompt_output.py
- **Migration Target**: tests/integration/test_prompt_output.py
- **Purpose**: Tests text output to active windows
- **Dependencies**:
  * src.text.TextManager
  * src.logging
  * config
- **Test Coverage**:
  * Text output timing
  * Multiple sentence handling
  * Output verification
  * Timing analysis

### 3. Test Runners

#### run_tests.py
- **Current Location**: tests/run_tests.py
- **Purpose**: Main test runner
- **Dependencies**:
  * config
  * src.hotkeys.HotkeyManager
  * tests.timing_tests
  * tests.run_timing_tests
- **Features**:
  * Test suite execution
  * Hotkey management
  * Test timeout handling
  * Test abort handling

#### run_timing_tests.py
- **Current Location**: tests/run_timing_tests.py
- **Purpose**: Specialized timing test runner
- **Dependencies**:
  * tests.timing_tests
  * config
- **Features**:
  * Multiple timing configurations
  * Result logging
  * Configuration management
  * Test analysis

### 4. POC Tests (Preserved)

#### test_tumbling_window.py
- **Current Location**: tests/poc/test_tumbling_window.py
- **Status**: Ready for implementation
- **Purpose**: Audio window management POC
- **Key Features**:
  * 130ms average latency
  * Stable processing (27 windows/3.5s)
  * Overlapping windows for transitions

#### test_queue_chunks.py
- **Current Location**: tests/poc/test_queue_chunks.py
- **Status**: Conceptually validated
- **Purpose**: Queue-based chunk processing POC
- **Key Features**:
  * Thread and async implementations
  * AudioChunk data model
  * Enhanced WebSocket integration

#### test_segmentation.py
- **Current Location**: tests/poc/test_segmentation.py
- **Status**: Partially validated
- **Purpose**: Audio segmentation POC
- **Key Features**:
  * Speech segment detection
  * Energy-based classification
  * Parameter optimization

## Server Parameter Research Needs

### 1. Buffer Management
- Internal buffer size investigation needed
- Buffer optimization research required
- WhisperLive server code analysis pending

### 2. Processing Strategy
- Processing triggers documentation needed
- Batch processing strategy analysis required
- Performance impact investigation needed

### 3. Integration Points
- Server ready state detection
- Connection management patterns
- Error recovery mechanisms

## Migration Notes

### 1. Dependencies
- All tests depend on project root in sys.path
- Config module used across all tests
- Logging system integration required

### 2. Test Resources
- Audio test files needed for timing tests
- Test markers for timing validation
- Expected output data

### 3. Test Runner Consolidation
- Unified test runner needed
- Category support required
- Configuration options needed
- Proper logging integration required

## Identified Test Coverage Gaps

### 1. Audio Processing
- Missing: Comprehensive audio device testing
- Missing: Audio format conversion tests
- Missing: Audio buffer overflow tests
- Missing: Long-running recording tests
- Missing: Device switching tests

### 2. WebSocket Communication
- Missing: Connection error recovery tests
- Missing: Message format validation tests
- Missing: Large message handling tests
- Missing: Connection timeout tests
- Missing: Reconnection strategy tests

### 3. Text Processing
- Missing: Special character handling tests
- Missing: Multi-language text tests
- Missing: Text buffering tests
- Missing: Memory management tests
- Missing: Text output performance tests

### 4. Integration Testing
- Missing: End-to-end flow tests
- Missing: System stress tests
- Missing: Resource cleanup tests
- Missing: Multi-session tests
- Missing: Error cascade tests

### 5. Speech Recognition
- Missing: Noise handling tests
- Missing: Accent variation tests
- Missing: Speed variation tests
- Missing: Volume variation tests
- Missing: Background noise tests

## Next Steps

1. Move test files to new locations
2. Update import statements
3. Verify functionality
4. Create missing tests (as identified above)
5. Document server parameters through research
6. Consult WhisperLive developers if needed

Note: This inventory will be updated as the migration progresses and new information is discovered.
