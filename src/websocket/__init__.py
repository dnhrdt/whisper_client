"""
WebSocket Package for the Whisper Client
Version: 1.2
Timestamp: 2025-04-20 14:10 CET

This package provides WebSocket communication functionality for the Whisper Client.
It includes classes and functions for establishing connections, sending audio data,
receiving transcription results, and managing the connection lifecycle.

The package has been refactored into multiple modules for better maintainability:
- manager.py: Contains the main WhisperWebSocket class
- callbacks.py: Contains callback functions for WebSocket events
- connection_management.py: Functions for managing WebSocket connections
- processing.py: Functions for processing WebSocket messages and data
- state_management.py: Functions for managing WebSocket connection states
- cleanup.py: Functions for cleaning up WebSocket resources
- connection.py: Connection utilities and management
- error_handling.py: Error handling utilities
- messaging.py: Message processing and sending utilities
- state.py: Connection state definitions
"""

# Export the main class and important types
from websocket.manager import WhisperWebSocket
from websocket.state import ConnectionState
from websocket.connection import ConnectionManager

# For backward compatibility, re-export any previously public functions
from websocket.connection import (
    create_websocket_app,
    generate_client_id,
    generate_session_id,
)
from websocket.error_handling import (
    handle_connection_close,
    handle_connection_error,
    wait_with_timeout,
)
from websocket.messaging import (
    process_message,
    send_audio_data,
    send_config,
    send_end_of_audio,
)

__all__ = [
    # Main class
    'WhisperWebSocket',

    # Important types
    'ConnectionState',
    'ConnectionManager',

    # Connection utilities
    'create_websocket_app',
    'generate_client_id',
    'generate_session_id',

    # Error handling
    'handle_connection_close',
    'handle_connection_error',
    'wait_with_timeout',

    # Messaging
    'process_message',
    'send_audio_data',
    'send_config',
    'send_end_of_audio',
]
