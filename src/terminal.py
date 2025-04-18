"""
Terminal Management for the Whisper Client
Version: 1.3
Timestamp: 2025-04-15 01:08 CET

This module provides terminal management functionality for the Whisper Client.
It tracks terminal status, handles terminal registration and cleanup, and
monitors terminals for inactivity.
"""

import subprocess
import threading
import time
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Optional

import config
from src import logger


class TerminalStatus(Enum):
    """Status of a terminal"""

    ACTIVE = "active"  # Terminal is active and in use
    INACTIVE = "inactive"  # Terminal is inactive (no activity for INACTIVITY_TIMEOUT)
    CLOSING = "closing"  # Terminal is being closed
    CLOSED = "closed"  # Terminal has been closed


@dataclass
class TerminalInfo:
    """Information about a terminal"""

    id: str  # Unique ID of the terminal
    name: str  # User-friendly name (e.g., "Audio Terminal")
    status: TerminalStatus  # Current status
    last_activity: float  # Timestamp of last activity
    process: Optional[object]  # Process handle (optional)


class TerminalManager:
    """Central management of all terminals"""

    def __init__(self):
        self.terminals: Dict[str, TerminalInfo] = {}
        self.lock = threading.Lock()

        # Start monitoring thread
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_terminals)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()

        logger.info("Terminal Manager started")

    def register_terminal(
        self, id: str, name: str, process: Optional[object] = None
    ) -> TerminalInfo:
        """
        Registers a new terminal

        Args:
            id: Unique ID of the terminal
            name: User-friendly name
            process: Optional, process handle

        Returns:
            TerminalInfo: Information about the registered terminal
        """
        with self.lock:
            if id in self.terminals:
                raise ValueError(f"Terminal with ID {id} already exists")

            terminal = TerminalInfo(
                id=id,
                name=name,
                status=TerminalStatus.ACTIVE,
                last_activity=time.time(),
                process=process,
            )
            self.terminals[id] = terminal
            logger.debug("Terminal registered: %s (ID: %s)", name, id)
            return terminal

    def update_activity(self, id: str):
        """Updates the timestamp of the last activity"""
        with self.lock:
            if id in self.terminals:
                self.terminals[id].last_activity = time.time()
                if self.terminals[id].status == TerminalStatus.INACTIVE:
                    self.terminals[id].status = TerminalStatus.ACTIVE
                    logger.debug("Terminal reactivated: %s", self.terminals[id].name)

    def close_terminal(self, id: str):
        """
        Closes a terminal

        Args:
            id: ID of the terminal to close
        """
        with self.lock:
            if id in self.terminals:
                terminal = self.terminals[id]
                if terminal.status not in [TerminalStatus.CLOSING, TerminalStatus.CLOSED]:
                    terminal.status = TerminalStatus.CLOSING
                    logger.debug("Terminal is being closed: %s", terminal.name)

                    # Prozess beenden falls vorhanden
                    if terminal.process and isinstance(terminal.process, subprocess.Popen):
                        try:
                            terminal.process.terminate()
                        except Exception as e:
                            logger.debug(
                                "Error terminating process for terminal %s: %s", terminal.name, e
                            )

                    terminal.status = TerminalStatus.CLOSED
                    logger.debug("Terminal closed: %s", terminal.name)

    def get_terminal_info(self, id: str) -> Optional[TerminalInfo]:
        """
        Returns information about a terminal

        Args:
            id: Terminal ID

        Returns:
            Optional[TerminalInfo]: Terminal information or None if not found
        """
        with self.lock:
            return self.terminals.get(id)

    def get_active_terminals(self) -> Dict[str, TerminalInfo]:
        """
        Returns all active terminals

        Returns:
            Dict[str, TerminalInfo]: Dictionary with terminal IDs and information
        """
        with self.lock:
            return {
                id: info
                for id, info in self.terminals.items()
                if info.status == TerminalStatus.ACTIVE
            }

    def _monitor_terminals(self):
        """
        Monitors terminals for inactivity
        Runs in its own thread
        """
        while self.monitoring:
            try:
                current_time = time.time()

                # List of terminals to close
                to_close = []

                with self.lock:
                    for id, terminal in self.terminals.items():
                        if terminal.status == TerminalStatus.ACTIVE:
                            inactive_time = current_time - terminal.last_activity
                            if inactive_time > config.TERMINAL_INACTIVITY_TIMEOUT:
                                terminal.status = TerminalStatus.INACTIVE
                                logger.debug("Terminal inactive: %s", terminal.name)
                                to_close.append(id)

                # Close inactive terminals
                for id in to_close:
                    self.close_terminal(id)

            except Exception as e:
                logger.error("Error in terminal monitor: %s", e)

            time.sleep(config.TERMINAL_MONITOR_INTERVAL)  # Interval for terminal monitoring

    def cleanup(self):
        """Release resources"""
        self.monitoring = False

        # Close all terminals
        with self.lock:
            for id in list(self.terminals.keys()):
                self.close_terminal(id)

        # Wait for monitor thread
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=config.TERMINAL_THREAD_TIMEOUT)

        logger.info("Terminal Manager stopped")
