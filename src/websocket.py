"""
WebSocket-Kommunikationsmodul für den Whisper-Client
"""
import json
import threading
import time
import uuid
import websocket
import config
from src import logging

logger = logging.get_logger()

class WhisperWebSocket:
    def __init__(self):
        self.uid = str(uuid.uuid4())
        self.ws = None
        self.ws_thread = None
        self.connected = False
        self.on_text_callback = None
    
    def connect(self, max_retries=3):
        """WebSocket-Verbindung aufbauen"""
        retry_count = 0
        retry_delay = 2  # Sekunden zwischen Versuchen
        
        while retry_count < max_retries:
            try:
                if retry_count > 0:
                    logger.info(f"Verbindungsversuch {retry_count + 1} von {max_retries}...")
                
                if self.ws:
                    self.ws.close()
                    self.ws = None
                
                logger.info(f"Verbinde mit Server: {config.WS_URL}")
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
                        raise TimeoutError("Timeout beim Verbindungsaufbau")
                    time.sleep(0.1)
                
                self.connected = True
                return True
                    
            except Exception as e:
                retry_count += 1
                self.connected = False
                
                if retry_count < max_retries:
                    if isinstance(e, ConnectionRefusedError):
                        logger.warning("⚠️ Server nicht erreichbar. Läuft der WhisperLive Server?")
                    elif isinstance(e, TimeoutError):
                        logger.warning("⚠️ Zeitüberschreitung beim Verbindungsaufbau")
                    else:
                        logger.warning(f"⚠️ Verbindungsfehler: {e}")
                    
                    logger.info(f"Warte {retry_delay} Sekunden vor erneutem Versuch...")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponentielles Backoff
                else:
                    logger.error("❌ Maximale Anzahl an Verbindungsversuchen erreicht")
                    raise
        
        return False
    
    def _on_open(self, ws):
        """Callback wenn WebSocket-Verbindung geöffnet wird"""
        logger.info("✓ Verbindung zum Server hergestellt")
        # Konfiguration an Server senden
        try:
            ws_config = {
                "uid": self.uid,
                "language": config.WHISPER_LANGUAGE,
                "task": config.WHISPER_TASK,
                "use_vad": config.WHISPER_USE_VAD,
                "backend": config.WHISPER_BACKEND
            }
            json_str = json.dumps(ws_config)
            logger.debug(f"Sende Konfiguration: {json.dumps(ws_config, indent=2)}")
            ws.send(json_str)
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Senden der Konfiguration: {e}")
    
    def _on_message(self, ws, message):
        """Callback für eingehende Server-Nachrichten"""
        try:
            data = json.loads(message)
            
            if "status" in data:
                if data["status"] == "ERROR":
                    logger.error(f"⚠️ Server-Fehler: {data.get('message', 'Unbekannter Fehler')}")
                return
            
            if "message" in data and data["message"] == "SERVER_READY":
                logger.info("✓ Server bereit")
                return
                
            if "segments" in data:
                # Debug: Zeige vollständige Segment-Struktur
                logger.debug("\n🔍 Server-Ausgabe:")
                for segment in data['segments']:
                    logger.debug(f"  → {segment.get('text', '').strip()}")
                
                # Callback für Textverarbeitung aufrufen
                if self.on_text_callback:
                    self.on_text_callback(data["segments"])
                    
        except json.JSONDecodeError as e:
            logger.error(f"⚠️ Fehler beim Dekodieren der Nachricht: {e}")
        except Exception as e:
            logger.error(f"⚠️ Unerwarteter Fehler bei Nachrichtenverarbeitung: {e}")
    
    def _on_error(self, ws, error):
        """Callback für WebSocket-Fehler"""
        logger.error(f"⚠️ Verbindungsfehler: {error}")
        if isinstance(error, websocket.WebSocketConnectionClosedException):
            logger.info("Verbindung verloren. Versuche Neuverbindung in 3 Sekunden...")
            time.sleep(3)
            try:
                self.connect()
                logger.info("✓ Neuverbindung erfolgreich")
            except:
                logger.error("⚠️ Neuverbindung fehlgeschlagen")
                raise
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback wenn WebSocket-Verbindung geschlossen wird"""
        logger.warning(f"✗ Verbindung geschlossen (Status: {close_status_code}, Nachricht: {close_msg})")
        self.connected = False
        
        # Beende die Verbindung bei Status 1000 (normal closure)
        if close_status_code == 1000:
            logger.info("Server hat die Verbindung normal beendet")
            self.ws = None
    
    def send_audio(self, audio_data):
        """Sendet Audio-Daten an den Server"""
        if not self.connected:
            logger.error("⚠️ Keine Verbindung zum Server")
            return False
        
        try:
            self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            return True
        except websocket.WebSocketConnectionClosedException:
            logger.error("⚠️ Verbindung während der Übertragung verloren")
            return False
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Senden der Audio-Daten: {e}")
            return False
    
    def set_text_callback(self, callback):
        """Setzt den Callback für empfangene Textsegmente"""
        self.on_text_callback = callback
    
    def cleanup(self):
        """Ressourcen freigeben"""
        if self.ws:
            self.ws.close()
