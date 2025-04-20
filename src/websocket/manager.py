"""
WebSocket Manager Module
Version: 1.0
Timestamp: 2025-04-20 14:05 CET

This module contains the main WhisperWebSocket class that manages the WebSocket
connection to the WhisperLive server.
"""

import threading
import time

import win32clipboard

import config
from src import logger
from src.logging import log_audio, log_connection, log_error
from websocket.state import ConnectionState
from websocket.callbacks import (
    on_open,
    on_message,
    on_error,
    on_close,
)
from websocket.connection_management import (
    cleanup_previous_connection,
    initialize_and_start_websocket,
    wait_for_socket_connection,
    wait_for_server_ready,
    connect_to_server,
)
from websocket.processing import (
    send_audio_data,
    send_end_of_audio_signal,
    start_message_processing,
    stop_message_processing,
)
from websocket.state_management import (
    set_connection_state,
    log_state_periodically,
)
from websocket.cleanup import (
    perform_cleanup,
    handle_instance_deletion,
)
from websocket.connection import (
    ConnectionManager,
    generate_client_id,
    generate_session_id,
)


class WhisperWebSocket:
    """WebSocket client for communication with the WhisperLive server"""

    def __init__(self):
        # Generate a persistent client ID that remains the same across reconnections
        self.client_id = generate_client_id()
        # Session ID changes with each new connection attempt
        self.session_id = generate_session_id()
        self.ws = None
        self.ws_thread = None
        self.state = ConnectionState.DISCONNECTED
        self.server_ready = False
        self.on_text_callback = None
        self.processing_enabled = True
        self.current_text = ""  # Stores the current text
        self.connection_lock = threading.Lock()  # Lock for thread-safe state changes
        self.last_connection_attempt: float = 0.0  # Timestamp of last connection attempt
        self.last_state_log_time: float = 0.0  # Timestamp of last state logging
        self.state_log_interval = config.WS_STATE_LOG_INTERVAL  # Log state every 5 seconds during long operations

        # Register this instance
        ConnectionManager.register_instance(self)
        log_connection(logger, "Created WebSocket client with ID: %s" % self.client_id)

    def __del__(self):
        """Remove this instance when garbage collected"""
        handle_instance_deletion(self.client_id)

    def _set_state(self, new_state):
        """Sets the connection state and logs the transition"""
        set_connection_state(self, new_state)

    def _log_state_periodically(self, operation_name):
        """Log state periodically during long-running operations"""
        log_state_periodically(self, operation_name)

    def _cleanup_previous_connection(self):
        """Cleans up the previous WebSocket connection if it exists."""
        cleanup_previous_connection(self)

    def _initialize_and_start_websocket(self):
        """Initializes and starts the WebSocketApp and its thread."""
        initialize_and_start_websocket(self)

    def _wait_for_socket_connection(self):
        """Waits for the WebSocket socket to connect with timeout."""
        wait_for_socket_connection(self)

    def _wait_for_server_ready(self):
        """Waits for the server to send the READY signal with timeout."""
        wait_for_server_ready(self)

    def connect(self, max_retries=3):
        """Establish WebSocket connection with enhanced timeout handling"""
        return connect_to_server(self, max_retries)

    def _on_open(self, ws):
        """Callback when WebSocket connection is opened"""
        on_open(self, ws)

    def _on_message(self, ws, message):
        """Callback for incoming server messages with enhanced error handling"""
        on_message(self, ws, message)

    def _on_error(self, ws, error):
        """Callback for WebSocket errors with enhanced logging"""
        on_error(self, ws, error)

    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when WebSocket connection is closed"""
        on_close(self, ws, close_status_code, close_msg)

    def is_ready(self):
        """Checks if the server is ready"""
        return self.state == ConnectionState.READY

    def send_audio(self, audio_data):
        """Sends audio data to the server with enhanced error handling"""
        return send_audio_data(self, audio_data)

    def set_text_callback(self, callback):
        """Sets the callback for received text segments"""
        self.on_text_callback = callback

    def send_end_of_audio(self):
        """Sends END_OF_AUDIO signal to the server with enhanced timeout handling"""
        return send_end_of_audio_signal(self)

    def stop_processing(self):
        """Stops processing server messages with enhanced timeout handling"""
        stop_message_processing(self)

    def start_processing(self):
        """Starts processing server messages with enhanced error handling"""
        return start_message_processing(self)

    def cleanup(self):
        """Release resources with enhanced timeout handling and logging"""
        perform_cleanup(self)
