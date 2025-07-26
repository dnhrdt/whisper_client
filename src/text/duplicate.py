"""
Duplicate Detection Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 18:10 CET

Dieses Modul enthält Funktionen zur Erkennung von Duplikaten in Textsegmenten.
"""


def is_duplicate(manager, text):
    """Checks if a text is a duplicate using the memory buffer."""
    # Use the memory buffer for duplicate detection
    return manager.text_buffer.is_duplicate(text)


def normalize_text(text):
    """Normalizes text for duplicate detection."""
    return " ".join(text.lower().split())


def is_significant_overlap(text1, text2, threshold=0.5):
    """Checks if there is significant overlap between two texts."""
    # Only consider it a duplicate if it's a significant portion
    # For longer texts, we're more lenient with the threshold
    if len(text1) > threshold * len(text2):
        return True
    return False
