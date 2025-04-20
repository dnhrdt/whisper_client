"""
WebSocket State Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 13:01 CET

This module defines the connection states and state management
functionality for the WebSocket client.
"""

import enum


class ConnectionState(enum.Enum):
    """Enum for WebSocket connection states"""

    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    READY = 3
    PROCESSING = 4
    FINALIZING = 5
    CLOSING = 6
    CLOSED = 7
    CONNECT_ERROR = 8
    PROCESSING_ERROR = 9
    TIMEOUT_ERROR = 10
