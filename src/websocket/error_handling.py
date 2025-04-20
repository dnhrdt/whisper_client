"""
WebSocket Error Handling Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 13:02 CET

This module provides error handling and recovery functionality
for the WebSocket client.
"""

import time

import config
from src import logger
from src.logging import log_connection, log_error


def handle_connection_error(error, state, client_id, session_id, server_ready, processing_enabled):
    """Handle WebSocket connection errors"""
    log_error(logger, "WebSocket error: %s" % str(error))

    # Log additional context for the error
    try:
        error_context = (
            "Error context - State: %s, Client ID: %s, Session ID: %s, Server ready: %s, Processing enabled: %s"
            % (
                state.name,
                client_id,
                session_id,
                server_ready,
                processing_enabled,
            )
        )
        log_error(logger, error_context)
    except Exception as e:
        # Ignore errors in error logging, but try to log a basic message
        try:
            logger.debug("Error while logging error context: %s" % e)
        except Exception:
            pass  # Suppress any errors in logging during error handling


def handle_connection_close(close_status_code, close_msg):
    """Handle WebSocket connection close events"""
    log_msg = "Connection closed"
    if close_status_code:
        log_msg += " (Status: %s)" % close_status_code
    if close_msg:
        log_msg += " (Message: %s)" % close_msg
    log_connection(logger, log_msg)


def wait_with_timeout(condition_func, timeout, operation_name, poll_interval=None):
    """Wait for a condition with timeout"""
    if poll_interval is None:
        poll_interval = config.WS_POLL_INTERVAL

    start_time = time.time()
    last_log_time = start_time
    log_interval = config.WS_STATE_LOG_INTERVAL

    while not condition_func():
        current_time = time.time()

        # Check for timeout
        if current_time - start_time > timeout:
            log_error(logger, "%s timeout after %ds" % (operation_name, timeout))
            return False

        # Periodically log status
        if current_time - last_log_time >= log_interval:
            last_log_time = current_time
            log_connection(
                logger,
                "[%s] Waiting... (%.1fs elapsed, timeout: %ds)" % (
                    operation_name,
                    current_time - start_time,
                    timeout,
                )
            )

        # Short pause
        time.sleep(poll_interval)

    # Success
    duration = time.time() - start_time
    log_connection(logger, "%s completed in %.2fs" % (operation_name, duration))
    return True
