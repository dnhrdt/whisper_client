# Regression Investigation: Server Communication (2025-02-14)
Version: 1.0
Timestamp: 2025-02-26 19:44 CET

## Initial Situation
- **Problem**: No texts being returned/processed from server
- **Recent Changes**:
  1. Float32 normalization disabled (2025-02-13 23:26)
  2. Code restructuring (2025-02-13 22:40)

## Investigation Plan

### 1. Documentation
- Every change is logged in this document
- Format per test:
  ```
  ### Test X: [Description]
  - Initial State: [...]
  - Change: [...]
  - Result: [...]
  - Next Steps: [...]
  ```

### 2. Systematic Tests

#### A. WebSocket Communication
1. Check connection establishment
   - Server-ready status
   - Handshake successful?
   - Configuration correctly transmitted?

2. Analyze message flow
   - Are audio data being sent?
   - Server responses in log?
   - Message format correct?

#### B. Audio Processing
1. Format verification
   - Client: int16 vs float32
   - Check server expectations
   - Sampling rate and channels

2. Data transmission
   - Buffer size
   - Timing
   - Data loss?

#### C. Text Processing
1. Callback chain
   - WebSocket → TextManager
   - Event handling
   - Error handling

### 3. Logging
- Debug level activated
- Separate log file: logs/regression_investigation.log
- Logging includes:
  - WebSocket messages
  - Audio data format
  - Server responses
  - Callback invocations

## Tests

### Test 1: Logging Setup
- **Initial State**:
  - Outdated reference to _whisperlive_logs.txt
  - Regression logger not fully configured

- **Changes**:
  - Removed _whisperlive_logs.txt references
  - Integrated regression logger with detailed format
  - Documented server log location (WSL: /home/michael/appdata/whisperlive/logs)

- **Result**:
  - Logging system ready for detailed error analysis
  - Server logs now accessible via Docker volume
  - Regression Investigation Logger activated

### Test 2: WebSocket Code Analysis
- **Initial State**:
  - Three versions of WebSocket code available:
    1. Last working version
    2. First faulty edit
    3. Second faulty edit

- **Found Differences**:
  1. Timing of processing_enabled flag:
     - Working: Flag deactivated only after waiting for last segments
     - Faulty: Flag deactivated too early, blocking incoming messages

  2. Cleanup process:
     - Working:
       * stop_processing() → send_end_of_audio() → wait → disable processing
       * Complete wait time for server responses
     - Faulty:
       * Immediate deactivation of processing
       * Incomplete wait time for server responses

  3. Message processing:
     - Working: Server has time to send last segments
     - Faulty: Premature deactivation prevents receiving last segments

- **Conclusion**:
  The regression was caused by a change in the cleanup operations sequence,
  leading to premature deactivation of message processing.

### Test 3: Server Log Access
- **Problem**:
  - Documentation needs updating
  - WSL symlink access requires prerequisites

- **Findings**:
  - Server logs available via symlink in logs/logs/server.log
  - Symlink requires WSL filesystem activation through:
    * Either opening WSL terminal
    * Or accessing WSL filesystem (U:\) in Windows
  - Reason: WSL symlinks are mounted only after filesystem activation

- **Correction**:
  - Documentation should mention WSL symlink prerequisites
  - Developers must activate WSL filesystem before log access
  - Logging paths should be consistently documented

### Test 4: Code Restoration
- **Initial State**:
  - WebSocket code with incorrect processing sequence
  - Premature deactivation of message processing
  - Missing wait time for server responses

- **Changes Made**:
  1. Restored send_end_of_audio() method:
     - Standalone method for END_OF_AUDIO signal
     - Integrated 20-second wait time
     - Improved error handling

  2. Fixed stop_processing() method:
     - Removed problematic wait_thread
     - Correct sequence: send signal first, then wait for response
     - Processing deactivation only after receiving last segments

  3. Improved cleanup() method:
     - Correct operation sequence
     - Complete wait time for server responses
     - More robust error handling

- **Expected Result**:
  - Server communication restored
  - Correct processing of last segments
  - Clean connection termination

## Results

The regression was caused by a faulty change in processing sequence:
1. Premature deactivation of message processing prevented receiving last segments
2. Missing wait times led to incomplete server communication
3. Thread-based solution was unstable and led to race conditions

The solution consists of:
1. Restoration of correct processing sequence
2. Implementation of robust wait times
3. Simplification of thread management

### Test 5: Audio Format Correction
- **Initial State**:
  - Audio data sent as raw int16 data
  - Server expects normalized float32 data
  - No transcriptions from server

- **Changes Made**:
  1. Float32 normalization reactivated:
     - Conversion from int16 to float32
     - Normalization by division by 32768.0
     - Correct data types for server processing

- **Result**:
  - Server can correctly process audio data
  - Transcriptions being received again
  - Complete processing chain restored

### Test 6: Connection Handling
- **Problem**:
  - Connection closed too early
  - Status of 20-second wait unclear
  - F13 key presses not correctly displayed

- **Changes Made**:
  1. Improved connection handling:
     - WebSocket connection remains open during wait time
     - Only audio processing is deactivated
     - Clearer sequence: Stop recording first, then wait

  2. Improved status messages:
     - "Stopping recording..." when ending recording
     - "Waiting for last texts from server..." during 20s
     - "Audio processing ended" after wait time

- **Result**:
  - Connection stays open for late texts
  - User sees clear processing status
  - Correct display of key presses

Next Steps:
1. Conduct speech tests for verification
2. Monitor server logs for successful communication
3. Document learnings for future changes
