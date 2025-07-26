"""
Audio Window Processing Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:39 CET

This module implements the tumbling window approach for audio processing,
providing smooth transitions between consecutive windows through linear
crossfading in the overlap regions.
"""

import numpy as np

import config
from src import logger
from src.logging import log_debug


class TumblingWindow:
    """Implements a tumbling window approach for audio processing.

    This class manages audio data in windows with configurable size and
    overlap, providing a smooth transition between consecutive windows
    through linear crossfading in the overlap regions.

    """

    def __init__(
        self, window_size=config.TUMBLING_WINDOW_SIZE, overlap=config.TUMBLING_WINDOW_OVERLAP
    ):
        """Initialize the tumbling window processor.

        Args:
            window_size: Size of each window in samples
            overlap: Overlap between windows as a fraction (0.0 - 1.0)

        """
        self.window_size = window_size
        self.overlap = max(0.0, min(1.0, overlap))  # Ensure overlap is between 0 and 1
        self.overlap_size = int(window_size * overlap)
        self.buffer = []
        self.previous_window = None
        log_debug(logger, "TumblingWindow initialized: size=%d, overlap=%.2f", window_size, overlap)

    def add_chunk(self, chunk):
        """Add an audio chunk to the buffer.

        Args:
            chunk: Audio data as bytes or numpy array

        """
        # Convert bytes to numpy array if needed
        if isinstance(chunk, bytes):
            chunk = np.frombuffer(chunk, dtype=np.int16)

        # Add chunk to buffer
        self.buffer.extend(chunk)
        log_debug(
            logger, "Added chunk of %d samples, buffer now %d samples", len(chunk), len(self.buffer)
        )

    def get_windows(self):
        """Generator that yields available windows from the buffer.

        Each window is a numpy array of samples with size equal to window_size.
        Windows are removed from the buffer as they are yielded, with overlap
        preserved for the next window.

        Yields:
            numpy.ndarray: Audio window of size window_size

        """
        while len(self.buffer) >= self.window_size:
            # Extract a complete window
            window = np.array(self.buffer[: self.window_size])

            # Apply crossfade with previous window if available
            if self.previous_window is not None and self.overlap > 0:
                # Create linear fade curves
                fade_out = np.linspace(1, 0, self.overlap_size)
                fade_in = np.linspace(0, 1, self.overlap_size)

                # Get overlap regions
                overlap_region = self.previous_window[-self.overlap_size :]
                current_overlap = window[: self.overlap_size]

                # Blend the overlap regions
                blended = (overlap_region * fade_out) + (current_overlap * fade_in)
                window[: self.overlap_size] = blended

                log_debug(logger, "Applied crossfade of %d samples", self.overlap_size)

            # Yield the processed window
            yield window

            # Update buffer and previous window
            # Remove window from buffer, keeping overlap for next window
            self.buffer = self.buffer[self.window_size - self.overlap_size :]
            self.previous_window = window

            log_debug(logger, "Window processed, buffer now %d samples", len(self.buffer))

    def clear(self):
        """Clear the buffer and reset state."""
        self.buffer = []
        self.previous_window = None
        log_debug(logger, "TumblingWindow buffer cleared")
