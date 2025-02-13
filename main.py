"""
Hauptprogramm des Whisper-Clients
"""
import sys
import time
import websocket
import config
import uuid
from src.audio import AudioManager
from src.websocket import WhisperWebSocket
from src.text import TextManager
from src.utils import check_server_status, show_startup_message, show_server_error, update_task_history
from src.hotkeys import HotkeyManager
from src.terminal import TerminalManager
from src import logger

class WhisperClient:
    def __init__(self):
        # WebSocket-Trace deaktivieren
        websocket.enableTrace(False)
        
        # Terminal-Manager initialisieren
        self.terminal_manager = TerminalManager()
        
        # Komponenten initialisieren
        self.text_manager = TextManager()
        self.websocket = WhisperWebSocket()
        self.audio_manager = AudioManager()
        self.hotkey_manager = HotkeyManager()
        
        # Terminals registrieren
        self.websocket_terminal = self.terminal_manager.register_terminal(
            id=f"ws_{uuid.uuid4().hex[:8]}", 
            name="WebSocket-Terminal"
        )
        self.audio_terminal = self.terminal_manager.register_terminal(
            id=f"audio_{uuid.uuid4().hex[:8]}", 
            name="Audio-Terminal"
        )
        
        # Flag für Programmstatus
        self.running = True
        
        # Callbacks setzen
        self.websocket.set_text_callback(self.on_text_segments)
    
    def start(self):
        """Startet den Client"""
        # Hotkeys registrieren
        self.hotkey_manager.register_hotkey(config.HOTKEY_TOGGLE_RECORDING, self.toggle_recording)
        self.hotkey_manager.register_hotkey(config.HOTKEY_EXIT, self.cleanup)
        self.hotkey_manager.start()
        
        # Verbindung aufbauen
        try:
            self.websocket.connect()
        except Exception as e:
            logger.error(f"⚠️ Verbindungsfehler: {e}")
            return False
        
        # Hauptschleife
        try:
            while self.running:
                if not self.websocket.connected and self.running:
                    try:
                        self.websocket.connect()
                    except:
                        pass
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.cleanup()
            
        return True
    
    def on_text_segments(self, segments):
        """Callback für neue Textsegmente"""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.websocket_terminal.id)
        # Textsegmente verarbeiten
        self.text_manager.process_segments(segments)
    
    def toggle_recording(self):
        """Aufnahme starten/stoppen"""
        if not self.audio_manager.recording:
            if not self.websocket.connected:
                logger.error("⚠️ Keine Verbindung zum Server")
                return
            # Aktiviere Verarbeitung und starte Aufnahme
            self.websocket.start_processing()
            self.audio_manager.start_recording(self.on_audio_data)
            # Terminal-Aktivität aktualisieren
            self.terminal_manager.update_activity(self.audio_terminal.id)
        else:
            # Stoppe zuerst die Aufnahme
            self.audio_manager.stop_recording()
            # Dann die Verarbeitung (inkl. 20s Wartezeit auf letzte Segmente)
            self.websocket.stop_processing()
    
    def on_audio_data(self, audio_data):
        """Callback für Audio-Daten"""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.audio_terminal.id)
        # Audio-Daten senden
        self.websocket.send_audio(audio_data)
    
    def cleanup(self):
        """Ressourcen freigeben und Programm beenden"""
        logger.info("\n🛑 Programm wird beendet...")
        self.running = False  # Hauptschleife beenden
        
        # Stoppe zuerst die Aufnahme
        self.audio_manager.stop_recording()
        
        # Dann die Verarbeitung
        self.websocket.stop_processing()
        
        # Komponenten beenden
        self.audio_manager.cleanup()
        self.websocket.cleanup()
        self.hotkey_manager.stop()
        self.terminal_manager.cleanup()
        
        # Warte kurz damit die Hauptschleife beendet werden kann
        time.sleep(0.2)
        sys.exit(0)

def main():
    # Startmeldung anzeigen
    show_startup_message()
    
    # Prüfe Server-Status
    if not check_server_status():
        show_server_error()
        sys.exit(1)
    
    try:
        # Client starten
        client = WhisperClient()
        if not client.start():
            logger.error("⚠️ Client konnte nicht gestartet werden")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n⚠️ Kritischer Fehler: {e}")
        logger.error("🛑 Programm wird beendet...")
        sys.exit(1)

if __name__ == "__main__":
    try:
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
    except Exception as e:
        logger.debug(f"Task-Historie konnte nicht aktualisiert werden: {e}")
    
    main()
