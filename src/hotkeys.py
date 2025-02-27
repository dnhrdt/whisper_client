"""
Hotkey Management for the Whisper Client
Version: 1.0
Timestamp: 2025-02-27 17:12 CET

This module provides hotkey detection and management for the Whisper Client.
It handles F13/F14 key detection and triggers appropriate callbacks when
hotkeys are pressed or released.
"""
import win32con
import win32api
import win32gui
import threading
import time
import config
from src import logger

class HotkeyManager:
    def __init__(self):
        self.running = False
        self.callbacks = {}
        self.thread = None
        
        # Hotkey-Mappings
        self.HOTKEYS = {
            'f13': (0, win32con.VK_F13),
            'f14': (0, win32con.VK_F14)
        }
    
    def register_hotkey(self, hotkey, callback):
        """Registers a hotkey with callback"""
        if hotkey not in self.HOTKEYS:
            logger.error(f"⚠️ Unknown hotkey: {hotkey}")
            return False
            
        self.callbacks[hotkey] = callback
        return True
    
    def _check_hotkeys(self):
        """Checks the status of registered hotkeys"""
        key_states = {key: False for key in self.HOTKEYS.keys()}  # Stores the key state
        
        while self.running:
            try:
                for hotkey, (mods, vk_code) in self.HOTKEYS.items():
                    # Check current key state
                    is_pressed = bool(win32api.GetAsyncKeyState(vk_code) & 0x8000)
                    
                    # Key was just pressed
                    if is_pressed and not key_states[hotkey]:
                        key_states[hotkey] = True
                        if hotkey == 'f13':
                            logger.debug("Recording started (F13)")
                        elif hotkey == 'f14':
                            logger.debug("Program is exiting (F14)")
                        else:
                            logger.debug(f"Key {hotkey} pressed")
                            
                        callback = self.callbacks.get(hotkey)
                        if callback:
                            try:
                                callback()
                            except Exception as e:
                                logger.error(f"Error in callback for {hotkey}: {e}")
                    
                    # Key was released
                    elif not is_pressed and key_states[hotkey]:
                        key_states[hotkey] = False
                        if hotkey == 'f13':
                            logger.debug("Recording stopped (F13)")
                        elif hotkey == 'f14':
                            logger.debug("Program exited (F14)")
                        else:
                            logger.debug(f"Key {hotkey} released")
                
                time.sleep(config.HOTKEY_POLL_INTERVAL)  # Polling interval for hotkey checking
                
            except Exception as e:
                logger.error(f"Error checking hotkeys: {e}")
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
                logger.debug(f"Thread join skipped: {e}")
            finally:
                self.thread = None
                
        logger.debug("✓ Hotkey system stopped")
