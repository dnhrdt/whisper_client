"""
Tumbling Window Integration Test
Version: 1.0
Timestamp: 2025-02-28 23:10 CET

This module tests the integration of the Tumbling Window implementation
for audio processing in the WhisperClient.
"""

import sys
import time
import unittest
from pathlib import Path
from queue import Queue
from threading import Event, Thread

import numpy as np

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import config
from src import logging
from src.audio import AudioProcessor, TumblingWindow

# Configure logger
logger = logging.get_logger()


class TumblingWindowTest(unittest.TestCase):
    """Tests for the TumblingWindow class."""

    def setUp(self):
        """Set up test environment."""
        self.window_size = 2048
        self.overlap = 0.25
        self.window = TumblingWindow(window_size=self.window_size, overlap=self.overlap)

    def test_initialization(self):
        """Test proper initialization of TumblingWindow."""
        self.assertEqual(self.window.window_size, self.window_size)
        self.assertEqual(self.window.overlap, self.overlap)
        self.assertEqual(self.window.overlap_size, int(self.window_size * self.overlap))
        self.assertEqual(len(self.window.buffer), 0)
        self.assertIsNone(self.window.previous_window)

    def test_add_chunk_bytes(self):
        """Test adding a bytes chunk to the window."""
        # Create a simple sine wave as bytes
        samples = 1000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)
        chunk = audio.tobytes()

        # Add chunk to window
        self.window.add_chunk(chunk)

        # Verify buffer size
        self.assertEqual(len(self.window.buffer), samples)

    def test_add_chunk_numpy(self):
        """Test adding a numpy array chunk to the window."""
        # Create a simple sine wave as numpy array
        samples = 1000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)

        # Add chunk to window
        self.window.add_chunk(audio)

        # Verify buffer size
        self.assertEqual(len(self.window.buffer), samples)

    def test_get_windows(self):
        """Test retrieving windows from the buffer."""
        # Create a simple sine wave
        samples = 5000  # Enough for multiple windows
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)

        # Add chunk to window
        self.window.add_chunk(audio)

        # Get windows
        windows = list(self.window.get_windows())

        # Calculate expected number of windows
        # With overlap, we should get more windows than without
        expected_step = self.window_size - self.window.overlap_size
        expected_windows = max(0, (samples - self.window_size) // expected_step + 1)

        # Verify number of windows
        self.assertEqual(len(windows), expected_windows)

        # Verify window size
        for window in windows:
            self.assertEqual(len(window), self.window_size)

    def test_window_overlap(self):
        """Test that windows properly overlap."""
        # Create a simple sine wave
        samples = 5000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)

        # Add chunk to window
        self.window.add_chunk(audio)

        # Get windows
        windows = list(self.window.get_windows())

        # Verify overlap between consecutive windows
        for i in range(1, len(windows)):
            prev_end = windows[i - 1][-self.window.overlap_size :]
            curr_start = windows[i][: self.window.overlap_size]

            # The overlapping regions should be blended, not identical
            # But they should be similar (not completely different)
            correlation = np.corrcoef(prev_end, curr_start)[0, 1]
            self.assertGreater(
                correlation, 0.5, "Windows should have significant correlation in overlap region"
            )

    def test_buffer_management(self):
        """Test that buffer is properly managed after getting windows."""
        # Create a simple sine wave
        samples = 5000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)

        # Add chunk to window
        self.window.add_chunk(audio)

        # Get initial buffer size
        initial_buffer_size = len(self.window.buffer)

        # Get one window
        next(self.window.get_windows())

        # Verify buffer size decreased by the step size
        expected_size = initial_buffer_size - (self.window_size - self.window.overlap_size)
        self.assertEqual(len(self.window.buffer), expected_size)

    def test_incremental_processing(self):
        """Test processing audio in small increments."""
        # Create a simple sine wave
        sample_rate = 16000
        duration = 1.0  # seconds
        total_samples = int(sample_rate * duration)
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, duration, total_samples))
        audio = (audio * 32767).astype(np.int16)

        # Process in small chunks
        chunk_size = 512
        chunks = [audio[i : i + chunk_size] for i in range(0, len(audio), chunk_size)]

        windows = []
        for chunk in chunks:
            self.window.add_chunk(chunk)
            windows.extend(list(self.window.get_windows()))

        # Verify we got some windows
        self.assertGreater(len(windows), 0)

        # Verify all windows have the correct size
        for window in windows:
            self.assertEqual(len(window), self.window_size)


class TumblingWindowPerformanceTest(unittest.TestCase):
    """Performance tests for the TumblingWindow class."""

    def test_realtime_performance(self):
        """Test performance under simulated real-time conditions."""
        window = TumblingWindow(window_size=2048, overlap=0.25)
        audio_queue = Queue()
        stop_event = Event()

        # Create a simple sine wave
        sample_rate = 16000
        chunk_size = 512
        duration = 3.0  # seconds

        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz tone
        audio = (audio * 32767).astype(np.int16)

        chunks = [audio[i : i + chunk_size] for i in range(0, len(audio), chunk_size)]

        def audio_producer():
            """Simulates audio input."""
            for chunk in chunks:
                if stop_event.is_set():
                    break
                audio_queue.put(chunk)
                time.sleep(chunk_size / sample_rate)  # Simulate real-time

        def audio_consumer():
            """Processes audio windows."""
            windows_processed = 0
            start_time = time.time()

            while not stop_event.is_set() or not audio_queue.empty():
                if not audio_queue.empty():
                    chunk = audio_queue.get()
                    window.add_chunk(chunk)

                    for w in window.get_windows():
                        windows_processed += 1
                        # Here we would normally process with Whisper

            duration = time.time() - start_time
            self.latency = (duration / windows_processed * 1000) if windows_processed > 0 else 0
            self.windows_processed = windows_processed

        # Run the test
        producer = Thread(target=audio_producer)
        consumer = Thread(target=audio_consumer)

        producer.start()
        consumer.start()

        time.sleep(3.5)  # Run test for 3.5 seconds
        stop_event.set()

        producer.join()
        consumer.join()

        # Verify performance
        print(
            f"Processed {self.windows_processed} windows with average latency of {self.latency:.2f}ms"
        )
        self.assertGreater(self.windows_processed, 0, "Should process at least one window")
        self.assertLess(self.latency, 200, "Average latency should be less than 200ms")


class AudioProcessorIntegrationTest(unittest.TestCase):
    """Tests for the integration of TumblingWindow with AudioProcessor."""

    def setUp(self):
        """Set up test environment."""
        self.audio_processor = AudioProcessor(test_mode=True)

    def test_tumbling_window_integration(self):
        """Test that TumblingWindow is properly integrated with
        AudioProcessor."""
        # Verify TumblingWindow is initialized
        self.assertIsNotNone(self.audio_processor.tumbling_window)

        # Create a simple sine wave
        samples = 5000
        audio = np.sin(2 * np.pi * 440 * np.linspace(0, 1, samples))
        audio = (audio * 32767).astype(np.int16)

        # Process audio
        self.audio_processor.process_audio(audio.tobytes())

        # Verify audio was processed
        self.assertGreater(len(self.audio_processor.processed_windows), 0)


if __name__ == "__main__":
    unittest.main()
