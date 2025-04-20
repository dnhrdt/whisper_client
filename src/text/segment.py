"""
Text Segment Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 12:58 CET

This module defines the TextSegment dataclass used for representing
text segments with metadata throughout the application.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class TextSegment:
    """Represents a text segment with metadata"""
    text: str
    timestamp: float
    sequence: int
    processed: bool = False
    output: Optional[str] = None

    def __hash__(self):
        """Enable use in sets and as dict keys"""
        return hash((self.text, self.sequence))
