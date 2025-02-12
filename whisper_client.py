import json
import logging
import os
import threading
import time
import uuid
import sys
import keyboard
import pyaudio
import websocket
import numpy as np
import pyperclip
from datetime import datetime

class WhisperClient:
    def __init__(self, host="localhost", port=9090):
        self.setup_logging()
        self.recording = False
        self.recording_lock = threading.Lock()
        self.uid = str(uuid.uuid4())
        self.ws = None
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.ws_url = f"ws://{host}:{port}"
        
        # Audio-Einstellungen
        self.chunk = 4096
        self.format = pyaudio.paInt16
        self.channels = 1
        self.rate = 16000
        
        self.last_transcription = ""  # Vermeidet Wiederholungen
        self.connected = False  # Verbindungsstatus
        
    def setup_logging(self):
        """Logging-System einrichten"""
        # Logs-Verzeichnis erstellen
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # Log-Dateiname mit Datum
        log_file = os.path.join(log_dir, f"whisper_client_{datetime.now().strftime('%Y%m%d')}.log")
        
        # Logger konfigurieren
        self.logger = logging.getLogger("WhisperClient")
        self.logger.setLevel(logging.DEBUG)
        
        # File Handler
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(file_formatter)
        
        # Console Handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(message)s')  # Vereinfachtes Format für Konsole
        console_handler.setFormatter(console_formatter)
        
        # Handler hinzufügen
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)

    def connect(self):
        """WebSocket-Verbindung aufbauen"""
        try:
            if self.ws:
                self.ws.close()
                self.ws = None
                
            self.ws = websocket.WebSocketApp(
                self.ws_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close
            )
            self.ws_thread = threading.Thread(target=self.ws.run_forever)
            self.ws_thread.daemon = True
            self.ws_thread.start()
            
            # Warte bis Verbindung hergestellt ist
            timeout = 5
            start_time = time.time()
            while not self.ws.sock or not self.ws.sock.connected:
                if time.time() - start_time > timeout:
                    raise TimeoutError("Timeout beim Verbindungsaufbau")
                time.sleep(0.1)
            
            self.connected = True
            self.show_status()
                
        except Exception as e:
            self.logger.error(f"⚠️ Fehler beim Verbindungsaufbau: {e}")
            self.connected = False
            self.show_status()
            self.cleanup()
            sys.exit(1)

    def on_open(self, ws):
        """Callback wenn WebSocket-Verbindung geöffnet wird"""
        self.logger.info("✓ Verbindung zum Server hergestellt")
        # Konfiguration an Server senden
        try:
            config = {
                "uid": self.uid,
                "language": "de",
                "task": "transcribe",
                "use_vad": True,
                "backend": "faster_whisper"
            }
            json_str = json.dumps(config)
            self.logger.debug(f"Sende Konfiguration: {json.dumps(config, indent=2)}")
            ws.send(json_str)
        except Exception as e:
            self.logger.error(f"⚠️ Fehler beim Senden der Konfiguration: {e}")

    def on_message(self, ws, message):
        """Callback für eingehende Server-Nachrichten"""
        try:
            data = json.loads(message)
            
            if "status" in data:
                if data["status"] == "ERROR":
                    self.logger.error(f"⚠️ Server-Fehler: {data.get('message', 'Unbekannter Fehler')}")
                return
            
            if "message" in data and data["message"] == "SERVER_READY":
                self.logger.info("✓ Server bereit")
                return
                
            if "segments" in data:
                for segment in data["segments"]:
                    text = segment.get("text", "").strip()
                    if text and text != self.last_transcription:
                        self.insert_text(text)
                        self.last_transcription = text
        except json.JSONDecodeError as e:
            self.logger.error(f"⚠️ Fehler beim Dekodieren der Nachricht: {e}")
        except Exception as e:
            self.logger.error(f"⚠️ Unerwarteter Fehler bei Nachrichtenverarbeitung: {e}")

    def on_error(self, ws, error):
        """Callback für WebSocket-Fehler"""
        self.logger.error(f"⚠️ Verbindungsfehler: {error}")
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            self.logger.info("Verbindung verloren. Versuche Neuverbindung in 3 Sekunden...")
            time.sleep(3)
            try:
                self.connect()
                self.logger.info("✓ Neuverbindung erfolgreich")
            except:
                self.logger.error("⚠️ Neuverbindung fehlgeschlagen")
                self.cleanup()
                sys.exit(1)

    def on_close(self, ws, close_status_code, close_msg):
        """Callback wenn WebSocket-Verbindung geschlossen wird"""
        self.logger.warning(f"✗ Verbindung geschlossen (Status: {close_status_code}, Nachricht: {close_msg})")
        self.recording = False
        self.connected = False
        self.show_status()
        
        # Beende die Verbindung bei Status 1000 (normal closure)
        if close_status_code == 1000:
            self.logger.info("Server hat die Verbindung normal beendet")
            self.ws = None
            sys.exit(0)  # Beende das Programm

    def show_status(self):
        """Zeigt den aktuellen Status an"""
        connection_status = "✓" if self.connected else "✗"
        recording_status = "🎤" if self.recording else "⏹️"
        self.logger.info(f"\rStatus: {connection_status} Verbindung | {recording_status} Aufnahme", extra={'end': ''})
        
    def start_recording(self):
        """Startet die Audio-Aufnahme"""
        with self.recording_lock:
            if self.recording:
                return
                
            if not self.connected:
                self.logger.error("⚠️ Keine Verbindung zum Server")
                return
                
            try:
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    frames_per_buffer=self.chunk
                )
                self.recording = True
                self.logger.info("🎤 Aufnahme gestartet...")
                self.show_status()
                
                # Aufnahme-Thread starten
                self.record_thread = threading.Thread(target=self.record_audio)
                self.record_thread.daemon = True
                self.record_thread.start()
                
            except Exception as e:
                self.logger.error(f"⚠️ Fehler beim Starten der Aufnahme: {e}")
                self.recording = False
                self.show_status()

    def stop_recording(self):
        """Stoppt die Audio-Aufnahme"""
        with self.recording_lock:
            if not self.recording:
                return
                
            self.recording = False
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            self.logger.info("⏹️ Aufnahme gestoppt")
            self.show_status()

    def record_audio(self):
        """Audio aufnehmen und an Server senden"""
        while self.recording:
            try:
                data = self.stream.read(self.chunk, exception_on_overflow=False)
                # Konvertiere zu float32 Array
                audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                
                # Sende Audio-Daten an Server
                if self.ws and self.ws.sock and self.ws.sock.connected:
                    try:
                        self.ws.send(audio_array.tobytes(), websocket.ABNF.OPCODE_BINARY)
                    except websocket.WebSocketConnectionClosedException:
                        self.logger.error("⚠️ Verbindung während der Aufnahme verloren")
                        self.stop_recording()
                        break
                else:
                    self.logger.error("⚠️ Keine aktive Verbindung zum Server")
                    self.stop_recording()
                    break
                    
            except Exception as e:
                self.logger.error(f"⚠️ Fehler bei der Aufnahme: {e}")
                self.stop_recording()
                break

    def toggle_recording(self):
        """Aufnahme starten/stoppen"""
        if not self.recording:
            self.start_recording()
        else:
            self.stop_recording()

    def insert_text(self, text):
        """Text in die Zwischenablage kopieren"""
        try:
            pyperclip.copy(text)
            self.logger.info(f"📋 Text in Zwischenablage kopiert: {text}")
            self.logger.info("⌨️  Drücke Strg+V zum Einfügen")
        except Exception as e:
            self.logger.error(f"⚠️ Fehler beim Kopieren in die Zwischenablage: {e}")
            
    def cleanup(self):
        """Ressourcen freigeben"""
        self.stop_recording()
        if self.ws:
            self.ws.close()
        if self.audio:
            self.audio.terminate()

def main():
    # Disable websocket trace
    websocket.enableTrace(False)
    
    try:
        client = WhisperClient()
        client.connect()
        
        # Hotkey registrieren
        keyboard.add_hotkey('alt+space', client.toggle_recording)
        
        client.logger.info("\n=== Whisper Client ===")
        client.logger.info("🔥 Client gestartet!")
        client.logger.info("⌨️  Drücke Alt+Space zum Starten/Stoppen der Aufnahme")
        client.logger.info("⚡ Drücke Strg+C zum Beenden")
        client.logger.info("-" * 50)
        client.show_status()
        
        try:
            while True:
                time.sleep(0.1)
        except KeyboardInterrupt:
            client.logger.info("\n🛑 Programm wird beendet...")
            client.cleanup()
            keyboard.unhook_all()
            sys.exit(0)
            
    except Exception as e:
        print(f"\n⚠️ Kritischer Fehler: {e}")
        print("🛑 Programm wird beendet...")
        sys.exit(1)

if __name__ == "__main__":
    main()
