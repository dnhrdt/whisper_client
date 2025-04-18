"""
WebSocket Communication Module for the Whisper Client (Simplified Version)
Version: 1.8
Timestamp: 2025-04-18 12:09 CET

This module handles WebSocket communication with the WhisperLive server.
It provides functionality for establishing connections, sending audio data,
receiving transcription results, and managing the connection lifecycle.

REFACTORING NOTICE: Diese Datei wird in mehrere Module aufgeteilt.
Die aktuelle Version dient als Referenz für die neue Modulstruktur.
Siehe docs/refactoring.md für den vollständigen Plan.

Neue Struktur:
- websocket/state.py: ConnectionState Enum und Zustandsverwaltung
- websocket/connection.py: Verbindungsfunktionalität und Instance-Tracking
- websocket/messaging.py: Nachrichtenverarbeitung und Datenübertragung
- websocket/error_handling.py: Fehlerbehandlung und Recovery
- websocket/__init__.py: API und Hauptklasse
"""

import enum
import json
import threading
import time
import uuid
from typing import Dict  # Import Dict

import win32clipboard

import config
import websocket
from src import logger
from src.logging import log_audio, log_connection, log_error, log_text  # Remove log_warning import


# MOVED TO: websocket/state.py
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


# MOVED TO: websocket/__init__.py
class WhisperWebSocket:
    # Class-level variable to track active instances
    _active_instances: Dict[str, "WhisperWebSocket"] = {}
    _instances_lock = threading.Lock()

    def __init__(self):
        # Generate a persistent client ID that remains the same across reconnections
        self.client_id = str(uuid.uuid4())
        # Session ID changes with each new connection attempt
        self.session_id = str(uuid.uuid4())
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
        self.state_log_interval = 5.0  # Log state every 5 seconds during long operations

        # Register this instance
        with WhisperWebSocket._instances_lock:
            WhisperWebSocket._active_instances[self.client_id] = self

        log_connection(logger, "Created WebSocket client with ID: %s" % self.client_id)

    def _set_state(self, new_state):
        """Sets the connection state and logs the transition"""
        with self.connection_lock:
            old_state = self.state
            self.state = new_state
            log_connection(logger, "State changed: %s -> %s" % (old_state.name, new_state.name))

    def _log_state_periodically(self, operation_name):
        """Log state periodically during long-running operations"""
        current_time = time.time()
        if current_time - self.last_state_log_time >= self.state_log_interval:
            self.last_state_log_time = current_time
            log_connection(
                logger,
                "[%s] Current state: %s, Active instances: %d" % (
                    operation_name,
                    self.state.name,
                    self.get_instance_count(),
                )
            )

    @classmethod
    def get_instance_count(cls):
        """Returns the number of active WebSocket instances"""
        with cls._instances_lock:
            return len(cls._active_instances)

    @classmethod
    def cleanup_all_instances(cls):
        """Cleanup all active WebSocket instances with proper timeout handling"""
        cleanup_start = time.time()
        log_connection(
            logger,
            "Starting cleanup of all WebSocket instances (%d active)..." % cls.get_instance_count(),
        )

        with cls._instances_lock:
            instances = list(cls._active_instances.values())

        success_count = 0
        error_count = 0

        for instance in instances:
            try:
                instance.cleanup()
                success_count += 1
            except Exception as e:
                error_count += 1
                log_error(logger, "Error cleaning up instance %s: %s" % (instance.client_id, str(e)))

        # Check if cleanup took too long
        cleanup_duration = time.time() - cleanup_start
        if cleanup_duration > config.WS_CLEANUP_TIMEOUT:
            log_error(
                logger,
                "Cleanup of all instances took longer than expected: %.2fs" % cleanup_duration,
            )

        # Final cleanup status
        log_connection(
            logger,
            "Cleanup completed: %d successful, %d failed, duration: %.2fs" % (
                success_count,
                error_count,
                cleanup_duration,
            )
        )

        # Check if any instances remain
        remaining = cls.get_instance_count()
        if remaining > 0:
            log_error(
                logger, "Warning: %d WebSocket instances still active after cleanup" % remaining
            )

    def __del__(self):
        """Remove this instance when garbage collected"""
        try:
            with WhisperWebSocket._instances_lock:
                if self.client_id in WhisperWebSocket._active_instances:
                    del WhisperWebSocket._active_instances[self.client_id]
        except Exception as e:
            # Ignore errors during shutdown, but log them in debug mode
            try:
                logger.debug("Error during instance cleanup in __del__: %s" % e)
            except Exception:
                pass  # Suppress any errors in logging during shutdown

    def _cleanup_previous_connection(self):
        """Cleans up the previous WebSocket connection if it exists."""
        if self.ws:
            try:
                log_connection(logger, "Cleaning up previous connection before reconnect...")
                self.cleanup()  # Use the existing cleanup method
            except Exception as e:
                log_error(logger, "Error during cleanup before reconnection: %s" % str(e))
            finally:
                self.ws = None
                self.ws_thread = None

    def _initialize_and_start_websocket(self):
        """Initializes and starts the WebSocketApp and its thread."""
        log_connection(
            logger,
            "Connecting to server: %s (Client: %s, Session: %s)" % (
                config.WS_URL,
                self.client_id,
                self.session_id,
            )
        )
        self.ws = websocket.WebSocketApp(
            config.WS_URL,
            on_open=self._on_open,
            on_message=self._on_message,
            on_error=self._on_error,
            on_close=self._on_close,
        )
        self.ws_thread = threading.Thread(target=self.ws.run_forever)
        self.ws_thread.daemon = True
        self.ws_thread.start()

    def _wait_for_socket_connection(self):
        """Waits for the WebSocket socket to connect with timeout."""
        start_time = time.time()
        while not self.ws or not self.ws.sock or not self.ws.sock.connected:
            if time.time() - start_time > config.WS_CONNECT_TIMEOUT:
                self._set_state(ConnectionState.TIMEOUT_ERROR)
                raise TimeoutError("Connection timeout after %ds" % config.WS_CONNECT_TIMEOUT)
            self._log_state_periodically("connect_wait")
            time.sleep(config.WS_POLL_INTERVAL)
        self._set_state(ConnectionState.CONNECTED)

    def _wait_for_server_ready(self):
        """Waits for the server to send the READY signal with timeout."""
        log_connection(
            logger,
            "Waiting for server ready signal (timeout: %ds)..." % config.WS_READY_TIMEOUT,
        )
        start_time = time.time()
        while not self.server_ready:
            if time.time() - start_time > config.WS_READY_TIMEOUT:
                self._set_state(ConnectionState.TIMEOUT_ERROR)
                raise TimeoutError("Server ready timeout after %ds" % config.WS_READY_TIMEOUT)
            self._log_state_periodically("ready_wait")
            time.sleep(config.WS_POLL_INTERVAL)

    def connect(self, max_retries=3):
        """Establish WebSocket connection with enhanced timeout handling"""
        # Check if already connected
        if (
            self.state
            in [ConnectionState.CONNECTED, ConnectionState.READY, ConnectionState.PROCESSING]
            and self.ws
            and self.ws.sock
            and self.ws.sock.connected
        ):
            log_connection(logger, "Already connected")
            return True

        # Check for connection throttling
        current_time = time.time()
        if current_time - self.last_connection_attempt < config.WS_RECONNECT_DELAY:
            wait_time = config.WS_RECONNECT_DELAY - (current_time - self.last_connection_attempt)
            log_connection(logger, "Connection attempt throttled, waiting %.2fs" % wait_time)
            time.sleep(wait_time)

        # Update connection attempt timestamp
        self.last_connection_attempt = time.time()
        connect_start_time: float = self.last_connection_attempt

        # Generate new session ID for this connection attempt
        self.session_id = str(uuid.uuid4())
        log_connection(logger, "Starting connection attempt with session ID: %s" % self.session_id)

        retry_count = 0
        retry_delay = config.WS_RETRY_DELAY

        while retry_count < max_retries:
            try:
                # 1. Cleanup previous connection
                self._cleanup_previous_connection()

                # 2. Set state and initialize WebSocket
                self._set_state(ConnectionState.CONNECTING)
                self._initialize_and_start_websocket()

                # 3. Wait for socket connection
                self._wait_for_socket_connection()
                self.processing_enabled = True  # Enable processing after successful connection

                # 4. Wait for server ready signal
                self._wait_for_server_ready()

                # Connection successful
                total_connect_time = time.time() - connect_start_time
                log_connection(
                    logger, "Connection established successfully in %.2fs" % total_connect_time
                )
                return True

            except Exception as e:
                retry_count += 1
                if self.state != ConnectionState.TIMEOUT_ERROR:
                    self._set_state(ConnectionState.CONNECT_ERROR)
                self.server_ready = False

                if retry_count < max_retries:
                    log_error(
                        logger,
                        "Connection error (attempt %d/%d): %s" % (
                            retry_count,
                            max_retries,
                            str(e),
                        )
                    )
                    log_connection(logger, "Retrying in %.1fs..." % retry_delay)
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, config.WS_MAX_RETRY_DELAY)
                else:
                    log_error(
                        logger,
                        "Maximum retry attempts reached (%d). Last error: %s" % (
                            max_retries,
                            str(e),
                        )
                    )
                    raise

        return False

    def _on_open(self, ws):
        """Callback when WebSocket connection is opened"""
        self._set_state(ConnectionState.CONNECTED)
        try:
            ws_config = {
                "uid": self.client_id,
                "session_id": self.session_id,
                "language": config.WHISPER_LANGUAGE,
                "task": config.WHISPER_TASK,
                "use_vad": config.WHISPER_USE_VAD,
                "backend": config.WHISPER_BACKEND,
            }
            json_str = json.dumps(ws_config).encode("utf-8")
            log_connection(logger, "Sending config: %s" % json.dumps(ws_config, indent=2))
            if self.ws:  # Check if ws is not None
                ws.send(json_str, websocket.ABNF.OPCODE_TEXT)
        except Exception as e:
            log_error(logger, "Error sending config: %s" % str(e))
            self._set_state(ConnectionState.CONNECT_ERROR)

    def _on_message(self, ws, message):
        """Callback for incoming server messages with enhanced error handling"""
        if not self.processing_enabled:
            return

        try:
            message_start = time.time()

            if isinstance(message, bytes):
                message = message.decode("utf-8")

            log_connection(logger, "Raw server message: %s" % message)
            data = json.loads(message)

            if "message" in data:
                if data["message"] == "SERVER_READY":
                    self.server_ready = True
                    self._set_state(ConnectionState.READY)
                    return
                elif data["message"] == "END_OF_AUDIO_RECEIVED":
                    # Server acknowledges END_OF_AUDIO signal
                    self._set_state(ConnectionState.FINALIZING)
                    return

            if "segments" in data:
                segments = data["segments"]
                if segments:
                    # Take only the last complete text
                    text = segments[-1].get("text", "").strip()
                    if text != self.current_text:
                        self.current_text = text
                        log_text(logger, text)
                        if self.on_text_callback:
                            callback_start = time.time()
                            self.on_text_callback([segments[-1]])
                            callback_duration = time.time() - callback_start
                            if callback_duration > config.WS_MESSAGE_WAIT:
                                log_connection(
                                    logger, "Text callback took too long: %.2fs" % callback_duration
                                )

            # Check if message processing took too long
            message_duration = time.time() - message_start
            if message_duration > config.WS_MESSAGE_WAIT:
                log_connection(
                    logger, "Message processing took longer than expected: %.2fs" % message_duration
                )

        except Exception as e:
            log_error(logger, "Error processing message: %s" % str(e))
            self._set_state(ConnectionState.PROCESSING_ERROR)

    def _on_error(self, ws, error):
        """Callback for WebSocket errors with enhanced logging"""
        log_error(logger, "WebSocket error: %s" % str(error))
        self._set_state(ConnectionState.CONNECT_ERROR)

        # Log additional context for the error
        try:
            error_context = (
                "Error context - State: %s, Client ID: %s, Session ID: %s, Server ready: %s, Processing enabled: %s"
                % (
                    self.state.name,
                    self.client_id,
                    self.session_id,
                    self.server_ready,
                    self.processing_enabled,
                )
            )
            log_error(logger, error_context)
        except Exception as e:
            # Ignore errors in error logging, but try to log a basic message
            try:
                logger.debug("Error while logging error context: %s" % e)
            except Exception:
                pass  # Suppress any errors in logging during error handling

    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when WebSocket connection is closed"""
        log_msg = "Connection closed"
        if close_status_code:
            log_msg += " (Status: %s)" % close_status_code
        if close_msg:
            log_msg += " (Message: %s)" % close_msg
        log_connection(logger, log_msg)
        self._set_state(ConnectionState.CLOSED)
        self.server_ready = False

    def is_ready(self):
        """Checks if the server is ready"""
        return self.state == ConnectionState.READY

    def send_audio(self, audio_data):
        """Sends audio data to the server with enhanced error handling"""
        if not self.processing_enabled or not self.is_ready():
            return False

        try:
            send_start = time.time()
            if self.ws:  # Check if ws is not None
                self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            else:
                log_error(logger, "Attempted to send audio while WebSocket is None")
                return False
            send_duration = time.time() - send_start

            # Log audio send with timing information
            log_audio(logger, "Sent %d bytes in %.3fs" % (len(audio_data), send_duration))

            # Check if send took too long
            if send_duration > config.WS_MESSAGE_WAIT:
                log_connection(logger, "Audio send took longer than expected: %.2fs" % send_duration)

            return True
        except Exception as e:
            log_error(logger, "Error sending audio: %s" % str(e))
            self._set_state(ConnectionState.CONNECT_ERROR)
            return False

    def set_text_callback(self, callback):
        """Sets the callback for received text segments"""
        self.on_text_callback = callback

    def send_end_of_audio(self):
        """Sends END_OF_AUDIO signal to the server with enhanced timeout handling"""
        if not self.is_ready() and self.state != ConnectionState.PROCESSING:
            return False

        try:
            self._set_state(ConnectionState.FINALIZING)
            send_start = time.time()
            if self.ws:  # Check if ws is not None
                self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
            else:
                log_error(logger, "Attempted to send END_OF_AUDIO while WebSocket is None")
                return False
            send_duration = time.time() - send_start

            log_audio(logger, "Sent END_OF_AUDIO signal in %.3fs" % send_duration)
            log_connection(
                logger, "Waiting for final segments (timeout: %ds)..." % config.WS_FINAL_WAIT
            )

            # Wait for server to acknowledge END_OF_AUDIO with timeout
            wait_start = time.time()
            while self.state == ConnectionState.FINALIZING:
                if time.time() - wait_start > config.WS_FINAL_WAIT:
                    log_connection(
                        logger, "Final wait timeout reached after %ds" % config.WS_FINAL_WAIT
                    )
                    break

                # Periodically log state during finalization
                self._log_state_periodically("finalization_wait")
                time.sleep(config.WS_POLL_INTERVAL)

            wait_duration = time.time() - wait_start
            log_connection(logger, "Finalization completed in %.2fs" % wait_duration)
            return True
        except Exception as e:
            log_error(logger, "Error sending END_OF_AUDIO: %s" % str(e))
            return False

    def stop_processing(self):
        """Stops processing server messages with enhanced timeout handling"""
        if self.processing_enabled:
            stop_start = time.time()
            log_connection(logger, "Stopping message processing...")

            try:
                if self.is_ready() or self.state == ConnectionState.PROCESSING:
                    # Send END_OF_AUDIO and wait for processing
                    self._set_state(ConnectionState.FINALIZING)
                    if self.ws:  # Check if ws is not None
                        self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
                        log_audio(logger, "Sent END_OF_AUDIO signal")
                    else:
                        log_error(
                            logger,
                            "Attempted to send END_OF_AUDIO during stop_processing while WebSocket is None",
                        )

                    # Wait for final segments with timeout monitoring
                    wait_start = time.time()
                    last_message_time = wait_start

                    while True:
                        # Check timeout
                        current_time = time.time()
                        if current_time - wait_start > config.WS_FINAL_WAIT:
                            log_connection(
                                logger, "Final wait timeout reached after %ds" % config.WS_FINAL_WAIT
                            )
                            break

                        # Check inactivity
                        if current_time - last_message_time > config.WS_MESSAGE_WAIT:
                            log_connection(
                                logger, "No new messages for %ds, stopping" % config.WS_MESSAGE_WAIT
                            )
                            break

                        # Periodically log state during stop processing
                        self._log_state_periodically("stop_processing_wait")

                        # Short pause
                        time.sleep(config.WS_POLL_INTERVAL)

                    # Disable processing
                    self.processing_enabled = False
                    self.current_text = ""

                    # Close connection cleanly
                    self._set_state(ConnectionState.CLOSING)
                    log_connection(logger, "Closing connection...")
                    close_start = time.time()
                    if self.ws:  # Check if ws is not None
                        self.ws.close()
                    else:
                        # Use log_error instead of log_warning and reformat
                        log_error(
                            logger,
                            "Attempted to close WebSocket during stop_processing "  # Break line again
                            "while it was None",
                        )
                    close_duration = time.time() - close_start
                    log_connection(logger, "Connection close() completed in %.2fs" % close_duration)

                    # Wait for thread to end with timeout
                    if self.ws_thread and self.ws_thread.is_alive():
                        join_start = time.time()
                        thread_wait_msg = (
                            "Waiting for WebSocket thread to terminate (timeout: %ds)..."
                            % config.WS_THREAD_TIMEOUT
                        )
                        log_connection(logger, thread_wait_msg)
                        self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)

                        # Check if thread is still alive after join timeout
                        if self.ws_thread.is_alive():
                            thread_timeout_msg = (
                                "WebSocket thread did not terminate within timeout (%ds)"
                                % config.WS_THREAD_TIMEOUT
                            )
                            log_error(logger, thread_timeout_msg)
                            log_connection(
                                logger, "Proceeding with cleanup despite thread still running"
                            )
                        else:
                            join_duration = time.time() - join_start
                            log_connection(
                                logger, "WebSocket thread terminated in %.2fs" % join_duration
                            )

            except Exception as e:
                log_error(logger, "Error stopping processing: %s" % str(e))
            finally:
                self.processing_enabled = False
                self._set_state(ConnectionState.CLOSED)
                self.server_ready = False
                stop_duration = time.time() - stop_start
                log_connection(logger, "Processing stopped in %.2fs" % stop_duration)

    def start_processing(self):
        """Starts processing server messages with enhanced error handling"""
        if not self.is_ready():
            not_ready_msg = "Server not ready for processing (current state: %s)" % self.state.name
            log_error(logger, not_ready_msg)
            return False

        start_time = time.time()
        log_connection(logger, "Starting message processing...")

        self.processing_enabled = True
        self.current_text = ""

        try:
            # Clear clipboard
            clipboard_start = time.time()
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                clipboard_duration = time.time() - clipboard_start
                log_connection(logger, "Clipboard cleared in %.3fs" % clipboard_duration)
            except Exception as e:
                log_error(logger, "Could not clear clipboard: %s" % str(e))

            self._set_state(ConnectionState.PROCESSING)
            total_duration = time.time() - start_time
            log_connection(logger, "Server message processing enabled in %.2fs" % total_duration)
            return True

        except Exception as e:
            log_error(logger, "Error starting processing: %s" % str(e))
            self.processing_enabled = False
            return False

    def cleanup(self):
        """Release resources with enhanced timeout handling and logging"""
        if not self.ws:
            return

        cleanup_start = time.time()
        log_connection(logger, "Starting cleanup for session %s..." % self.session_id)

        try:
            # Set a timeout for the entire cleanup operation
            cleanup_timeout = config.WS_CLEANUP_TIMEOUT

            # Disable processing
            self.processing_enabled = False

            # Close WebSocket connection
            if self.ws and self.ws.sock:
                self._set_state(ConnectionState.CLOSING)
                close_start = time.time()
                log_connection(logger, "Closing WebSocket connection...")
                if self.ws:  # Check if ws is not None
                    self.ws.close()
                else:
                    # Use log_error instead of log_warning
                    log_error(  # Break line for flake8 E501
                        logger,
                        "Attempted to close WebSocket during cleanup while it was None",
                    )
                close_duration = time.time() - close_start
                log_connection(logger, "WebSocket close() completed in %.2fs" % close_duration)

            # Wait for thread to terminate
            if self.ws_thread and self.ws_thread.is_alive():
                join_start = time.time()
                thread_wait_msg = (
                    "Waiting for WebSocket thread to terminate (timeout: %ds)..."
                    % config.WS_THREAD_TIMEOUT
                )
                log_connection(logger, thread_wait_msg)
                self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)

                # Check if thread is still alive after join timeout
                if self.ws_thread.is_alive():
                    thread_timeout_msg = (
                        "WebSocket thread did not terminate within %ds timeout"
                        % config.WS_THREAD_TIMEOUT
                    )
                    log_error(logger, thread_timeout_msg)
                    log_connection(logger, "Proceeding with cleanup despite thread still running")
                else:
                    join_duration = time.time() - join_start
                    log_connection(logger, "WebSocket thread terminated in %.2fs" % join_duration)

            # Check overall cleanup timeout
            if time.time() - cleanup_start > cleanup_timeout:
                timeout_msg = (
                    "Cleanup operation taking longer than expected (%ds)" % cleanup_timeout
                )
                log_error(logger, timeout_msg)

        except Exception as e:
            log_error(logger, "Error during cleanup: %s" % str(e))
        finally:
            self.ws = None
            self._set_state(ConnectionState.DISCONNECTED)
            self.server_ready = False
            cleanup_duration = time.time() - cleanup_start
            cleanup_msg = "Cleanup completed for session %s in %.2fs" % (
                self.session_id,
                cleanup_duration,
            )
            log_connection(logger, cleanup_msg)
