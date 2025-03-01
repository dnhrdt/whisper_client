# WebSocket Protocol for WhisperLive Server
Version: 1.0
Timestamp: 2025-03-01 19:50 CET

## Overview
This document describes the WebSocket protocol used for communication between the WhisperClient and the WhisperLive server. It includes details about connection states, message formats, and the overall communication flow.

## Connection States

The client implements a state machine to track the connection status:

```
DISCONNECTED → CONNECTING → CONNECTED → READY → PROCESSING → FINALIZING → CLOSING → CLOSED
```

### State Descriptions

1. **DISCONNECTED**: Initial state, no active connection
2. **CONNECTING**: Attempting to establish a WebSocket connection
3. **CONNECTED**: WebSocket connection established, waiting for server ready signal
4. **READY**: Server is ready to receive audio data
5. **PROCESSING**: Actively processing audio data
6. **FINALIZING**: END_OF_AUDIO sent, waiting for final transcriptions
7. **CLOSING**: Closing the connection
8. **CLOSED**: Connection closed

### Error States

9. **CONNECT_ERROR**: Error during connection establishment
10. **PROCESSING_ERROR**: Error during audio processing
11. **TIMEOUT_ERROR**: Timeout waiting for server response

## Connection Flow

1. Client initiates connection to `ws://localhost:9090`
2. Upon successful connection, client sends configuration
3. Server responds with `SERVER_READY` message
4. Client transitions to READY state
5. Client can start sending audio data (PROCESSING state)
6. When finished, client sends `END_OF_AUDIO` signal
7. Client transitions to FINALIZING state
8. Client waits for final transcriptions
9. Client closes connection

## Message Formats

### Client to Server

#### Configuration Message
Sent immediately after connection is established:

```json
{
  "uid": "unique-client-id",
  "language": "de",
  "task": "transcribe",
  "use_vad": true,
  "backend": "faster_whisper"
}
```

#### Audio Data
Audio data is sent as binary WebSocket messages (OPCODE_BINARY).
- Format: Raw audio bytes (16-bit PCM, 16kHz, mono)
- Chunk size: Variable, typically 4096 samples

#### End of Audio Signal
Sent to indicate the end of the audio stream:
```
END_OF_AUDIO
```

### Server to Client

#### Server Ready Message
Sent when the server is ready to receive audio:

```json
{
  "message": "SERVER_READY"
}
```

#### Transcription Message
Sent when new transcription segments are available:

```json
{
  "type": "transcription",
  "segments": [
    {
      "start": 0.0,
      "end": 1.5,
      "text": "Example transcription"
    }
  ]
}
```

## Connection Handling

### Reconnection Strategy
- Unlimited reconnection attempts
- Exponential backoff: Starting at 3s, doubling each attempt, up to 30s
- 5s connection timeout

### Error Handling
- Connection errors: Transition to CONNECT_ERROR state, attempt reconnection
- Processing errors: Transition to PROCESSING_ERROR state, log error details
- Timeout errors: Transition to TIMEOUT_ERROR state, attempt recovery

## END_OF_AUDIO Handling

When the client sends the END_OF_AUDIO signal:

1. Client transitions to FINALIZING state
2. Client waits for up to 30 seconds for final transcriptions
3. If no new messages are received for 1 second, client assumes processing is complete
4. Client closes the connection

## Thread Safety

The connection state is protected by a mutex lock to ensure thread-safe state transitions, especially important when:
- Transitioning between states
- Handling reconnection attempts
- Processing incoming messages
- Sending audio data

## Known Issues

1. **Multiple Parallel Connections**
   - Server logs show multiple client connections in short time periods
   - Possible cause: Reconnection attempts without proper cleanup

2. **Connection Closures During Processing**
   - Connections are closed with status 1000 after END_OF_AUDIO but before processing completes
   - Possible cause: Server timeout or resource management issue

3. **Server Continues Processing After END_OF_AUDIO**
   - Server continues processing despite the completed=true flag
   - Possible cause: Server buffer management issue

## Next Steps for Protocol Improvement

1. Implement server acknowledgment for END_OF_AUDIO
2. Add connection ID tracking to prevent multiple parallel connections
3. Improve cleanup and resource management
4. Document server buffer handling and processing triggers
