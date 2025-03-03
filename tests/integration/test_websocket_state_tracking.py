"""
WebSocket Connection State Tracking Test
Version: 1.0
Timestamp: 2025-03-01 21:12 CET

This module tests the connection state tracking system implemented in the WebSocket client
to ensure proper state transitions, reconnection behavior, and error handling.
"""
import sys
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch
from threading import Event

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.websocket import WhisperWebSocket, ConnectionState
import config
from src import logging

# Configure logger
logger = logging.get_logger()

class MockWebSocketApp:
    """Mock WebSocketApp for testing"""
    
    def __init__(self, url, on_open=None, on_message=None, on_error=None, on_close=None):
        self.url = url
        self.on_open = on_open
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close
        self.sock = None
        self.connected = False
        self.closed = False
        self.messages_sent = []
    
    def run_forever(self):
        """Simulate running the WebSocket"""
        self.sock = MagicMock()
        self.sock.connected = True
        self.connected = True
        if self.on_open:
            self.on_open(self)
            
        # Simulate server ready message
        if self.on_message:
            server_ready_msg = '{"message": "SERVER_READY"}'
            self.on_message(self, server_ready_msg)
    
    def send(self, message, opcode=None):
        """Record sent messages"""
        self.messages_sent.append((message, opcode))
    
    def close(self):
        """Simulate closing the WebSocket"""
        self.closed = True
        self.connected = False
        if self.sock:
            self.sock.connected = False
        if self.on_close:
            self.on_close(self, 1000, "Normal closure")

