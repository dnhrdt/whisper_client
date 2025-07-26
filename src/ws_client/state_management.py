"""
WebSocket State Management Module
Version: 1.1
Timestamp: 2025-04-20 17:14 CET

This module contains functions for managing WebSocket connection states.
"""

import time

from src import logger
from src.logging import log_connection

from .connection import ConnectionManager


def set_connection_state(ws_instance, new_state):
    """Sets the connection state and logs the transition."""
    with ws_instance.connection_lock:
        old_state = ws_instance.state
        ws_instance.state = new_state
        log_connection(logger, f"State changed: {old_state.name} -> {new_state.name}")


def log_state_periodically(ws_instance, operation_name):
    """Log state periodically during long-running operations."""
    current_time = time.time()
    if current_time - ws_instance.last_state_log_time >= ws_instance.state_log_interval:
        ws_instance.last_state_log_time = current_time
        log_connection(
            logger,
            f"[{operation_name}] Current state: {ws_instance.state.name}, Active instances: {ConnectionManager.get_instance_count()}",
        )
