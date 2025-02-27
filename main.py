"""
Main Program for the Whisper Client
Version: 1.0
Timestamp: 2025-02-27 17:30 CET

This is the main entry point for the Whisper Client application.
It initializes all components, manages the application lifecycle,
and handles user interactions through hotkeys.
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
        """Starts the client"""
        # Hotkeys registrieren
        self.hotkey_manager.register_hotkey(config.HOTKEY_TOGGLE_RECORDING, self.toggle_recording)
        self.hotkey_manager.register_hotkey(config.HOTKEY_EXIT, self.cleanup)
        self.hotkey_manager.start()
        
        # Verbindung aufbauen
        try:
            self.websocket.connect()
        except Exception as e:
            logger.error(f"⚠️ Connection error: {e}")
            return False
        
        # Hauptschleife
        try:
            while self.running:
                if not self.websocket.connected and self.running:
                    try:
                        self.websocket.connect()
                    except:
                        pass
                time.sleep(config.MAIN_POLL_INTERVAL)
        except KeyboardInterrupt:
            self.cleanup()
            
        return True
    
    def on_text_segments(self, segments):
        """Callback for new text segments"""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.websocket_terminal.id)
        # Textsegmente verarbeiten
        self.text_manager.process_segments(segments)
    
    def toggle_recording(self):
        """Start/stop recording"""
        if not self.audio_manager.recording:
            if not self.websocket.connected:
                logger.error("⚠️ No connection to server")
                return
            # Aktiviere Verarbeitung und starte Aufnahme
            self.websocket.start_processing()
            self.audio_manager.start_recording(self.on_audio_data)
            # Terminal-Aktivität aktualisieren
            self.terminal_manager.update_activity(self.audio_terminal.id)
        else:
            # Beende zuerst die Aufnahme
            logger.info("Stopping recording...")
            self.audio_manager.stop_recording()
            
            # Dann sende END_OF_AUDIO und warte auf letzte Texte
            logger.info("Waiting for final texts from server...")
            self.websocket.stop_processing()
    
    def on_audio_data(self, audio_data):
        """Callback for audio data"""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.audio_terminal.id)
        # Audio-Daten senden
        self.websocket.send_audio(audio_data)
    
    def cleanup(self):
        """Release resources and exit program"""
        logger.info("\n🛑 Program is shutting down...")
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
        
        # Wait briefly so the main loop can terminate
        time.sleep(config.MAIN_SHUTDOWN_WAIT)
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
            logger.error("⚠️ Client could not be started")
            sys.exit(1)
    except Exception as e:
        logger.error(f"\n⚠️ Critical error: {e}")
        logger.error("🛑 Program is shutting down...")
        sys.exit(1)

if __name__ == "__main__":
    try:
        # Task-Historie aktualisieren
        update_task_history(
            description="Code Restructuring",
            changes=[
                {
                    "type": "refactor",
                    "description": "Split code into separate modules for better maintainability"
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
        logger.debug(f"Task history could not be updated: {e}")
    
    main()
