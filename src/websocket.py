"""
WebSocket Communication Module for the Whisper Client (Simplified Version)
Version: 1.2
Timestamp: 2025-03-01 21:40 CET

This module handles WebSocket communication with the WhisperLive server.
It provides functionality for establishing connections, sending audio data,
receiving transcription results, and managing the connection lifecycle.
"""
import json
import threading
import time
import uuid
import websocket
import enum
import win32clipboard
import config
from src import logger
from src.logging import log_connection, log_audio, log_text, log_error

class ConnectionState(enum.Enum):
    """Enum for WebSocket connection states"""
    DISCONNECTED = 0
    CONNECTING = 1
    CONNECTED = 2
    READY = 3
    PROCESSING = 4
    FINALIZING = 5
    CLOSING = 6
    CLOSED = 7
    CONNECT_ERROR = 8
    PROCESSING_ERROR = 9
    TIMEOUT_ERROR = 10

class WhisperWebSocket:
    # Class-level variable to track active instances
    _active_instances = {}
    _instances_lock = threading.Lock()
    
    def __init__(self):
        # Generate a persistent client ID that remains the same across reconnections
        self.client_id = str(uuid.uuid4())
        # Session ID changes with each new connection attempt
        self.session_id = str(uuid.uuid4())
        self.ws = None
        self.ws_thread = None
        self.state = ConnectionState.DISCONNECTED
        self.server_ready = False
        self.on_text_callback = None
        self.processing_enabled = True
        self.current_text = ""  # Stores the current text
        self.connection_lock = threading.Lock()  # Lock for thread-safe state changes
        self.last_connection_attempt = 0  # Timestamp of last connection attempt
        
        # Register this instance
        with WhisperWebSocket._instances_lock:
            WhisperWebSocket._active_instances[self.client_id] = self
        
        log_connection(logger, f"Created WebSocket client with ID: {self.client_id}")
    
    def _set_state(self, new_state):
        """Sets the connection state and logs the transition"""
        with self.connection_lock:
            old_state = self.state
            self.state = new_state
            log_connection(logger, f"State changed: {old_state.name} -> {new_state.name}")
    
    @classmethod
    def get_instance_count(cls):
        """Returns the number of active WebSocket instances"""
        with cls._instances_lock:
            return len(cls._active_instances)
    
    @classmethod
    def cleanup_all_instances(cls):
        """Cleanup all active WebSocket instances"""
        with cls._instances_lock:
            instances = list(cls._active_instances.values())
        
        for instance in instances:
            try:
                instance.cleanup()
            except Exception as e:
                log_error(logger, f"Error cleaning up instance {instance.client_id}: {str(e)}")
    
    def __del__(self):
        """Remove this instance when garbage collected"""
        try:
            with WhisperWebSocket._instances_lock:
                if self.client_id in WhisperWebSocket._active_instances:
                    del WhisperWebSocket._active_instances[self.client_id]
        except:
            pass  # Ignore errors during shutdown
    
    def connect(self, max_retries=3):
        """Establish WebSocket connection"""
        # Check if already connected
        if self.state in [ConnectionState.CONNECTED, ConnectionState.READY, ConnectionState.PROCESSING] and self.ws and self.ws.sock and self.ws.sock.connected:
            log_connection(logger, "Already connected")
            return True
        
        # Check for connection throttling
        current_time = time.time()
        if current_time - self.last_connection_attempt < config.WS_RECONNECT_DELAY:
            wait_time = config.WS_RECONNECT_DELAY - (current_time - self.last_connection_attempt)
            log_connection(logger, f"Connection attempt throttled, waiting {wait_time:.2f}s")
            time.sleep(wait_time)
        
        # Update connection attempt timestamp
        self.last_connection_attempt = time.time()
        
        # Generate new session ID for this connection attempt
        self.session_id = str(uuid.uuid4())
        log_connection(logger, f"Starting connection attempt with session ID: {self.session_id}")
        
        retry_count = 0
        retry_delay = config.WS_RETRY_DELAY
        
        while retry_count < max_retries:
            try:
                # Ensure proper cleanup before reconnection
                if self.ws:
                    try:
                        self.cleanup()
                    except Exception as e:
                        log_error(logger, f"Error during cleanup before reconnection: {str(e)}")
                    self.ws = None
                    self.ws_thread = None
                
                self._set_state(ConnectionState.CONNECTING)
                log_connection(logger, f"Connecting to server: {config.WS_URL} (Client: {self.client_id}, Session: {self.session_id})")
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
                
                self._set_state(ConnectionState.CONNECTED)
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
                self._set_state(ConnectionState.CONNECT_ERROR)
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
        self._set_state(ConnectionState.CONNECTED)
        try:
            ws_config = {
                "uid": self.client_id,
                "session_id": self.session_id,
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
            self._set_state(ConnectionState.CONNECT_ERROR)
    
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
                    self._set_state(ConnectionState.READY)
                    return
                elif data["message"] == "END_OF_AUDIO_RECEIVED":
                    # Server acknowledges END_OF_AUDIO signal
                    self._set_state(ConnectionState.FINALIZING)
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
            self._set_state(ConnectionState.PROCESSING_ERROR)
    
    def _on_error(self, ws, error):
        """Callback for WebSocket errors"""
        log_error(logger, f"Connection error: {str(error)}")
        self._set_state(ConnectionState.CONNECT_ERROR)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when WebSocket connection is closed"""
        log_connection(logger, f"Connection closed (Status: {close_status_code}, Message: {close_msg})")
        self._set_state(ConnectionState.CLOSED)
        self.server_ready = False
    
    def is_ready(self):
        """Checks if the server is ready"""
        return self.state == ConnectionState.READY
    
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
            self._set_state(ConnectionState.CONNECT_ERROR)
            return False
    
    def set_text_callback(self, callback):
        """Sets the callback for received text segments"""
        self.on_text_callback = callback
    
    def send_end_of_audio(self):
        """Sends END_OF_AUDIO signal to the server"""
        if not self.is_ready() and self.state != ConnectionState.PROCESSING:
            return False
            
        try:
            self._set_state(ConnectionState.FINALIZING)
            self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
            log_audio(logger, "Sent END_OF_AUDIO signal")
            log_connection(logger, f"Waiting for final segments ({config.WS_FINAL_WAIT}s)...")
            
            # Wait for server to acknowledge END_OF_AUDIO
            wait_start = time.time()
            while self.state == ConnectionState.FINALIZING:
                if time.time() - wait_start > config.WS_FINAL_WAIT:
                    log_connection(logger, "Final wait timeout reached")
                    break
                time.sleep(config.WS_POLL_INTERVAL)
                
            return True
        except Exception as e:
            log_error(logger, f"Error sending END_OF_AUDIO: {str(e)}")
            return False
    
    def stop_processing(self):
        """Stops processing server messages"""
        if self.processing_enabled:
            try:
                if self.is_ready() or self.state == ConnectionState.PROCESSING:
                    # Send END_OF_AUDIO and wait for processing
                    self._set_state(ConnectionState.FINALIZING)
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
                    self._set_state(ConnectionState.CLOSING)
                    log_connection(logger, "Closing connection...")
                    self.ws.close()
                    
                    # Wait for thread to end
                    if self.ws_thread and self.ws_thread.is_alive():
                        self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
                
            except Exception as e:
                log_error(logger, f"Error stopping processing: {str(e)}")
            finally:
                self.processing_enabled = False
                self._set_state(ConnectionState.CLOSED)
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
        
        self._set_state(ConnectionState.PROCESSING)
        log_connection(logger, "Server message processing enabled")
        return True
    
    def cleanup(self):
        """Release resources"""
        if not self.ws:
            return
            
        try:
            log_connection(logger, f"Starting cleanup for session {self.session_id}...")
            self.processing_enabled = False
            if self.ws and self.ws.sock:
                self._set_state(ConnectionState.CLOSING)
                self.ws.close()
            if self.ws_thread and self.ws_thread.is_alive():
                self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
        except Exception as e:
            log_error(logger, f"Error during cleanup: {str(e)}")
        finally:
            self.ws = None
            self._set_state(ConnectionState.DISCONNECTED)
            self.server_ready = False
            log_connection(logger, f"Cleanup completed for session {self.session_id}")
