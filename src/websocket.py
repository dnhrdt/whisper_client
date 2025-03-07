"""
WebSocket Communication Module for the Whisper Client (Simplified Version)
Version: 1.3
Timestamp: 2025-03-07 23:08 CET

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
        self.last_state_log_time = 0  # Timestamp of last state logging
        self.state_log_interval = 5.0  # Log state every 5 seconds during long operations
        
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
    
    def _log_state_periodically(self, operation_name):
        """Log state periodically during long-running operations"""
        current_time = time.time()
        if current_time - self.last_state_log_time >= self.state_log_interval:
            self.last_state_log_time = current_time
            log_connection(logger, f"[{operation_name}] Current state: {self.state.name}, "
                          f"Active instances: {self.get_instance_count()}")
    
    @classmethod
    def get_instance_count(cls):
        """Returns the number of active WebSocket instances"""
        with cls._instances_lock:
            return len(cls._active_instances)
    
    @classmethod
    def cleanup_all_instances(cls):
        """Cleanup all active WebSocket instances with proper timeout handling"""
        cleanup_start = time.time()
        log_connection(logger, f"Starting cleanup of all WebSocket instances ({cls.get_instance_count()} active)...")
        
        with cls._instances_lock:
            instances = list(cls._active_instances.values())
        
        success_count = 0
        error_count = 0
        
        for instance in instances:
            try:
                instance.cleanup()
                success_count += 1
            except Exception as e:
                error_count += 1
                log_error(logger, f"Error cleaning up instance {instance.client_id}: {str(e)}")
        
        # Check if cleanup took too long
        cleanup_duration = time.time() - cleanup_start
        if cleanup_duration > config.WS_CLEANUP_TIMEOUT:
            log_error(logger, f"Cleanup of all instances took longer than expected: {cleanup_duration:.2f}s")
        
        # Final cleanup status
        log_connection(logger, f"Cleanup completed: {success_count} successful, {error_count} failed, "
                      f"duration: {cleanup_duration:.2f}s")
        
        # Check if any instances remain
        remaining = cls.get_instance_count()
        if remaining > 0:
            log_error(logger, f"Warning: {remaining} WebSocket instances still active after cleanup")
    
    def __del__(self):
        """Remove this instance when garbage collected"""
        try:
            with WhisperWebSocket._instances_lock:
                if self.client_id in WhisperWebSocket._active_instances:
                    del WhisperWebSocket._active_instances[self.client_id]
        except:
            pass  # Ignore errors during shutdown
    
    def connect(self, max_retries=3):
        """Establish WebSocket connection with enhanced timeout handling"""
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
        connect_start_time = self.last_connection_attempt
        
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
                        log_connection(logger, "Cleaning up previous connection before reconnect...")
                        self.cleanup()
                    except Exception as e:
                        log_error(logger, f"Error during cleanup before reconnection: {str(e)}")
                    self.ws = None
                    self.ws_thread = None
                
                self._set_state(ConnectionState.CONNECTING)
                log_connection(logger, f"Connecting to server: {config.WS_URL} (Client: {self.client_id}, Session: {self.session_id})")
                
                # Create WebSocket with timeout
                self.ws = websocket.WebSocketApp(
                    config.WS_URL,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                
                # Start WebSocket thread
                self.ws_thread = threading.Thread(target=self.ws.run_forever)
                self.ws_thread.daemon = True
                self.ws_thread.start()
                
                # Wait for connection with timeout
                start_time = time.time()
                while not self.ws.sock or not self.ws.sock.connected:
                    if time.time() - start_time > config.WS_CONNECT_TIMEOUT:
                        self._set_state(ConnectionState.TIMEOUT_ERROR)
                        raise TimeoutError(f"Connection timeout after {config.WS_CONNECT_TIMEOUT}s")
                    
                    # Periodically log state during connection wait
                    self._log_state_periodically("connect_wait")
                    time.sleep(config.WS_POLL_INTERVAL)
                
                self._set_state(ConnectionState.CONNECTED)
                self.processing_enabled = True
                
                # Wait for server ready signal with timeout
                log_connection(logger, f"Waiting for server ready signal (timeout: {config.WS_READY_TIMEOUT}s)...")
                start_time = time.time()
                while not self.server_ready:
                    if time.time() - start_time > config.WS_READY_TIMEOUT:
                        self._set_state(ConnectionState.TIMEOUT_ERROR)
                        raise TimeoutError(f"Server ready timeout after {config.WS_READY_TIMEOUT}s")
                    
                    # Periodically log state during ready wait
                    self._log_state_periodically("ready_wait")
                    time.sleep(config.WS_POLL_INTERVAL)
                
                # Connection successful
                total_connect_time = time.time() - connect_start_time
                log_connection(logger, f"Connection established successfully in {total_connect_time:.2f}s")
                return True
                    
            except Exception as e:
                retry_count += 1
                if self.state != ConnectionState.TIMEOUT_ERROR:
                    self._set_state(ConnectionState.CONNECT_ERROR)
                self.server_ready = False
                
                if retry_count < max_retries:
                    log_error(logger, f"Connection error (attempt {retry_count}/{max_retries}): {str(e)}")
                    log_connection(logger, f"Retrying in {retry_delay:.1f}s...")
                    time.sleep(retry_delay)
                    retry_delay = min(retry_delay * 2, config.WS_MAX_RETRY_DELAY)
                else:
                    log_error(logger, f"Maximum retry attempts reached ({max_retries}). Last error: {str(e)}")
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
        """Callback for incoming server messages with enhanced error handling"""
        if not self.processing_enabled:
            return
            
        try:
            message_start = time.time()
            
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
                            callback_start = time.time()
                            self.on_text_callback([segments[-1]])
                            callback_duration = time.time() - callback_start
                            if callback_duration > config.WS_MESSAGE_WAIT:
                                log_connection(logger, f"Text callback took longer than expected: {callback_duration:.2f}s")
            
            # Check if message processing took too long
            message_duration = time.time() - message_start
            if message_duration > config.WS_MESSAGE_WAIT:
                log_connection(logger, f"Message processing took longer than expected: {message_duration:.2f}s")
                    
        except Exception as e:
            log_error(logger, f"Error processing message: {str(e)}")
            self._set_state(ConnectionState.PROCESSING_ERROR)
    
    def _on_error(self, ws, error):
        """Callback for WebSocket errors with enhanced logging"""
        log_error(logger, f"WebSocket error: {str(error)}")
        self._set_state(ConnectionState.CONNECT_ERROR)
        
        # Log additional context for the error
        try:
            log_error(logger, f"Error context - State: {self.state.name}, "
                     f"Client ID: {self.client_id}, Session ID: {self.session_id}, "
                     f"Server ready: {self.server_ready}, Processing enabled: {self.processing_enabled}")
        except:
            pass  # Ignore errors in error logging
    
    def _on_close(self, ws, close_status_code, close_msg):
        """Callback when WebSocket connection is closed"""
        log_connection(logger, f"Connection closed (Status: {close_status_code}, Message: {close_msg})")
        self._set_state(ConnectionState.CLOSED)
        self.server_ready = False
    
    def is_ready(self):
        """Checks if the server is ready"""
        return self.state == ConnectionState.READY
    
    def send_audio(self, audio_data):
        """Sends audio data to the server with enhanced error handling"""
        if not self.processing_enabled or not self.is_ready():
            return False
            
        try:
            send_start = time.time()
            self.ws.send(audio_data, websocket.ABNF.OPCODE_BINARY)
            send_duration = time.time() - send_start
            
            # Log audio send with timing information
            log_audio(logger, f"Sent {len(audio_data)} bytes in {send_duration:.3f}s")
            
            # Check if send took too long
            if send_duration > config.WS_MESSAGE_WAIT:
                log_connection(logger, f"Audio send took longer than expected: {send_duration:.2f}s")
            
            return True
        except Exception as e:
            log_error(logger, f"Error sending audio: {str(e)}")
            self._set_state(ConnectionState.CONNECT_ERROR)
            return False
    
    def set_text_callback(self, callback):
        """Sets the callback for received text segments"""
        self.on_text_callback = callback
    
    def send_end_of_audio(self):
        """Sends END_OF_AUDIO signal to the server with enhanced timeout handling"""
        if not self.is_ready() and self.state != ConnectionState.PROCESSING:
            return False
            
        try:
            self._set_state(ConnectionState.FINALIZING)
            send_start = time.time()
            self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
            send_duration = time.time() - send_start
            
            log_audio(logger, f"Sent END_OF_AUDIO signal in {send_duration:.3f}s")
            log_connection(logger, f"Waiting for final segments (timeout: {config.WS_FINAL_WAIT}s)...")
            
            # Wait for server to acknowledge END_OF_AUDIO with timeout
            wait_start = time.time()
            while self.state == ConnectionState.FINALIZING:
                if time.time() - wait_start > config.WS_FINAL_WAIT:
                    log_connection(logger, f"Final wait timeout reached after {config.WS_FINAL_WAIT}s")
                    break
                
                # Periodically log state during finalization
                self._log_state_periodically("finalization_wait")
                time.sleep(config.WS_POLL_INTERVAL)
            
            wait_duration = time.time() - wait_start
            log_connection(logger, f"Finalization completed in {wait_duration:.2f}s")
            return True
        except Exception as e:
            log_error(logger, f"Error sending END_OF_AUDIO: {str(e)}")
            return False
    
    def stop_processing(self):
        """Stops processing server messages with enhanced timeout handling"""
        if self.processing_enabled:
            stop_start = time.time()
            log_connection(logger, "Stopping message processing...")
            
            try:
                if self.is_ready() or self.state == ConnectionState.PROCESSING:
                    # Send END_OF_AUDIO and wait for processing
                    self._set_state(ConnectionState.FINALIZING)
                    self.ws.send(b"END_OF_AUDIO", websocket.ABNF.OPCODE_BINARY)
                    log_audio(logger, "Sent END_OF_AUDIO signal")
                    
                    # Wait for final segments with timeout monitoring
                    wait_start = time.time()
                    last_message_time = wait_start
                    
                    while True:
                        # Check timeout
                        current_time = time.time()
                        if current_time - wait_start > config.WS_FINAL_WAIT:
                            log_connection(logger, f"Final wait timeout reached after {config.WS_FINAL_WAIT}s")
                            break
                            
                        # Check inactivity
                        if current_time - last_message_time > config.WS_MESSAGE_WAIT:
                            log_connection(logger, f"No new messages for {config.WS_MESSAGE_WAIT}s, stopping")
                            break
                        
                        # Periodically log state during stop processing
                        self._log_state_periodically("stop_processing_wait")
                        
                        # Short pause
                        time.sleep(config.WS_POLL_INTERVAL)
                    
                    # Disable processing
                    self.processing_enabled = False
                    self.current_text = ""
                    
                    # Close connection cleanly
                    self._set_state(ConnectionState.CLOSING)
                    log_connection(logger, "Closing connection...")
                    close_start = time.time()
                    self.ws.close()
                    close_duration = time.time() - close_start
                    log_connection(logger, f"Connection close() completed in {close_duration:.2f}s")
                    
                    # Wait for thread to end with timeout
                    if self.ws_thread and self.ws_thread.is_alive():
                        join_start = time.time()
                        log_connection(logger, f"Waiting for WebSocket thread to terminate (timeout: {config.WS_THREAD_TIMEOUT}s)...")
                        self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
                        
                        # Check if thread is still alive after join timeout
                        if self.ws_thread.is_alive():
                            log_error(logger, f"WebSocket thread did not terminate within {config.WS_THREAD_TIMEOUT}s timeout")
                            log_connection(logger, "Proceeding with cleanup despite thread still running")
                        else:
                            join_duration = time.time() - join_start
                            log_connection(logger, f"WebSocket thread terminated in {join_duration:.2f}s")
                
            except Exception as e:
                log_error(logger, f"Error stopping processing: {str(e)}")
            finally:
                self.processing_enabled = False
                self._set_state(ConnectionState.CLOSED)
                self.server_ready = False
                stop_duration = time.time() - stop_start
                log_connection(logger, f"Processing stopped in {stop_duration:.2f}s")
    
    def start_processing(self):
        """Starts processing server messages with enhanced error handling"""
        if not self.is_ready():
            log_error(logger, f"Server not ready for processing (current state: {self.state.name})")
            return False
            
        start_time = time.time()
        log_connection(logger, "Starting message processing...")
        
        self.processing_enabled = True
        self.current_text = ""
        
        try:
            # Clear clipboard
            clipboard_start = time.time()
            try:
                win32clipboard.OpenClipboard()
                win32clipboard.EmptyClipboard()
                win32clipboard.CloseClipboard()
                clipboard_duration = time.time() - clipboard_start
                log_connection(logger, f"Clipboard cleared in {clipboard_duration:.3f}s")
            except Exception as e:
                log_error(logger, f"Could not clear clipboard: {str(e)}")
            
            self._set_state(ConnectionState.PROCESSING)
            total_duration = time.time() - start_time
            log_connection(logger, f"Server message processing enabled in {total_duration:.2f}s")
            return True
            
        except Exception as e:
            log_error(logger, f"Error starting processing: {str(e)}")
            self.processing_enabled = False
            return False
    
    def cleanup(self):
        """Release resources with enhanced timeout handling and logging"""
        if not self.ws:
            return
            
        cleanup_start = time.time()
        log_connection(logger, f"Starting cleanup for session {self.session_id}...")
        
        try:
            # Set a timeout for the entire cleanup operation
            cleanup_timeout = config.WS_CLEANUP_TIMEOUT
            
            # Disable processing
            self.processing_enabled = False
            
            # Close WebSocket connection
            if self.ws and self.ws.sock:
                self._set_state(ConnectionState.CLOSING)
                close_start = time.time()
                log_connection(logger, "Closing WebSocket connection...")
                self.ws.close()
                close_duration = time.time() - close_start
                log_connection(logger, f"WebSocket close() completed in {close_duration:.2f}s")
            
            # Wait for thread to terminate
            if self.ws_thread and self.ws_thread.is_alive():
                join_start = time.time()
                log_connection(logger, f"Waiting for WebSocket thread to terminate (timeout: {config.WS_THREAD_TIMEOUT}s)...")
                self.ws_thread.join(timeout=config.WS_THREAD_TIMEOUT)
                
                # Check if thread is still alive after join timeout
                if self.ws_thread.is_alive():
                    log_error(logger, f"WebSocket thread did not terminate within {config.WS_THREAD_TIMEOUT}s timeout")
                    log_connection(logger, "Proceeding with cleanup despite thread still running")
                else:
                    join_duration = time.time() - join_start
                    log_connection(logger, f"WebSocket thread terminated in {join_duration:.2f}s")
            
            # Check overall cleanup timeout
            if time.time() - cleanup_start > cleanup_timeout:
                log_error(logger, f"Cleanup operation taking longer than expected ({cleanup_timeout}s)")
        
        except Exception as e:
            log_error(logger, f"Error during cleanup: {str(e)}")
        finally:
            self.ws = None
            self._set_state(ConnectionState.DISCONNECTED)
            self.server_ready = False
            cleanup_duration = time.time() - cleanup_start
            log_connection(logger, f"Cleanup completed for session {self.session_id} in {cleanup_duration:.2f}s")
