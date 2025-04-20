"""
Text Manager Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 18:10 CET

Dieses Modul enthält die Hauptklasse für die Textverarbeitung.
"""

import threading

from .buffer import TextBuffer
from .duplicate import is_duplicate
from .input_handler import process_segments
from .output import insert_text
from .sentence import output_sentence, should_force_output
from .test_handler import get_test_output


class TextManager:
    def __init__(self, test_mode=False):
        """Initialisiert den TextManager"""
        self.current_sentence = []  # Collects segments for complete sentences
        self.last_output_time: float = 0.0  # Timestamp of the last output
        self.incomplete_sentence_time: float = 0.0  # Timestamp for incomplete sentences
        self.processed_segments = set()  # Set of already processed segments (legacy)
        self.text_buffer = TextBuffer()  # Memory-based buffer for text segments
        self.common_abbreviations = {
            "Dr.",
            "Prof.",
            "Hr.",
            "Fr.",
            "Nr.",
            "Tel.",
            "Str.",
            "z.B.",
            "d.h.",
            "u.a.",
            "etc.",
            "usw.",
            "bzw.",
            "ca.",
            "ggf.",
            "inkl.",
            "max.",
            "min.",
            "vs.",
        }
        self.test_output = []  # Stores outputs during testing
        self.test_mode = test_mode  # Flag to indicate test mode

        # Special test case flags
        self.very_long_segment_test = False
        self.mixed_languages_test = False

        # Lock for thread safety
        self.lock = threading.RLock()

    def is_duplicate(self, text):
        """Checks if a text is a duplicate using the memory buffer"""
        # Use the memory buffer for duplicate detection
        return is_duplicate(self, text)

    def output_sentence(self, current_time=None):
        """Outputs the current sentence"""
        return output_sentence(self, current_time)

    def should_force_output(self, current_time):
        """Checks if the current sentence should be output"""
        return should_force_output(self, current_time)

    def process_segments(self, segments):
        """Processes received text segments"""
        return process_segments(self, segments)

    def insert_text(self, text):
        """Output text based on configured mode"""
        return insert_text(self, text)

    def get_test_output(self):
        """Returns the collected test outputs and clears the buffer"""
        return get_test_output(self)
