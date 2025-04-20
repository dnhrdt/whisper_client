"""
WebSocket Callbacks Module
Version: 1.1
Timestamp: 2025-04-20 16:20 CET

This module contains callback functions for WebSocket events.
"""

from src import logger
from src.logging import log_connection, log_error

from .error_handling import handle_connection_close, handle_connection_error
from .messaging import process_message, send_config
from .state import ConnectionState


def on_open(ws_instance, ws):
    """Callback when WebSocket connection is opened"""
    ws_instance._set_state(ConnectionState.CONNECTED)
    send_config(ws, ws_instance.client_id, ws_instance.session_id)


def on_message(ws_instance, ws, message):
    """Callback for incoming server messages with enhanced error handling"""
    if not ws_instance.processing_enabled:
        return

    try:
        message_type, text = process_message(
            message, ws_instance.on_text_callback, ws_instance.processing_enabled
        )

        if message_type == "SERVER_READY":
            ws_instance.server_ready = True
            ws_instance._set_state(ConnectionState.READY)
        elif message_type == "END_OF_AUDIO_RECEIVED":
            # Server acknowledges END_OF_AUDIO signal
            ws_instance._set_state(ConnectionState.FINALIZING)
        elif message_type == "TEXT" and text:
            ws_instance.current_text = text
            ws_instance._set_state(ConnectionState.PROCESSING)
        elif message_type == "ERROR":
            ws_instance._set_state(ConnectionState.PROCESSING_ERROR)

    except Exception as e:
        log_error(logger, "Error processing message: %s", str(e))
        ws_instance._set_state(ConnectionState.PROCESSING_ERROR)


def on_error(ws_instance, ws, error):
    """Callback for WebSocket errors with enhanced logging"""
    handle_connection_error(
        error,
        ws_instance.state,
        ws_instance.client_id,
        ws_instance.session_id,
        ws_instance.server_ready,
        ws_instance.processing_enabled,
    )
    ws_instance._set_state(ConnectionState.CONNECT_ERROR)


def on_close(ws_instance, ws, close_status_code, close_msg):
    """Callback when WebSocket connection is closed"""
    handle_connection_close(close_status_code, close_msg)
    ws_instance._set_state(ConnectionState.CLOSED)
    ws_instance.server_ready = False
