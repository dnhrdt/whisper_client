"""
WebSocket Communication Module for the Whisper Client (Simplified Version)
Version: 1.0
Timestamp: 2025-02-27 17:12 CET

This module handles WebSocket communication with the WhisperLive server.
It provides functionality for establishing connections, sending audio data,
receiving transcription results, and managing the connection lifecycle.
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
        self.server_ready = False
        self.on_text_callback = None
        self.processing_enabled = True
        self.current_text = ""  # Stores the current text
    
    def connect(self, max_retries=3):
        """Establish WebSocket connection"""
        if self.connected and self.ws and self.ws.sock and self.ws.sock.connected:
            log_connection(logger, "Already connected")
            return True
            
        retry_count = 0
        retry_delay = config.WS_RETRY_DELAY
        
        while retry_count < max_retries:
            try:
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
                
                start_time = time.time()
                while not self.ws.sock or not self.ws.sock.connected:
                    if time.time() - start_time > config.WS_CONNECT_TIMEOUT:
                        raise TimeoutError("Connection timeout")
                    time.sleep(config.WS_POLL_INTERVAL)
                
                self.connected = True
                self.processing_enabled = True
                
                log_connection(logger, "Waiting for server ready signal...")
                start_time = time.time()
                while not self.server_ready:
                    if time.time() - start_time > config.WS_READY_TIMEOUT:
                        raise TimeoutError("Server ready timeout")
                    time.sleep(config.WS_POLL_INTERVAL)
                
                return True
                    
            except Exception as e:
                retry_count += 1
                self.connected = False
                self.server_ready = False
                
                if retry_count < max_retries:
                    log_error(logger, f"Connection error: {str(e)}")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, 30.0)
                else:
                    log_error(logger, "Maximum retry attempts reached")
                    raise
        
        return False
    
    def _on_open(self, ws):
        """Callback when WebSocket connection is opened"""
        log_connection(logger, "Connected to server")
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
        """Callback for incoming server messages"""
        if not self.processing_enabled:
            return
            
        try:
            if isinstance(message, bytes):
                message = message.decode('utf-8')
            
            log_connection(logger, f"Raw server message: {message}")
            data = json.loads(message)
            
            if "message" in data:
                if data["message"] == "SERVER_READY":
                    self.server_ready = True
                    log_connection(logger, "Server ready")
                    return
            
            if "segments" in data:
                segments = data["segments"]
                if segments:
                    # Take only the last complete text
                    text = segments[-1].get('text', '').strip()
                    if text != self.current_text:
                        self.current_text = text
                        log_text(logger, text)
                        if self.on_text_callback:
                            self.on_text_callback([segments[-1]])
                    
        except Exception as e:
            log_error(logger, f"Error processing message: {str(e)}")
    
    def _on_error(self, ws, error):
        """Callback for WebSocket errors"""
        log_error(logger, f"Connection error: {str(error)}")
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when WebSocket connection is closed"""
        log_connection(logger, f"Connection closed (Status: {close_status_code}, Message: {close_msg})")
        self.connected = False
        self.server_ready = False
    
    def is_ready(self):
        """Checks if the server is ready"""
        return self.connected and self.server_ready
    
    def send_audio(self, audio_data):
        """Sends audio data to the server"""
        if not self.processing_enabled or not self.is_ready():
            return False
            
        try:
            self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            log_audio(logger, f"Sent {len(audio_data)} bytes")
            return True
        except Exception as e:
            log_error(logger, f"Error sending audio: {str(e)}")
            self.connected = False
            return False
    
    def set_text_callback(self, callback):
        """Sets the callback for received text segments"""
        self.on_text_callback = callback
    
    def send_end_of_audio(self):
        """Sends END_OF_AUDIO signal to the server"""
        if not self.is_ready():
            return False
            
        try:
            self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
            log_audio(logger, "Sent END_OF_AUDIO signal")
            log_connection(logger, f"Waiting for final segments ({config.WS_FINAL_WAIT}s)...")
            time.sleep(config.WS_FINAL_WAIT)
            return True
        except Exception as e:
            log_error(logger, f"Error sending END_OF_AUDIO: {str(e)}")
            return False
    
    def stop_processing(self):
        """Stops processing server messages"""
        if self.processing_enabled:
            try:
                if self.is_ready():
                    # Send END_OF_AUDIO and wait for processing
                    self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
                    log_audio(logger, "Sent END_OF_AUDIO signal")
                    
                    # Wait for final segments
                    wait_start = time.time()
                    last_message_time = wait_start
                    
                    while True:
                        # Check timeout
                        current_time = time.time()
                        if current_time - wait_start > config.WS_FINAL_WAIT:
                            log_connection(logger, "Final wait timeout reached")
                            break
                            
                        # Check inactivity
                        if current_time - last_message_time > config.WS_MESSAGE_WAIT:
                            log_connection(logger, "No new messages, stopping")
                            break
                            
                        # Short pause
                        time.sleep(config.WS_POLL_INTERVAL)
                    
                    # Disable processing
                    self.processing_enabled = False
                    self.current_text = ""
                    
                    # Close connection cleanly
                    log_connection(logger, "Closing connection...")
                    self.ws.close()
                    
                    # Wait for thread to end
                    if self.ws_thread and self.ws_thread.is_alive():
                        self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
                
            except Exception as e:
                log_error(logger, f"Error stopping processing: {str(e)}")
            finally:
                self.processing_enabled = False
                self.connected = False
                self.server_ready = False
    
    def start_processing(self):
        """Starts processing server messages"""
        if not self.is_ready():
            log_error(logger, "Server not ready for processing")
            return False
            
        self.processing_enabled = True
        self.current_text = ""
        
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.CloseClipboard()
            log_connection(logger, "Clipboard cleared")
        except Exception as e:
            log_error(logger, f"Could not clear clipboard: {str(e)}")
        
        log_connection(logger, "Server message processing enabled")
        return True
    
    def cleanup(self):
        """Release resources"""
        if not self.ws:
            return
            
        try:
            log_connection(logger, "Starting cleanup...")
            self.processing_enabled = False
            if self.ws and self.ws.sock:
                self.ws.close()
            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
        except Exception as e:
            log_error(logger, f"Error during cleanup: {str(e)}")
        finally:
            self.ws = None
            self.connected = False
            self.server_ready = False
