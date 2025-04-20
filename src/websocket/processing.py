"""
WebSocket Processing Module
Version: 1.0
Timestamp: 2025-04-20 14:07 CET

This module contains functions for processing WebSocket messages and data.
"""

import time

import win32clipboard

import config
from src import logger
from src.logging import log_connection, log_error
from websocket.state import ConnectionState
from websocket.messaging import send_audio_data as send_audio_to_server
from websocket.messaging import send_end_of_audio as send_eoa_to_server
from websocket.error_handling import wait_with_timeout


def send_audio_data(ws_instance, audio_data):
    """Sends audio data to the server with enhanced error handling"""
    if not ws_instance.processing_enabled or not ws_instance.is_ready():
        return False

    success = send_audio_to_server(ws_instance.ws, audio_data)
    if not success:
        ws_instance._set_state(ConnectionState.CONNECT_ERROR)

    return success


def send_end_of_audio_signal(ws_instance):
    """Sends END_OF_AUDIO signal to the server with enhanced timeout handling"""
    if not ws_instance.is_ready() and ws_instance.state != ConnectionState.PROCESSING:
        return False

    try:
        ws_instance._set_state(ConnectionState.FINALIZING)
        success = send_eoa_to_server(ws_instance.ws)
        if not success:
            return False

        log_connection(
            logger, "Waiting for final segments (timeout: %ds)..." % config.WS_FINAL_WAIT
        )

        # Wait for server to acknowledge END_OF_AUDIO with timeout
        wait_start = time.time()
        while ws_instance.state == ConnectionState.FINALIZING:
            if time.time() - wait_start > config.WS_FINAL_WAIT:
                log_connection(
                    logger, "Final wait timeout reached after %ds" % config.WS_FINAL_WAIT
                )
                break

            # Periodically log state during finalization
            ws_instance._log_state_periodically("finalization_wait")
            time.sleep(config.WS_POLL_INTERVAL)

        wait_duration = time.time() - wait_start
        log_connection(logger, "Finalization completed in %.2fs" % wait_duration)
        return True
    except Exception as e:
        log_error(logger, "Error sending END_OF_AUDIO: %s" % str(e))
        return False


def start_message_processing(ws_instance):
    """Starts processing server messages with enhanced error handling"""
    if not ws_instance.is_ready():
        not_ready_msg = "Server not ready for processing (current state: %s)" % ws_instance.state.name
        log_error(logger, not_ready_msg)
        return False

    start_time = time.time()
    log_connection(logger, "Starting message processing...")

    ws_instance.processing_enabled = True
    ws_instance.current_text = ""

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

        ws_instance._set_state(ConnectionState.PROCESSING)
        total_duration = time.time() - start_time
        log_connection(logger, "Server message processing enabled in %.2fs" % total_duration)
        return True

    except Exception as e:
        log_error(logger, "Error starting processing: %s" % str(e))
        ws_instance.processing_enabled = False
        return False


def stop_message_processing(ws_instance):
    """Stops processing server messages with enhanced timeout handling"""
    if ws_instance.processing_enabled:
        stop_start = time.time()
        log_connection(logger, "Stopping message processing...")

        try:
            if ws_instance.is_ready() or ws_instance.state == ConnectionState.PROCESSING:
                # Send END_OF_AUDIO and wait for processing
                ws_instance._set_state(ConnectionState.FINALIZING)
                send_eoa_to_server(ws_instance.ws)

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
                    ws_instance._log_state_periodically("stop_processing_wait")

                    # Short pause
                    time.sleep(config.WS_POLL_INTERVAL)

                # Disable processing
                ws_instance.processing_enabled = False
                ws_instance.current_text = ""

                # Close connection cleanly
                ws_instance._set_state(ConnectionState.CLOSING)
                log_connection(logger, "Closing connection...")
                close_start = time.time()
                if ws_instance.ws:  # Check if ws is not None
                    ws_instance.ws.close()
                else:
                    log_error(
                        logger,
                        "Attempted to close WebSocket during stop_processing "
                        "while it was None",
                    )
                close_duration = time.time() - close_start
                log_connection(logger, "Connection close() completed in %.2fs" % close_duration)

                # Wait for thread to end with timeout
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
            ws_instance.processing_enabled = False
            ws_instance._set_state(ConnectionState.CLOSED)
            ws_instance.server_ready = False
            stop_duration = time.time() - stop_start
            log_connection(logger, "Processing stopped in %.2fs" % stop_duration)
