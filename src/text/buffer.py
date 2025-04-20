"""
Text Buffer Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 12:58 CET

This module provides a thread-safe buffer for text segments with
functionality for duplicate detection and segment management.
"""

import collections
import threading
import time
from typing import List

import config
from text.segment import TextSegment


class TextBuffer:
    """Thread-safe ring buffer for text segments"""

    def __init__(self, max_size=config.TEXT_BUFFER_SIZE, max_age=config.TEXT_BUFFER_MAX_AGE):
        """Initialize the buffer with specified size and age limits"""
        self.max_size = max_size
        self.max_age = max_age
        self.buffer: collections.deque[TextSegment] = collections.deque(maxlen=max_size)
        self.lock = threading.RLock()  # Reentrant lock for thread safety
        self.sequence_counter = 0
        self.text_lookup = {}  # For quick duplicate detection

    def add_segment(self, text: str) -> TextSegment:
        """Add a new text segment to the buffer"""
        with self.lock:
            # Clean up old segments first
            self._cleanup_old_segments()

            # Create new segment
            segment = TextSegment(
                text=text, timestamp=time.time(), sequence=self.sequence_counter, processed=False
            )
            self.sequence_counter += 1

            # Add to buffer and lookup
            self.buffer.append(segment)
            self.text_lookup[text.lower()] = segment

            return segment

    def mark_processed(self, segment: TextSegment, output: str = None):
        """Mark a segment as processed with optional output text"""
        with self.lock:
            if segment in self.buffer:
                segment.processed = True
                segment.output = output

    def is_duplicate(self, text: str) -> bool:
        """Check if text is a duplicate of recent segments"""
        with self.lock:
            # Normalize text for comparison
            normalized_text = " ".join(text.lower().split())

            # Direct match
            if normalized_text in self.text_lookup:
                return True

            # Substring match (both ways)
            for existing_text, segment in self.text_lookup.items():
                # Skip old segments
                if time.time() - segment.timestamp > self.max_age:
                    continue

                # Check if this text is a substring of existing text
                if normalized_text in existing_text:
                    return True

                # Check if existing text is a substring of this text
                if existing_text in normalized_text:
                    # Only consider it a duplicate if it's a significant portion
                    # For longer texts, we're more lenient with the threshold
                    if len(existing_text) > 0.5 * len(normalized_text):
                        return True

            return False

    def get_recent_segments(
        self, count=None, processed_only=False, max_age=None
    ) -> List[TextSegment]:
        """Get recent segments from the buffer"""
        with self.lock:
            if max_age is None:
                max_age = self.max_age

            current_time = time.time()
            result = []

            # Get segments in chronological order (oldest first)
            segments = list(self.buffer)

            for segment in segments:
                if processed_only and not segment.processed:
                    continue

                if current_time - segment.timestamp > max_age:
                    continue

                result.append(segment)

                if count is not None and len(result) >= count:
                    break

            return result  # Already in chronological order

    def get_unprocessed_segments(self) -> List[TextSegment]:
        """Get all unprocessed segments"""
        with self.lock:
            return [s for s in self.buffer if not s.processed]

    def clear(self):
        """Clear the buffer"""
        with self.lock:
            self.buffer.clear()
            self.text_lookup.clear()

    def _cleanup_old_segments(self):
        """Remove segments that exceed the maximum age"""
        with self.lock:
            current_time = time.time()
            to_remove = []

            for text, segment in self.text_lookup.items():
                if current_time - segment.timestamp > self.max_age:
                    to_remove.append(text)

            for text in to_remove:
                del self.text_lookup[text]

            # The deque automatically handles size limits, but we need to clean up old segments
            while self.buffer and current_time - self.buffer[0].timestamp > self.max_age:
                self.buffer.popleft()
