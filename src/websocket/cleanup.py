"""
WebSocket Cleanup Module
Version: 1.0
Timestamp: 2025-04-20 14:09 CET

This module contains functions for cleaning up WebSocket resources.
"""

import time

from src import logger
from src.logging import log_connection, log_error
from websocket.state import ConnectionState
from websocket.connection import ConnectionManager
import config


def handle_instance_deletion(client_id):
    """Remove this instance when garbage collected"""
    try:
        ConnectionManager.unregister_instance(client_id)
    except Exception as e:
        # Ignore errors during shutdown, but log them in debug mode
        try:
            logger.debug("Error during instance cleanup in __del__: %s" % e)
        except Exception:
            pass  # Suppress any errors in logging during shutdown


def perform_cleanup(ws_instance):
    """Release resources with enhanced timeout handling and logging"""
    if not ws_instance.ws:
        return

    cleanup_start = time.time()
    log_connection(logger, "Starting cleanup for session %s..." % ws_instance.session_id)

    try:
        # Set a timeout for the entire cleanup operation
        cleanup_timeout = config.WS_CLEANUP_TIMEOUT

        # Disable processing
        ws_instance.processing_enabled = False

        # Close WebSocket connection
        if ws_instance.ws and ws_instance.ws.sock:
            ws_instance._set_state(ConnectionState.CLOSING)
            close_start = time.time()
            log_connection(logger, "Closing WebSocket connection...")
            if ws_instance.ws:  # Check if ws is not None
                ws_instance.ws.close()
            else:
                log_error(
                    logger,
                    "Attempted to close WebSocket during cleanup while it was None",
                )
            close_duration = time.time() - close_start
            log_connection(logger, "WebSocket close() completed in %.2fs" % close_duration)

        # Wait for thread to terminate
        if ws_instance.ws_thread and ws_instance.ws_thread.is_alive():
            join_start = time.time()
            thread_wait_msg = (
                "Waiting for WebSocket thread to terminate (timeout: %ds)..."
                % config.WS_THREAD_TIMEOUT
            )
            log_connection(logger, thread_wait_msg)
            ws_instance.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)

            # Check if thread is still alive after join timeout
            if ws_instance.ws_thread.is_alive():
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
        ws_instance.ws = None
        ws_instance._set_state(ConnectionState.DISCONNECTED)
        ws_instance.server_ready = False
        cleanup_duration = time.time() - cleanup_start
        cleanup_msg = "Cleanup completed for session %s in %.2fs" % (
            ws_instance.session_id,
            cleanup_duration,
        )
        log_connection(logger, cleanup_msg)
