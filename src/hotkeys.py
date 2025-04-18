"""
Hotkey Management for the Whisper Client
Version: 1.2
Timestamp: 2025-04-15 01:07 CET

This module provides hotkey detection and management for the Whisper Client.
It handles F13/F14 key detection and triggers appropriate callbacks when
hotkeys are pressed or released.
"""

import threading
import time

import win32api
import win32con

import config
from src import logger


class HotkeyManager:
    def __init__(self):
        self.running = False
        self.callbacks = {}
        self.thread = None

        # Hotkey-Mappings
        self.HOTKEYS = {"f13": (0, win32con.VK_F13), "f14": (0, win32con.VK_F14)}

    def register_hotkey(self, hotkey, callback):
        """Registers a hotkey with callback"""
        if hotkey not in self.HOTKEYS:
            logger.error("⚠️ Unknown hotkey: %s", hotkey)
            return False

        self.callbacks[hotkey] = callback
        return True

    def _execute_callback(self, hotkey):
        """Executes the callback for a given hotkey."""
        callback = self.callbacks.get(hotkey)
        if callback:
            try:
                callback()
            except Exception as e:
                logger.error("Error in callback for %s: %s", hotkey, e)

    def _check_hotkeys(self):
        """Checks the status of registered hotkeys"""
        key_states = {key: False for key in self.HOTKEYS}  # Stores the key state

        while self.running:
            try:
                for hotkey, (_, vk_code) in self.HOTKEYS.items():  # Ignore mods
                    # Check current key state
                    is_pressed = bool(win32api.GetAsyncKeyState(vk_code) & 0x8000)

                    # Key was just pressed
                    if is_pressed and not key_states[hotkey]:
                        key_states[hotkey] = True
                        if hotkey == "f13":
                            logger.debug("Recording started (F13)")
                        elif hotkey == "f14":
                            logger.debug("Program is exiting (F14)")
                        else:
                            logger.debug("Key %s pressed", hotkey)

                        # Execute the callback using the helper method
                        self._execute_callback(hotkey)

                    # Key was released
                    elif not is_pressed and key_states[hotkey]:
                        key_states[hotkey] = False
                        if hotkey == "f13":
                            logger.debug("Recording stopped (F13)")
                        elif hotkey == "f14":
                            logger.debug("Program exited (F14)")
                        else:
                            logger.debug("Key %s released", hotkey)

                time.sleep(config.HOTKEY_POLL_INTERVAL)  # Polling interval for hotkey checking

            except Exception as e:
                logger.error("Error checking hotkeys: %s", e)
                time.sleep(config.HOTKEY_ERROR_DELAY)  # Wait time after errors

    def start(self):
        """Starts hotkey monitoring"""
        if self.running:
            return

        self.running = True
        self.thread = threading.Thread(target=self._check_hotkeys)
        self.thread.daemon = True
        self.thread.start()
        logger.debug("✓ Hotkey system started")

    def stop(self):
        """Stops hotkey monitoring"""
        if not self.running:
            return

        logger.debug("Stopping hotkey system...")
        self.running = False

        # Wait briefly so the thread detects the running=False change
        time.sleep(config.HOTKEY_SHUTDOWN_WAIT)

        if self.thread and threading.current_thread() != self.thread:
            try:
                if self.thread.is_alive():
                    logger.debug("Waiting for hotkey thread...")
                    self.thread.join(timeout=config.HOTKEY_THREAD_TIMEOUT)
                    if self.thread.is_alive():
                        logger.warning("Hotkey thread not responding - Terminating thread...")
            except RuntimeError as e:
                logger.debug("Thread join skipped: %s", e)
            finally:
                self.thread = None

        logger.debug("✓ Hotkey system stopped")
