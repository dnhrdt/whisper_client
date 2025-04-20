"""
Audio Processing Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:38 CET

This module provides audio processing functionality using the tumbling window approach.
It integrates with the AudioManager to process audio chunks and prepare them for
the WhisperLive server.
"""

import threading
from queue import Empty, Queue
from typing import Callable, List, Optional

import numpy as np

import config
from src import logger
from src.logging import log_debug, log_error, log_info, log_warning

from .window import TumblingWindow


class AudioProcessor:
    """
    Processes audio data using the tumbling window approach.

    This class integrates with the AudioManager to process audio chunks
    and prepare them for the WhisperLive server.
    """

    def __init__(self, test_mode=False):
        """
        Initialize the audio processor.

        Args:
            test_mode: If True, operates in test mode without sending data
        """
        self.tumbling_window = TumblingWindow()
        self.test_mode = test_mode
        self.processed_windows: List[np.ndarray] = []
        self.window_callback: Optional[Callable[[bytes], None]] = None
        self.processing_lock = threading.Lock()
        self.processing_queue: Queue[bytes] = Queue()
        self.processing_thread: Optional[threading.Thread] = None
        self.running = False
        log_debug(logger, "AudioProcessor initialized")

    def start_processing(self, callback):
        """
        Start the audio processing thread.

        Args:
            callback: Function to call with processed audio windows
        """
        with self.processing_lock:
            if self.running:
                return

            self.window_callback = callback
            self.running = True

            # Start processing thread
            self.processing_thread = threading.Thread(target=self._process_queue)
            self.processing_thread.daemon = True
            self.processing_thread.start()

            log_info(logger, "🔄 Audio processing started")

    def stop_processing(self):
        """Stop the audio processing thread."""
        with self.processing_lock:
            if not self.running:
                return

            self.running = False

            # Wait for processing thread to finish
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=config.AUDIO_THREAD_TIMEOUT)
                if self.processing_thread.is_alive():
                    log_warning(logger, "Processing thread not responding - will terminate")

            # Clear state
            self.tumbling_window.clear()
            self.processing_queue = Queue()

            log_info(logger, "🛑 Audio processing stopped")

    def process_audio(self, audio_data):
        """
        Process audio data through the tumbling window.

        Args:
            audio_data: Audio data as bytes
        """
        # Add to processing queue
        self.processing_queue.put(audio_data)

        # If in test mode, process immediately
        if self.test_mode:
            self._process_audio_data(audio_data)

    def _process_queue(self):
        """Process audio data from the queue."""
        log_debug(logger, "Processing thread started")

        try:
            while self.running:
                try:
                    # Get audio data from queue with timeout
                    try:
                        audio_data = self.processing_queue.get(timeout=0.1)
                        self._process_audio_data(audio_data)
                        self.processing_queue.task_done()
                    except Empty:
                        continue

                except Exception as e:
                    log_error(logger, "Error processing audio: %s", e)

        finally:
            log_debug(logger, "Processing thread terminated")

    def _process_audio_data(self, audio_data):
        """
        Process a chunk of audio data.

        Args:
            audio_data: Audio data as bytes
        """
        # Add to tumbling window
        self.tumbling_window.add_chunk(audio_data)

        # Get windows and process
        windows = list(self.tumbling_window.get_windows())

        # In test mode, store windows
        if self.test_mode:
            self.processed_windows.extend(windows)
            return

        # Process each window
        for window in windows:
            # Convert to bytes
            window_bytes = window.tobytes()

            # Call callback with window
            if self.window_callback and self.running:
                self.window_callback(window_bytes)
