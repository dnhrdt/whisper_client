"""
WebSocket Connection Management Module
Version: 1.0
Timestamp: 2025-04-20 14:07 CET

This module contains functions for managing WebSocket connections.
"""

import time
import threading

import config
from src import logger
from src.logging import log_connection, log_error
from websocket.state import ConnectionState
from websocket.connection import create_websocket_app, generate_session_id


def cleanup_previous_connection(ws_instance):
    """Cleans up the previous WebSocket connection if it exists."""
    if ws_instance.ws:
        try:
            log_connection(logger, "Cleaning up previous connection before reconnect...")
            ws_instance.cleanup()  # Use the existing cleanup method
        except Exception as e:
            log_error(logger, "Error during cleanup before reconnection: %s" % str(e))
        finally:
            ws_instance.ws = None
            ws_instance.ws_thread = None


def initialize_and_start_websocket(ws_instance):
    """Initializes and starts the WebSocketApp and its thread."""
    log_connection(
        logger,
        "Connecting to server: %s (Client: %s, Session: %s)" % (
            config.WS_URL,
            ws_instance.client_id,
            ws_instance.session_id,
        )
    )
    ws_instance.ws = create_websocket_app(
        config.WS_URL,
        on_open=ws_instance._on_open,
        on_message=ws_instance._on_message,
        on_error=ws_instance._on_error,
        on_close=ws_instance._on_close,
    )
    ws_instance.ws_thread = threading.Thread(target=ws_instance.ws.run_forever)
    ws_instance.ws_thread.daemon = True
    ws_instance.ws_thread.start()


def wait_for_socket_connection(ws_instance):
    """Waits for the WebSocket socket to connect with timeout."""
    start_time = time.time()
    while not ws_instance.ws or not ws_instance.ws.sock or not ws_instance.ws.sock.connected:
        if time.time() - start_time > config.WS_CONNECT_TIMEOUT:
            ws_instance._set_state(ConnectionState.TIMEOUT_ERROR)
            raise TimeoutError("Connection timeout after %ds" % config.WS_CONNECT_TIMEOUT)
        ws_instance._log_state_periodically("connect_wait")
        time.sleep(config.WS_POLL_INTERVAL)
    ws_instance._set_state(ConnectionState.CONNECTED)


def wait_for_server_ready(ws_instance):
    """Waits for the server to send the READY signal with timeout."""
    log_connection(
        logger,
        "Waiting for server ready signal (timeout: %ds)..." % config.WS_READY_TIMEOUT,
    )
    start_time = time.time()
    while not ws_instance.server_ready:
        if time.time() - start_time > config.WS_READY_TIMEOUT:
            ws_instance._set_state(ConnectionState.TIMEOUT_ERROR)
            raise TimeoutError("Server ready timeout after %ds" % config.WS_READY_TIMEOUT)
        ws_instance._log_state_periodically("ready_wait")
        time.sleep(config.WS_POLL_INTERVAL)


def connect_to_server(ws_instance, max_retries=3):
    """Establish WebSocket connection with enhanced timeout handling"""
    # Check if already connected
    if (
        ws_instance.state
        in [ConnectionState.CONNECTED, ConnectionState.READY, ConnectionState.PROCESSING]
        and ws_instance.ws
        and ws_instance.ws.sock
        and ws_instance.ws.sock.connected
    ):
        log_connection(logger, "Already connected")
        return True

    # Check for connection throttling
    current_time = time.time()
    if current_time - ws_instance.last_connection_attempt < config.WS_RECONNECT_DELAY:
        wait_time = config.WS_RECONNECT_DELAY - (current_time - ws_instance.last_connection_attempt)
        log_connection(logger, "Connection attempt throttled, waiting %.2fs" % wait_time)
        time.sleep(wait_time)

    # Update connection attempt timestamp
    ws_instance.last_connection_attempt = time.time()
    connect_start_time: float = ws_instance.last_connection_attempt

    # Generate new session ID for this connection attempt
    ws_instance.session_id = generate_session_id()
    log_connection(logger, "Starting connection attempt with session ID: %s" % ws_instance.session_id)

    retry_count = 0
    retry_delay = config.WS_RETRY_DELAY

    while retry_count < max_retries:
        try:
            # 1. Cleanup previous connection
            cleanup_previous_connection(ws_instance)

            # 2. Set state and initialize WebSocket
            ws_instance._set_state(ConnectionState.CONNECTING)
            initialize_and_start_websocket(ws_instance)

            # 3. Wait for socket connection
            wait_for_socket_connection(ws_instance)
            ws_instance.processing_enabled = True  # Enable processing after successful connection

            # 4. Wait for server ready signal
            wait_for_server_ready(ws_instance)

            # Connection successful
            total_connect_time = time.time() - connect_start_time
            log_connection(
                logger, "Connection established successfully in %.2fs" % total_connect_time
            )
            return True

        except Exception as e:
            retry_count += 1
            if ws_instance.state != ConnectionState.TIMEOUT_ERROR:
                ws_instance._set_state(ConnectionState.CONNECT_ERROR)
            ws_instance.server_ready = False

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
