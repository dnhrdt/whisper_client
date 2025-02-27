# WhisperLive Client Processing Analysis
Version: 1.01
Timestamp: 2025-02-27 15:17 CET

## Overview
This document analyzes the client-side text processing in WhisperLive and WhisperFusion, focusing on how the client receives and processes transcription segments from the server.

## Data Flow

1. **Server sends JSON:** 
   - The server sends a JSON object containing a list of transcription segments to the client.
   - Each segment contains timing information and transcribed text.

2. **Client receives JSON (`on_message`):**
   - The client's `on_message` function receives the JSON object.
   - Validates the client UID to ensure the message is for the correct client.
   - Checks for status messages or server commands.

3. **Segments are processed (`process_segments`):**
   - The function iterates through each segment in the received list.
   - Extracts the text from each segment.
   - Performs deduplication by checking if the current segment's text matches the last segment's text.
   - Updates the `last_segment` and `last_received_segment` variables for tracking.

4. **Transcript is updated:**
   - The `transcript` list maintains the complete history of processed segments.
   - For the faster_whisper backend:
     - Segments are only added if they are marked as completed.
     - Segments are only added if their start time is greater than or equal to the end time of the last transcript segment.

5. **Text Display/Processing:**
   - **WhisperLive:**
     - Uses `utils.clear_screen()` to clear the console.
     - Uses `utils.print_transcript()` to display the latest transcription.
     - Truncates displayed text to last 3 entries for brevity.
   - **WhisperFusion:**
     - Sends the processed text to a queue for LLM processing.
     - Handles additional LLM-related output and console display.

## Key Parameters

### Segment Data Structure
Each segment contains:
- `start`: Start time of the segment
- `end`: End time of the segment
- `text`: Transcribed text
- `completed`: Boolean flag indicating if the segment is complete (WhisperLive only)

### Deduplication Logic
- Checks if the current segment's text matches the last segment's text.
- Only appends new text if it differs from the previous segment.
- Helps prevent duplicate text in the final transcript.

### Timing Parameters
- `timestamp_offset`: Tracks the current position in the audio stream.
- Used for synchronizing transcription segments with audio playback.

### State Tracking
- `last_segment`: Stores the most recent incomplete segment.
- `last_received_segment`: Tracks the last received segment text.
- `last_response_received`: Timestamp of the last server response.

## Implementation Details

### Error Handling
- Validates client UID for each message.
- Handles server status messages (WAIT, ERROR, WARNING).
- Manages connection timeouts and disconnections.

### Output Formats
- Supports SRT file output for completed transcriptions.
- Maintains conversation history for LLM context (WhisperFusion).
- Provides real-time console output with configurable logging.

## Differences between Implementations

1. **WhisperLive (Base):**
   - Focuses on real-time transcription display.
   - Maintains simpler state management.
   - Outputs directly to console and SRT files.

2. **WhisperFusion:**
   - Adds LLM processing capabilities.
   - Maintains conversation history for context.
   - Handles additional queues for LLM input/output.
   - More complex state management for LLM integration.

3. **Chrome Extension:**
   - Implements browser-specific text processing.
   - Handles visual presentation in web pages.
   - Manages line-by-line text display.
   - Includes drag-and-drop UI functionality.

4. **Firefox Extension:**
   - Implements browser-specific text processing.
   - Handles visual presentation in web pages.
   - Manages line-by-line text display.

## Chrome Extension-Specific Processing

### Text Segment Display
- Uses a container div with multiple span elements for text display.
- Implements a line-based text segmentation system:
  - Calculates line heights dynamically.
  - Splits text into segments based on available space.
  - Maintains a rolling display of the last 3 lines.

### Visual Processing
- Handles text wrapping and line breaks.
- Removes newlines and carriage returns from text.
- Calculates proper positioning for each line of text.
- Provides draggable interface for the transcription window.

### State Management
- Maintains separate arrays for segments and text_segments.
- Processes text segments for optimal display:
  ```javascript
  text_segments = get_lines(elem, line_height);
  ```
- Updates display based on segment count:
  - For 2 or fewer segments: displays all segments.
  - For 3 or more segments: displays last 3 segments.

### Audio Processing
- Resamples audio to 16kHz before sending to server:
  ```javascript
  const audioData16kHz = resampleTo16kHZ(inputData, context.sampleRate);
  ```
- Processes audio in chunks of 4096 samples.
- Maintains an audio data cache for continuous streaming.

### Communication Flow
1. Captures tab audio using Chrome's tabCapture API.
2. Establishes WebSocket connection with server.
3. Sends initial configuration (language, task, model).
4. Streams resampled audio data continuously.
5. Receives and processes transcription segments.
6. Updates visual display in real-time.

### Error Handling
- Manages connection timeouts.
- Handles server wait states with user feedback.
- Provides visual feedback for server status.
- Implements cleanup on stream disconnection.

## Firefox Extension-Specific Processing

### Audio Processing
- Resamples audio to 16kHz before sending to server:
  ```javascript
  const audioData16kHz = resampleTo16kHZ(inputData, audioContext.sampleRate);
  ```
- Processes audio in chunks of 4096 samples.

### Communication Flow
1. Captures tab audio using Firefox's `navigator.mediaDevices.getUserMedia` API.
2. Establishes WebSocket connection with server.
3. Sends initial configuration (language, task, model).
4. Streams resampled audio data continuously.
5. Receives transcription segments.
6. Updates visual display in real-time.

### Text Segment Display
- Uses a container div with multiple span elements for text display.
- Implements a line-based text segmentation system:
  - Calculates line heights dynamically.
  - Splits text into segments based on available space.
  - Maintains a rolling display of the last 3 lines.

### Visual Processing
- Handles text wrapping and line breaks.
- Removes newlines and carriage returns from text.
- Calculates proper positioning for each line of text.

### State Management
- Maintains separate arrays for segments and text_segments.
- Processes text segments for optimal display:
  ```javascript
  text_segments = get_lines(elem, line_height);
  ```
- Updates display based on segment count:
  - For 2 or fewer segments: displays all segments.
  - For 3 or more segments: displays last 3 lines.

## Potential Improvements from Other Implementations

This section summarizes potential improvements based on analysis of other WhisperLive client implementations.

1. **Audio Resampling (jianshen02-whisperlivecppclient):** The C++ client uses `libsamplerate` for audio resampling. This library could potentially offer better performance or quality compared to our current resampling method.

2. **System Audio Capture (qasax-whisperlive-systemaudio):** The `qasax-whisperlive-systemaudio` implementation uses the `soundcard` library for cross-platform system audio capture. This library could enable our client to capture audio from various sources on different operating systems.

3. **Inter-Process Communication (qasax-whisperlive-systemaudio):** The `qasax-whisperlive-systemaudio` implementation uses a message queue for inter-process communication between the client and the UI. This pattern could be useful for decoupling the UI from the audio processing logic, making the application more modular and easier to maintain.
