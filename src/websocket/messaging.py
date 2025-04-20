"""
WebSocket Messaging Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 13:02 CET

This module handles message processing, sending and receiving data,
and callback handling for the WebSocket client.
"""

import json
import time

import websocket

import config
from src import logger
from src.logging import log_audio, log_connection, log_error, log_text


def send_config(ws, client_id, session_id):
    """Sends configuration to the server"""
    try:
        ws_config = {
            "uid": client_id,
            "session_id": session_id,
            "language": config.WHISPER_LANGUAGE,
            "task": config.WHISPER_TASK,
            "use_vad": config.WHISPER_USE_VAD,
            "backend": config.WHISPER_BACKEND,
        }
        json_str = json.dumps(ws_config).encode("utf-8")
        log_connection(logger, "Sending config: %s" % json.dumps(ws_config, indent=2))
        if ws:  # Check if ws is not None
            ws.send(json_str, websocket.ABNF.OPCODE_TEXT)
        return True
    except Exception as e:
        log_error(logger, "Error sending config: %s" % str(e))
        return False


def send_audio_data(ws, audio_data):
    """Sends audio data to the server"""
    try:
        send_start = time.time()
        if ws:  # Check if ws is not None
            ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
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
        return False


def send_end_of_audio(ws):
    """Sends END_OF_AUDIO signal to the server"""
    try:
        send_start = time.time()
        if ws:  # Check if ws is not None
            ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
        else:
            log_error(logger, "Attempted to send END_OF_AUDIO while WebSocket is None")
            return False
        send_duration = time.time() - send_start

        log_audio(logger, "Sent END_OF_AUDIO signal in %.3fs" % send_duration)
        return True
    except Exception as e:
        log_error(logger, "Error sending END_OF_AUDIO: %s" % str(e))
        return False


def process_message(message, on_text_callback=None, processing_enabled=True):
    """Process a message from the server"""
    if not processing_enabled:
        return None, None

    try:
        message_start = time.time()

        if isinstance(message, bytes):
            message = message.decode("utf-8")

        log_connection(logger, "Raw server message: %s" % message)
        data = json.loads(message)

        if "message" in data:
            if data["message"] == "SERVER_READY":
                return "SERVER_READY", None
            elif data["message"] == "END_OF_AUDIO_RECEIVED":
                return "END_OF_AUDIO_RECEIVED", None

        if "segments" in data:
            segments = data["segments"]
            if segments:
                # Take only the last complete text
                text = segments[-1].get("text", "").strip()
                log_text(logger, text)
                if on_text_callback:
                    callback_start = time.time()
                    on_text_callback([segments[-1]])
                    callback_duration = time.time() - callback_start
                    if callback_duration > config.WS_MESSAGE_WAIT:
                        log_connection(
                            logger, "Text callback took too long: %.2fs" % callback_duration
                        )
                return "TEXT", text

        # Check if message processing took too long
        message_duration = time.time() - message_start
        if message_duration > config.WS_MESSAGE_WAIT:
            log_connection(
                logger, "Message processing took longer than expected: %.2fs" % message_duration
            )

        return None, None
    except Exception as e:
        log_error(logger, "Error processing message: %s" % str(e))
        return "ERROR", str(e)
