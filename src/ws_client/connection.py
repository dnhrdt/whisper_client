"""
WebSocket Connection Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:18 CET

This module handles the core connection functionality for the WebSocket client,
including connection establishment, reconnection logic, and instance tracking.
"""

import threading
import time
import uuid
from typing import Dict

import config
import websocket
from src import logger
from src.logging import log_connection, log_error

from .state import ConnectionState


class ConnectionManager:
    """Manages WebSocket connections and instance tracking"""

    # Class-level variable to track active instances
    _active_instances: Dict[str, "WhisperWebSocket"] = {}
    _instances_lock = threading.Lock()

    @classmethod
    def register_instance(cls, instance):
        """Register a WebSocket instance"""
        with cls._instances_lock:
            cls._active_instances[instance.client_id] = instance

    @classmethod
    def unregister_instance(cls, client_id):
        """Unregister a WebSocket instance"""
        with cls._instances_lock:
            if client_id in cls._active_instances:
                del cls._active_instances[client_id]

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
            "Starting cleanup of all WebSocket instances (%d active)...",
            cls.get_instance_count(),
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
                log_error(logger, "Error cleaning up instance %s: %s", instance.client_id, str(e))

        # Check if cleanup took too long
        cleanup_duration = time.time() - cleanup_start
        if cleanup_duration > config.WS_CLEANUP_TIMEOUT:
            log_error(
                logger,
                "Cleanup of all instances took longer than expected: %.2fs",
                cleanup_duration,
            )

        # Final cleanup status
        log_connection(
            logger,
            "Cleanup completed: %d successful, %d failed, duration: %.2fs",
            success_count,
            error_count,
            cleanup_duration,
        )

        # Check if any instances remain
        remaining = cls.get_instance_count()
        if remaining > 0:
            log_error(
                logger, "Warning: %d WebSocket instances still active after cleanup", remaining
            )


def create_websocket_app(url, on_open, on_message, on_error, on_close):
    """Creates a WebSocketApp instance"""
    return websocket.WebSocketApp(
        url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
    )


def generate_client_id():
    """Generate a unique client ID"""
    return str(uuid.uuid4())


def generate_session_id():
    """Generate a unique session ID"""
    return str(uuid.uuid4())
