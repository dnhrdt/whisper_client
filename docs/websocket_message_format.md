# WebSocket Message Format
Version: 1.0
Timestamp: 2025-02-27 16:00 CET

## Overview
This document describes the format of messages exchanged between the WhisperLive client and server via WebSocket.

## Message Types

### Client to Server
```json
{
  "type": "audio_data",
  "audio": "base64 encoded audio data"
}
```

### Server to Client
```json
{
  "type": "transcription",
  "segments": [
    {
      "start": 0.0,
      "end": 0.0,
      "text": "example transcription"
    }
  ]
}
```

## Data Structures

### audio_data (Client to Server)
This message is sent from the client to the server to transmit audio data.

```json
{
  "type": "audio_data",
  "audio": "base64 encoded audio data"
}
```

*   `type`: (string, required) The message type, which is always "audio_data".
*   `audio`: (string, required) The base64 encoded audio data.

### transcription (Server to Client)
This message is sent from the server to the client to transmit transcription results.

```json
{
  "type": "transcription",
  "segments": [
    {
      "start": 0.0,
      "end": 0.0,
      "text": "example transcription"
    }
  ]
}
```

*   `type`: (string, required) The message type, which is always "transcription".
*   `segments`: (array, required) An array of transcription segments.

### segment (Server to Client)
This data structure represents a single transcription segment.

```json
{
  "start": 0.0,
  "end": 0.0,
  "text": "example transcription"
}
```

*   `start`: (number, required) The start time of the segment in seconds.
*   `end`: (number, required) The end time of the segment in seconds.
*   `text`: (string, required) The transcribed text of the segment.
