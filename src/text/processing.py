"""
Text Processing Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 12:59 CET

This module handles text processing, including sentence detection,
formatting, and special text handling like abbreviations and ellipses.
"""

import config


def is_sentence_end(text, common_abbreviations):
    """Checks if a text marks the end of a sentence"""
    # Check for abbreviations at the end of the text
    text_lower = text.lower()
    for abbr in common_abbreviations:
        if text_lower.endswith(abbr.lower()) and not any(
            text_lower.endswith(abbr.lower() + p) for p in config.SENTENCE_END_MARKERS
        ):
            return False

    # Special handling for ellipsis
    if text.endswith("..."):
        return True

    # Check for multiple sentence end markers (like !? or ?!)
    for i in range(len(text) - 1, 0, -1):
        if text[i] in ".!?" and text[i - 1] in ".!?":
            return True

    # Check for sentence punctuation
    return any(text.endswith(p) for p in config.SENTENCE_END_MARKERS)


def format_sentence(text, common_abbreviations):
    """Formats a sentence for output"""
    # Remove multiple spaces
    text = " ".join(text.split())

    # Special handling for ellipsis
    text = text.replace(" . . .", "...")
    text = text.replace(". . .", "...")

    # Special handling for multiple sentence end markers
    # Don't add spaces between them
    for marker1 in ".!?":
        for marker2 in ".!?":
            if marker1 != "." or marker2 != ".":  # Skip '..', which is part of ellipsis
                text = text.replace(marker1 + " " + marker2, marker1 + marker2)

    # Check if the text is part of a larger sentence
    starts_sentence = not any(
        text.lower().startswith(word) for word in ["und", "oder", "aber", "denn"]
    )

    # First letter uppercase if it's the beginning of a sentence
    if (
        text
        and starts_sentence
        and not any(text.startswith(abbr) for abbr in common_abbreviations)
    ):
        text = text[0].upper() + text[1:]

    return text


def find_overlap(text1, text2):
    """Finds the overlap between two texts"""
    # Find the longest overlap between the end of text1 and the start of text2
    max_overlap = ""
    for i in range(1, min(len(text1), len(text2)) + 1):
        if text1[-i:] == text2[:i]:
            max_overlap = text1[-i:]
    return max_overlap
