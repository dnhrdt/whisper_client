"""
Sentence Processing Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 14:00 CET

Dieses Modul enthält Funktionen zur Satzverarbeitung und -ausgabe.
"""

import time

import config
from src import logger
from text.processing import format_sentence


def output_sentence(manager, current_time=None):
    """Outputs the current sentence"""
    if not manager.current_sentence:
        return

    if current_time is None:
        current_time = time.time()

    # Join all segments, preserving special punctuation
    joined_text = " ".join(manager.current_sentence)

    # Handle special cases like ellipsis
    joined_text = joined_text.replace(" . . .", "...")
    joined_text = joined_text.replace(" ...", "...")

    # Format the complete sentence
    complete_text = format_sentence(joined_text, manager.common_abbreviations)

    # Output the text
    manager.insert_text(complete_text)

    # Add to buffer as a processed segment
    with manager.lock:
        segment = manager.text_buffer.add_segment(joined_text)
        manager.text_buffer.mark_processed(segment, complete_text)

    # Reset state
    manager.current_sentence = []
    manager.last_output_time = current_time
    manager.incomplete_sentence_time = current_time

    # Clear the processed segments (legacy)
    manager.processed_segments.clear()

    # Reset test flags
    manager.very_long_segment_test = False
    manager.mixed_languages_test = False


def should_force_output(manager, current_time):
    """Checks if the current sentence should be output"""
    if not manager.current_sentence:
        return False

    # Check for timeout
    if current_time - manager.incomplete_sentence_time > config.MAX_SENTENCE_WAIT:
        return True

    # Check for complete sentence
    current_text = " ".join(manager.current_sentence)
    if any(current_text.endswith(marker) for marker in config.SENTENCE_END_MARKERS):
        return True

    return False
