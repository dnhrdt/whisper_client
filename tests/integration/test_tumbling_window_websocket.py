"""
Tumbling Window WebSocket Integration Test
Version: 1.0
Timestamp: 2025-02-28 23:33 CET

This module tests the integration of the Tumbling Window with the WebSocket client
to ensure proper audio processing flow in the WhisperClient.
"""
import sys
import time
import numpy as np
from pathlib import Path
import unittest
from queue import Queue
from threading import Event, Thread
from unittest.mock import MagicMock, patch

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.audio import TumblingWindow, AudioProcessor
from src.websocket import WhisperWebSocket
import config
from src import logging

# Configure logger
logger = logging.get_logger()

class MockWebSocket:
    """Mock WebSocket client for testing"""
    
    def __init__(self):
        self.connected = True
        self.server_ready = True
        self.sent_audio = []
        self.on_text_callback = None
    
    def send_audio(self, audio_data):
        """Record sent audio data"""
        self.sent_audio.append(audio_data)
        return True
    
    def is_ready(self):
        """Always return ready for testing"""
        return self.connected and self.server_ready
    
    def set_text_callback(self, callback):
        """Set callback for text segments"""
        self.on_text_callback = callback

class TumblingWindowWebSocketTest(unittest.TestCase):
    """Tests for the integration of TumblingWindow with WebSocket client"""
    
    def setUp(self):
        """Set up test environment"""
        self.mock_websocket = MockWebSocket()
        self.audio_processor = AudioProcessor(test_mode=False)
    
    def test_audio_flow(self):
        """Test audio data flow from AudioProcessor to WebSocket"""
        # Start audio processing with mock WebSocket callback
        self.audio_processor.start_processing(self.mock_websocket.send_audio)
        
        # Create a simple sine wave
        samples = 10000  # Enough for multiple windows
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)
        audio_bytes = audio.tobytes()
        
        # Process audio
        self.audio_processor.process_audio(audio_bytes)
        
        # Give some time for processing to complete
        time.sleep(0.5)
        
        # Stop processing
        self.audio_processor.stop_processing()
        
        # Verify audio was sent to WebSocket
        self.assertGreater(len(self.mock_websocket.sent_audio), 0, 
                          "WebSocket should receive processed audio")
        
        # Verify format of sent audio
        for audio_chunk in self.mock_websocket.sent_audio:
            self.assertIsInstance(audio_chunk, bytes, 
                                 "WebSocket should receive audio as bytes")
    
    def test_window_size_and_overlap(self):
        """Test that audio is processed with correct window size and overlap"""
        # Start audio processing with mock WebSocket callback
        self.audio_processor.start_processing(self.mock_websocket.send_audio)
        
        # Create a simple sine wave
        samples = 10000  # Enough for multiple windows
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)
        audio_bytes = audio.tobytes()
        
        # Process audio
        self.audio_processor.process_audio(audio_bytes)
        
        # Give some time for processing to complete
        time.sleep(0.5)
        
        # Stop processing
        self.audio_processor.stop_processing()
        
        # Calculate expected number of windows
        window_size = config.TUMBLING_WINDOW_SIZE
        overlap = config.TUMBLING_WINDOW_OVERLAP
        overlap_size = int(window_size * overlap)
        step_size = window_size - overlap_size
        expected_windows = max(0, (samples - window_size) // step_size + 1)
        
        # Allow for some flexibility in the number of windows due to threading
        self.assertGreaterEqual(len(self.mock_websocket.sent_audio), expected_windows * 0.8,
                               f"Should send at least 80% of expected windows ({expected_windows})")
        
        # Verify size of audio chunks
        for audio_chunk in self.mock_websocket.sent_audio:
            # Each window should be window_size samples (2 bytes per sample for int16)
            self.assertEqual(len(audio_chunk), window_size * 2,
                            f"Audio chunk should be {window_size} samples")

class MainIntegrationTest(unittest.TestCase):
    """Tests for the integration in main.py"""
    
    @patch('src.websocket.WhisperWebSocket')
    @patch('src.audio.AudioProcessor')
    def test_main_integration(self, MockAudioProcessor, MockWebSocket):
        """Test the integration flow in main.py"""
        # Import main module
        from main import WhisperClient
        
        # Create mocks
        mock_websocket = MagicMock()
        MockWebSocket.return_value = mock_websocket
        mock_websocket.connected = True
        mock_websocket.is_ready.return_value = True
        
        mock_processor = MagicMock()
        MockAudioProcessor.return_value = mock_processor
        
        # Create client
        client = WhisperClient()
        
        # Verify AudioProcessor is initialized
        self.assertIsNotNone(client.audio_processor, 
                            "AudioProcessor should be initialized")
        
        # Simulate starting recording
        client.toggle_recording()
        
        # Verify audio processing is started
        mock_processor.start_processing.assert_called_once()
        
        # Verify the callback chain
        # The callback passed to start_processing should be client.on_processed_audio
        callback_arg = mock_processor.start_processing.call_args[0][0]
        self.assertEqual(callback_arg.__name__, "on_processed_audio",
                        "AudioProcessor should be started with on_processed_audio callback")
        
        # Create test audio data
        test_audio = b"test_audio_data"
        
        # Simulate audio data flow
        client.on_audio_data(test_audio)
        
        # Verify audio data is passed to AudioProcessor
        mock_processor.process_audio.assert_called_once_with(test_audio)
        
        # Simulate processed audio data
        processed_audio = b"processed_audio_data"
        client.on_processed_audio(processed_audio)
        
        # Verify processed audio is sent to WebSocket
        mock_websocket.send_audio.assert_called_once_with(processed_audio)
        
        # Simulate stopping recording
        client.toggle_recording()
        
        # Verify cleanup
        mock_processor.stop_processing.assert_called_once()
        mock_websocket.stop_processing.assert_called_once()

if __name__ == "__main__":
    unittest.main()
