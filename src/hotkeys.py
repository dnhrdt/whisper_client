"""
Hotkey-Verwaltung für den Whisper-Client
"""
import win32con
import win32api
import win32gui
import threading
import time
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
        """Registriert einen Hotkey mit Callback"""
        if hotkey not in self.HOTKEYS:
            logger.error(f"⚠️ Unbekannter Hotkey: {hotkey}")
            return False
            
        self.callbacks[hotkey] = callback
        return True
    
    def _check_hotkeys(self):
        """Prüft den Status der registrierten Hotkeys"""
        key_states = {key: False for key in self.HOTKEYS.keys()}  # Speichert den Tastenzustand
        
        while self.running:
            try:
                for hotkey, (mods, vk_code) in self.HOTKEYS.items():
                    # Prüfe aktuellen Tastenzustand
                    is_pressed = bool(win32api.GetAsyncKeyState(vk_code) & 0x8000)
                    
                    # Taste wurde gerade gedrückt
                    if is_pressed and not key_states[hotkey]:
                        key_states[hotkey] = True
                        if hotkey == 'f13':
                            logger.debug("Aufnahme gestartet (F13)")
                        elif hotkey == 'f14':
                            logger.debug("Programm wird beendet (F14)")
                        else:
                            logger.debug(f"Taste {hotkey} gedrückt")
                            
                        callback = self.callbacks.get(hotkey)
                        if callback:
                            try:
                                callback()
                            except Exception as e:
                                logger.error(f"Fehler im Callback für {hotkey}: {e}")
                    
                    # Taste wurde losgelassen
                    elif not is_pressed and key_states[hotkey]:
                        key_states[hotkey] = False
                        if hotkey == 'f13':
                            logger.debug("Aufnahme gestoppt (F13)")
                        elif hotkey == 'f14':
                            logger.debug("Programm beendet (F14)")
                        else:
                            logger.debug(f"Taste {hotkey} losgelassen")
                
                time.sleep(0.05)  # Reduzierte Wartezeit für bessere Reaktion
                
            except Exception as e:
                logger.error(f"Fehler bei Hotkey-Prüfung: {e}")
                time.sleep(0.1)  # Kurze Pause bei Fehlern
    
    def start(self):
        """Startet die Hotkey-Überwachung"""
        if self.running:
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._check_hotkeys)
        self.thread.daemon = True
        self.thread.start()
        logger.debug("✓ Hotkey-System gestartet")
    
    def stop(self):
        """Stoppt die Hotkey-Überwachung"""
        if not self.running:
            return
            
        logger.debug("Beende Hotkey-System...")
        self.running = False
        
        # Warte kurz damit der Thread die running=False Änderung mitbekommt
        time.sleep(0.1)
        
        if self.thread and threading.current_thread() != self.thread:
            try:
                if self.thread.is_alive():
                    logger.debug("Warte auf Hotkey-Thread...")
                    self.thread.join(timeout=2.0)
                    if self.thread.is_alive():
                        logger.warning("Hotkey-Thread reagiert nicht - Beende Thread...")
            except RuntimeError as e:
                logger.debug(f"Thread-Join übersprungen: {e}")
            finally:
                self.thread = None
                
        logger.debug("✓ Hotkey-System gestoppt")
