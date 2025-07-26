"""
Main Program for the Whisper Client
Version: 1.8
Timestamp: 2025-04-20 18:14 CET

This is the main entry point for the Whisper Client application.
It initializes all components, manages the application lifecycle,
and handles user interactions through hotkeys.
"""

import sys
import time
import uuid

import config
import websocket
from src import logger
from src.audio import AudioManager, AudioProcessor
from src.hotkeys import HotkeyManager
from src.logging import log_debug, log_error, log_info, log_warning
from src.terminal import TerminalManager
from src.text import TextManager
from src.utils import (
    check_server_status,
    show_server_error,
    show_startup_message,
    update_task_history,
)
from src.ws_client import ConnectionState, WhisperWebSocket
from src.ws_client.connection import ConnectionManager


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
        self.audio_processor = AudioProcessor()
        self.hotkey_manager = HotkeyManager()

        # Terminals registrieren
        self.websocket_terminal = self.terminal_manager.register_terminal(
            id=f"ws_{uuid.uuid4().hex[:8]}", name="WebSocket-Terminal"
        )
        self.audio_terminal = self.terminal_manager.register_terminal(
            id=f"audio_{uuid.uuid4().hex[:8]}", name="Audio-Terminal"
        )

        # Flag für Programmstatus
        self.running = True

        # Callbacks setzen
        self.websocket.set_text_callback(self.on_text_segments)

    def start(self):
        """Starts the client."""
        # Hotkeys registrieren
        self.hotkey_manager.register_hotkey(config.HOTKEY_TOGGLE_RECORDING, self.toggle_recording)
        self.hotkey_manager.register_hotkey(config.HOTKEY_EXIT, self.cleanup)
        self.hotkey_manager.start()

        # Verbindung aufbauen
        try:
            self.websocket.connect()
        except Exception as e:
            log_error(logger, "⚠️ Connection error: %s", e)
            return False

        # Hauptschleife
        try:
            while self.running:
                if self.websocket.state == ConnectionState.DISCONNECTED and self.running:
                    try:
                        self.websocket.connect()
                    except Exception:
                        pass
                time.sleep(config.MAIN_POLL_INTERVAL)
        except KeyboardInterrupt:
            self.cleanup()

        return True

    def on_text_segments(self, segments):
        """Callback for new text segments."""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.websocket_terminal.id)
        # Textsegmente verarbeiten
        self.text_manager.process_segments(segments)

    def toggle_recording(self):
        """Start/stop recording."""
        if not self.audio_manager.recording:
            if self.websocket.state != ConnectionState.READY:
                log_error(logger, "⚠️ No connection to server")
                return
            # Aktiviere Verarbeitung und starte Aufnahme
            self.websocket.start_processing()

            # Start audio processing with tumbling window
            self.audio_processor.start_processing(self.on_processed_audio)

            # Start audio recording
            self.audio_manager.start_recording(self.on_audio_data)

            # Terminal-Aktivität aktualisieren
            self.terminal_manager.update_activity(self.audio_terminal.id)
        else:
            # Beende zuerst die Aufnahme
            log_info(logger, "Stopping recording...")
            self.audio_manager.stop_recording()

            # Stop audio processing
            self.audio_processor.stop_processing()

            # Dann sende END_OF_AUDIO und warte auf letzte Texte
            log_info(logger, "Waiting for final texts from server...")
            self.websocket.stop_processing()

    def on_audio_data(self, audio_data):
        """Callback for raw audio data."""
        # Terminal-Aktivität aktualisieren
        self.terminal_manager.update_activity(self.audio_terminal.id)
        # Process audio data through tumbling window
        self.audio_processor.process_audio(audio_data)

    def on_processed_audio(self, processed_audio):
        """Callback for processed audio data from tumbling window."""
        # Send processed audio to WebSocket
        self.websocket.send_audio(processed_audio)

    def cleanup(self):
        """Release resources and exit program."""
        log_info(logger, "\n🛑 Program is shutting down...")
        self.running = False  # Hauptschleife beenden

        # Stoppe zuerst die Aufnahme
        self.audio_manager.stop_recording()

        # Stop audio processing
        self.audio_processor.stop_processing()

        # Dann die Verarbeitung
        self.websocket.stop_processing()

        # Komponenten beenden
        self.audio_manager.cleanup()
        self.websocket.cleanup()

        # Cleanup all WebSocket instances to prevent multiple parallel connections
        log_info(logger, "Cleaning up all WebSocket instances...")
        ConnectionManager.cleanup_all_instances()

        self.hotkey_manager.stop()
        self.terminal_manager.cleanup()

        # Wait briefly so the main loop can terminate
        time.sleep(config.HOTKEY_SHUTDOWN_WAIT)  # Correct constant name (added space for E261)
        sys.exit(0)


def main():
    # Startmeldung anzeigen
    show_startup_message()

    # Check for existing WebSocket instances and clean them up
    instance_count = ConnectionManager.get_instance_count()
    if instance_count > 0:
        log_warning(logger, "Found %d existing WebSocket instances. Cleaning up...", instance_count)
        ConnectionManager.cleanup_all_instances()

    # Prüfe Server-Status
    if not check_server_status():
        show_server_error()
        sys.exit(1)

    try:
        # Client starten
        client = WhisperClient()
        if not client.start():
            log_error(logger, "⚠️ Client could not be started")
            sys.exit(1)
    except Exception as e:
        log_error(logger, "\n⚠️ Critical error: %s", e)
        log_error(logger, "🛑 Program is shutting down...")
        sys.exit(1)


if __name__ == "__main__":
    try:
        # Task-Historie aktualisieren
        update_task_history(
            description="Multiple Parallel Connections Fix",
            changes=[
                {"type": "fix", "description": "Addressed multiple parallel connections issue"},
                {
                    "type": "feat",
                    "description": "Added client and session tracking for WebSocket connections",
                },
                {
                    "type": "improvement",
                    "description": "Enhanced cleanup process to prevent orphaned connections",
                },
                {
                    "type": "refactor",
                    "description": "Improved connection management with throttling",
                },
            ],
            status="in_development",
            files=["main.py", "src/websocket.py"],
        )
    except Exception as e:
        log_debug(logger, "Task history could not be updated: %s", e)

    main()
