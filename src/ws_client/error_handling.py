"""
WebSocket Error Handling Module for the Whisper Client
Version: 1.2
Timestamp: 2025-04-20 17:15 CET

This module provides error handling and recovery functionality
for the WebSocket client.
"""

import time

import config
from src import logger
from src.logging import log_connection, log_debug, log_error


def handle_connection_error(error, state, client_id, session_id, server_ready, processing_enabled):
    """Handle WebSocket connection errors"""
    log_error(logger, f"WebSocket error: {str(error)}")

    # Log additional context for the error
    try:
        log_error(
            logger,
            f"Error context - State: {state.name}, Client ID: {client_id}, Session ID: {session_id}, Server ready: {server_ready}, Processing enabled: {processing_enabled}",
        )
    except Exception as e:
        # Ignore errors in error logging, but try to log a basic message
        try:
            log_debug(logger, f"Error while logging error context: {e}")
        except Exception:
            pass  # Suppress any errors in logging during error handling


def handle_connection_close(close_status_code, close_msg):
    """Handle WebSocket connection close events"""
    if close_status_code and close_msg:
        log_connection(
            logger, f"Connection closed (Status: {close_status_code}) (Message: {close_msg})"
        )
    elif close_status_code:
        log_connection(logger, f"Connection closed (Status: {close_status_code})")
    elif close_msg:
        log_connection(logger, f"Connection closed (Message: {close_msg})")
    else:
        log_connection(logger, "Connection closed")


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
            log_error(logger, f"{operation_name} timeout after {timeout}s")
            return False

        # Periodically log status
        if current_time - last_log_time >= log_interval:
            last_log_time = current_time
            log_connection(
                logger,
                f"[{operation_name}] Waiting... ({current_time - start_time:.1f}s elapsed, timeout: {timeout}s)",
            )

        # Short pause
        time.sleep(poll_interval)

    # Success
    duration = time.time() - start_time
    log_connection(logger, f"{operation_name} completed in {duration:.2f}s")
    return True
