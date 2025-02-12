"""
Hauptprogramm des Whisper-Clients
"""
import sys
import time
import websocket
from src.audio import AudioManager
from src.websocket import WhisperWebSocket
from src.text import TextManager
from src.utils import check_server_status, show_startup_message, show_server_error, update_task_history
from src.hotkeys import HotkeyManager
from src import logging
import config

logger = logging.get_logger()

class WhisperClient:
    def __init__(self):
        # WebSocket-Trace deaktivieren
        websocket.enableTrace(False)
        
        # Manager initialisieren
        self.text_manager = TextManager()
        self.websocket = WhisperWebSocket()
        self.audio_manager = AudioManager()
        self.hotkey_manager = HotkeyManager()
        
        # Callback für Textsegmente setzen
        self.websocket.set_text_callback(self.text_manager.process_segments)
    
    def start(self):
        """Startet den Client"""
        # Verbindung aufbauen
        self.websocket.connect()
        
        # Hotkeys registrieren
        self.hotkey_manager.register_hotkey(config.HOTKEY_TOGGLE_RECORDING, self.toggle_recording)
        self.hotkey_manager.register_hotkey(config.HOTKEY_EXIT, self.cleanup)
        self.hotkey_manager.start()
        
        # Startmeldung anzeigen
        show_startup_message()
        
        # Hauptschleife
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.cleanup()
    
    def toggle_recording(self):
        """Aufnahme starten/stoppen"""
        if not self.audio_manager.recording:
            if not self.websocket.connected:
                logger.error("⚠️ Keine Verbindung zum Server")
                return
            self.audio_manager.start_recording(self.websocket.send_audio)
        else:
            self.audio_manager.stop_recording()
    
    def cleanup(self):
        """Ressourcen freigeben und Programm beenden"""
        logger.info("\n🛑 Programm wird beendet...")
        self.audio_manager.cleanup()
        self.websocket.cleanup()
        self.hotkey_manager.stop()
        sys.exit(0)

def main():
    # Prüfe Server-Status
    if not check_server_status():
        show_server_error()
        sys.exit(1)
    
    try:
        # Client starten
        client = WhisperClient()
        client.start()
    except Exception as e:
        logger.error(f"\n⚠️ Kritischer Fehler: {e}")
        logger.error("🛑 Programm wird beendet...")
        sys.exit(1)

if __name__ == "__main__":
    # Task-Historie aktualisieren
    update_task_history(
        description="Code-Restrukturierung",
        changes=[
            {
                "type": "refactor",
                "description": "Code in separate Module aufgeteilt für bessere Wartbarkeit"
            }
        ],
        status="in_development",
        files=[
            "src/audio.py",
            "src/websocket.py",
            "src/logging.py",
            "src/text.py",
            "src/utils.py",
            "main.py",
            "config.py"
        ]
    )
    main()
