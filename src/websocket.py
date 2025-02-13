"""
WebSocket-Kommunikationsmodul für den Whisper-Client
"""
import json
import threading
import time
import uuid
import websocket
import win32clipboard
import config
from src import logger
from src.logging import log_connection, log_audio, log_text, log_error

class WhisperWebSocket:
    def __init__(self):
        self.uid = str(uuid.uuid4())
        self.ws = None
        self.ws_thread = None
        self.connected = False
        self.server_ready = False  # Flag für Server-Bereitschaft
        self.on_text_callback = None
        self.processing_enabled = True  # Flag für Verarbeitung von Server-Nachrichten
        self.last_segments = []  # Speichert den letzten Stand der Segmente
    
    def connect(self, max_retries=3):
        """WebSocket-Verbindung aufbauen"""
        if self.connected and self.ws and self.ws.sock and self.ws.sock.connected:
            log_connection(logger, "Already connected")
            return True
            
        retry_count = 0
        retry_delay = 2  # Sekunden zwischen Versuchen
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    log_connection(logger, f"Connection attempt {retry_count + 1} of {max_retries}")
                
                # Alte Verbindung sauber beenden
                if self.ws:
                    try:
                        self.cleanup()
                    except:
                        pass
                    self.ws = None
                    self.ws_thread = None
                
                log_connection(logger, f"Connecting to server: {config.WS_URL}")
                self.ws = websocket.WebSocketApp(
                    config.WS_URL,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                self.ws_thread = threading.Thread(target=self.ws.run_forever)
                self.ws_thread.daemon = True
                self.ws_thread.start()
                
                # Warte bis Verbindung hergestellt ist
                timeout = 5
                start_time = time.time()
                while not self.ws.sock or not self.ws.sock.connected:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Connection timeout")
                    time.sleep(0.1)
                
                self.connected = True
                self.processing_enabled = True
                
                # Warte auf Server-Ready Signal
                log_connection(logger, "Waiting for server ready signal...")
                timeout = 10
                start_time = time.time()
                while not self.server_ready:
                    if time.time() - start_time > timeout:
                        raise TimeoutError("Server ready timeout")
                    time.sleep(0.1)
                
                return True
                    
            except Exception as e:
                retry_count += 1
                self.connected = False
                self.server_ready = False
                
                if retry_count < max_retries:
                    if isinstance(e, ConnectionRefusedError):
                        log_error(logger, "Server not reachable. Is WhisperLive server running?")
                    elif isinstance(e, TimeoutError):
                        log_error(logger, f"Connection timeout: {str(e)}")
                    else:
                        log_error(logger, f"Connection error: {str(e)}")
                    
                    log_connection(logger, f"Waiting {retry_delay} seconds before retry...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponentielles Backoff
                else:
                    log_error(logger, "Maximum retry attempts reached")
                    raise
        
        return False
    
    def _on_open(self, ws):
        """Callback wenn WebSocket-Verbindung geöffnet wird"""
        log_connection(logger, "Connected to server")
        # Konfiguration an Server senden
        try:
            ws_config = {
                "uid": self.uid,
                "language": config.WHISPER_LANGUAGE,
                "task": config.WHISPER_TASK,
                "use_vad": config.WHISPER_USE_VAD,
                "backend": config.WHISPER_BACKEND
            }
            json_str = json.dumps(ws_config).encode('utf-8')
            log_connection(logger, f"Sending config: {json.dumps(ws_config, indent=2)}")
            ws.send(json_str, websocket.ABNF.OPCODE_TEXT)
        except Exception as e:
            log_error(logger, f"Error sending config: {str(e)}")
    
    def _on_message(self, ws, message):
        """Callback für eingehende Server-Nachrichten"""
        if not self.processing_enabled:
            return  # Ignoriere Nachrichten wenn Verarbeitung deaktiviert
            
        try:
            # Konvertiere bytes zu string wenn nötig
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            
            # Logge rohe Server-Nachricht
            log_connection(logger, f"Raw server message: {message}")
            
            data = json.loads(message)
            
            if "status" in data:
                if data["status"] == "ERROR":
                    log_error(logger, f"Server error: {data.get('message', 'Unknown error')}")
                return
            
            if "message" in data and data["message"] == "SERVER_READY":
                self.server_ready = True
                log_connection(logger, "Server ready")
                return
                
            if "segments" in data:
                new_segments = data["segments"]
                # Logge detaillierte Segment-Informationen
                for segment in new_segments:
                    text = segment.get('text', '').strip()
                    try:
                        start = float(segment.get('start', '0'))
                        end = float(segment.get('end', '0'))
                        log_text(logger, f"Segment [{start:.2f}s - {end:.2f}s]: {text}")
                    except (ValueError, TypeError):
                        log_text(logger, f"Segment: {text}")
                
                # Prüfe ob sich die Segmente geändert haben
                if self._segments_changed(new_segments):
                    # Log neue/geänderte Segmente
                    for segment in new_segments:
                        if segment not in self.last_segments:
                            text = segment.get('text', '').strip()
                            log_text(logger, text)
                    
                    # Aktualisiere letzten Stand und rufe Callback auf
                    self.last_segments = new_segments
                    if self.on_text_callback:
                        self.on_text_callback(new_segments)
                    
        except json.JSONDecodeError as e:
            log_error(logger, f"Error decoding message: {str(e)}")
        except Exception as e:
            log_error(logger, f"Unexpected error processing message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Callback für WebSocket-Fehler"""
        log_error(logger, f"Connection error: {str(error)}")
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            log_connection(logger, "Connection lost. Attempting reconnect in 3 seconds...")
            time.sleep(3)
            try:
                self.connect()
                log_connection(logger, "Reconnection successful")
            except:
                log_error(logger, "Reconnection failed")
                raise
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback wenn WebSocket-Verbindung geschlossen wird"""
        log_connection(logger, f"Connection closed (Status: {close_status_code}, Message: {close_msg})")
        
        # Nur wenn wir nicht auf letzte Segmente warten
        if not self.processing_enabled:
            self.connected = False
            self.server_ready = False
            
            # Beende die Verbindung bei Status 1000 (normal closure)
            if close_status_code == 1000:
                log_connection(logger, "Server closed connection normally")
                self.ws = None
    
    def is_ready(self):
        """Prüft ob der Server bereit ist"""
        return self.connected and self.server_ready
    
    def send_audio(self, audio_data):
        """Sendet Audio-Daten an den Server"""
        if not self.processing_enabled:
            return False
            
        if not self.connected or not self.ws or not self.ws.sock:
            log_error(logger, "No active server connection")
            return False
            
        if not self.server_ready:
            log_error(logger, "Server not ready")
            return False
            
        try:
            if not self.ws.sock.connected:
                log_error(logger, "Socket not connected")
                self.connected = False
                return False
                
            self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            log_audio(logger, f"Sent {len(audio_data)} bytes")
            return True
        except websocket.WebSocketConnectionClosedException:
            log_error(logger, "Connection lost while sending audio")
            self.connected = False
            return False
        except Exception as e:
            log_error(logger, f"Error sending audio: {str(e)}")
            self.connected = False
            return False
    
    def set_text_callback(self, callback):
        """Setzt den Callback für empfangene Textsegmente"""
        self.on_text_callback = callback
    
    def _segments_changed(self, new_segments):
        """Prüft ob sich die Segmente geändert haben"""
        if not new_segments:
            return False
            
        # Vergleiche nur den Text des letzten Segments
        if not self.last_segments:
            return True
            
        last_new = new_segments[-1].get('text', '').strip()
        last_old = self.last_segments[-1].get('text', '').strip()
        
        return last_new != last_old
    
    def stop_processing(self):
        """Stoppt die Verarbeitung von Server-Nachrichten"""
        if self.processing_enabled:
            try:
                # Sende END_OF_AUDIO
                self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
                log_audio(logger, "Sent END_OF_AUDIO signal")
                
                # Starte Thread für Wartezeit
                def wait_for_segments():
                    try:
                        # Warte auf letzte Segmente
                        log_connection(logger, "Waiting for final segments (20s)...")
                        time.sleep(20.0)
                    finally:
                        # Stoppe die Verarbeitung nach der Wartezeit
                        self.processing_enabled = False
                        self.last_segments = []  # Reset gespeicherte Segmente
                        log_connection(logger, "Server message processing disabled")
                
                # Starte Warte-Thread
                wait_thread = threading.Thread(target=wait_for_segments)
                wait_thread.daemon = True
                wait_thread.start()
                
            except Exception as e:
                log_error(logger, f"Error sending END_OF_AUDIO: {str(e)}")
                self.processing_enabled = False
    
    def start_processing(self):
        """Startet die Verarbeitung von Server-Nachrichten"""
        if not self.is_ready():
            log_error(logger, "Server not ready for processing")
            return False
            
        self.processing_enabled = True
        self.last_segments = []  # Reset gespeicherte Segmente
        
        # Leere die Zwischenablage
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            log_connection(logger, "Clipboard cleared")
        except Exception as e:
            log_error(logger, f"Error clearing clipboard: {str(e)}")
            
        log_connection(logger, "Server message processing enabled")
        return True
    
    def cleanup(self):
        """Ressourcen freigeben"""
        if not self.ws:
            return
            
        try:
            log_connection(logger, "Starting cleanup...")
            
            # Stoppe zuerst die Verarbeitung
            log_connection(logger, "Stopping processing...")
            self.processing_enabled = False
            
            # Speichere Referenz für Thread-Join
            thread = self.ws_thread
            
            # Schließe WebSocket mit Close-Frame
            log_connection(logger, "Closing connection...")
            try:
                self.ws.close(1000, "Client shutdown".encode('utf-8'))
            except Exception as e:
                log_error(logger, f"Error closing connection: {str(e)}")
                
            self.ws = None
            self.connected = False
            self.server_ready = False
            
            # Warte auf Thread-Ende
            if thread and thread.is_alive():
                thread.join(timeout=5.0)
                if thread.is_alive():
                    log_error(logger, "Thread could not be terminated")
                else:
                    log_connection(logger, "Thread terminated")
                
        except Exception as e:
            log_error(logger, f"Error during cleanup: {str(e)}")
            # Setze Status zurück
            self.ws = None
            self.connected = False
            self.server_ready = False