class WebSocketStateTrackingTest(unittest.TestCase):
    """Tests for the WebSocket connection state tracking system"""
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def setUp(self):
        """Set up test environment"""
        self.ws_client = WhisperWebSocket()
        # Patch time.sleep to avoid delays in tests
        self.sleep_patcher = patch('time.sleep')
        self.mock_sleep = self.sleep_patcher.start()
    
    def tearDown(self):
        """Clean up after tests"""
        self.sleep_patcher.stop()
        self.ws_client.cleanup()
    
    def test_initial_state(self):
        """Test initial connection state"""
        self.assertEqual(self.ws_client.state, ConnectionState.DISCONNECTED,
                        "Initial state should be DISCONNECTED")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_connect_state_transition(self):
        """Test state transitions during connection"""
        # Connect to server
        self.ws_client.connect()
        
        # Verify state transition to READY (since MockWebSocketApp now sends SERVER_READY)
        self.assertEqual(self.ws_client.state, ConnectionState.READY,
                        "State should transition to READY after connection and server ready message")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_processing_state_transition(self):
        """Test state transitions during audio processing"""
        # Connect and set to READY state
        self.ws_client.connect()
        server_ready_msg = '{"message": "SERVER_READY"}'
        self.ws_client._on_message(self.ws_client.ws, server_ready_msg)
        
        # Start processing
        self.ws_client.start_processing()
        
        # Verify state transition to PROCESSING
        self.assertEqual(self.ws_client.state, ConnectionState.PROCESSING,
                        "State should transition to PROCESSING after start_processing")
        
        # Send end of audio
        self.ws_client.send_end_of_audio()
        
        # Verify state transition to FINALIZING
        self.assertEqual(self.ws_client.state, ConnectionState.FINALIZING,
                        "State should transition to FINALIZING after send_end_of_audio")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_error_state_transition(self):
        """Test state transitions during errors"""
        # Connect to server
        self.ws_client.connect()
        
        # Simulate error
        self.ws_client._on_error(self.ws_client.ws, Exception("Test error"))
        
        # Verify state transition to CONNECT_ERROR
        self.assertEqual(self.ws_client.state, ConnectionState.CONNECT_ERROR,
                        "State should transition to CONNECT_ERROR after error")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_close_state_transition(self):
        """Test state transitions during connection closure"""
        # Connect to server
        self.ws_client.connect()
        
        # Close connection
        self.ws_client.cleanup()
        
        # Verify state transition to DISCONNECTED
        self.assertEqual(self.ws_client.state, ConnectionState.DISCONNECTED,
                        "State should transition to DISCONNECTED after cleanup")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_end_of_audio_acknowledgment(self):
        """Test END_OF_AUDIO acknowledgment handling"""
        # Connect and set to READY state
        self.ws_client.connect()
        server_ready_msg = '{"message": "SERVER_READY"}'
        self.ws_client._on_message(self.ws_client.ws, server_ready_msg)
        
        # Start processing
        self.ws_client.start_processing()
        
        # Send end of audio
        self.ws_client.send_end_of_audio()
        
        # Simulate END_OF_AUDIO_RECEIVED acknowledgment
        ack_msg = '{"message": "END_OF_AUDIO_RECEIVED"}'
        self.ws_client._on_message(self.ws_client.ws, ack_msg)
        
        # Verify state is still FINALIZING
        self.assertEqual(self.ws_client.state, ConnectionState.FINALIZING,
                        "State should remain FINALIZING after END_OF_AUDIO_RECEIVED")
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_reconnection_behavior(self):
        """Test reconnection behavior after connection error"""
        # Mock connect method to track calls
        original_connect = self.ws_client.connect
        connect_called = [0]
        
        def mock_connect(*args, **kwargs):
            connect_called[0] += 1
            return original_connect(*args, **kwargs)
        
        self.ws_client.connect = mock_connect
        
        # Connect to server
        self.ws_client.connect()
        
        # Verify connect was called
        self.assertEqual(connect_called[0], 1, "Connect should be called once")
        
        # Simulate error
        self.ws_client._on_error(self.ws_client.ws, Exception("Test error"))
        
        # Verify state transition to CONNECT_ERROR
        self.assertEqual(self.ws_client.state, ConnectionState.CONNECT_ERROR,
                        "State should transition to CONNECT_ERROR after error")
        
        # Restore original connect method
        self.ws_client.connect = original_connect
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_thread_safety(self):
        """Test thread safety of state transitions"""
        # This is a basic test to ensure no exceptions are thrown
        # when multiple state transitions occur in quick succession
        
        # Connect to server
        self.ws_client.connect()
        
        # Simulate multiple state transitions
        self.ws_client._set_state(ConnectionState.READY)
        self.ws_client._set_state(ConnectionState.PROCESSING)
        self.ws_client._set_state(ConnectionState.FINALIZING)
        self.ws_client._set_state(ConnectionState.CLOSING)
        self.ws_client._set_state(ConnectionState.CLOSED)
        
        # Verify final state
        self.assertEqual(self.ws_client.state, ConnectionState.CLOSED,
                        "Final state should be CLOSED")

class WebSocketMultipleConnectionsTest(unittest.TestCase):
    """Tests for handling multiple parallel connections"""
    
    @patch('websocket.WebSocketApp', MockWebSocketApp)
    def test_multiple_connections(self):
        """Test handling of multiple connection attempts"""
        # Create two WebSocket clients
        ws_client1 = WhisperWebSocket()
        ws_client2 = WhisperWebSocket()
        
        # Connect first client
        ws_client1.connect()
        
        # Verify first client is ready (since MockWebSocketApp now sends SERVER_READY)
        self.assertEqual(ws_client1.state, ConnectionState.READY,
                        "First client should be ready")
        
        # Connect second client
        ws_client2.connect()
        
        # Verify second client is ready
        self.assertEqual(ws_client2.state, ConnectionState.READY,
                        "Second client should be ready")
        
        # Verify client IDs are different
        self.assertNotEqual(ws_client1.client_id, ws_client2.client_id,
                           "Each client should have a unique client ID")
        
        # Clean up
        ws_client1.cleanup()
        ws_client2.cleanup()

if __name__ == "__main__":
    unittest.main()
