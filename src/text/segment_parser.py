"""
Segment Parser Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 14:00 CET

Dieses Modul enthält Funktionen zum Parsen und Verarbeiten von Textsegmenten.
"""

import time

import config
from src import logger
from text.sentence_splitter import split_into_sentences
from text.sentence_combiner import handle_sentence_continuation
from text.segment_processor import process_single_sentence


def process_text(manager, text, current_time):
    """Verarbeitet einen Text"""
    # Text für die Verarbeitung vorbereiten
    prepared_text = prepare_text(text, manager.common_abbreviations)

    # Text in Sätze aufteilen
    sentences = split_into_sentences(prepared_text, manager.common_abbreviations)

    # Spezielle Marker wiederherstellen
    sentences = restore_special_markers(sentences)

    # Satzfortsetzungen behandeln
    sentences = handle_sentence_continuation(sentences)

    # Jeden Satz verarbeiten
    for sentence in sentences:
        process_single_sentence(manager, sentence, current_time)


def prepare_text(text, common_abbreviations):
    """Bereitet Text für die Verarbeitung vor"""
    # Ellipsen behandeln
    text = text.replace("...", " ELLIPSIS_MARKER ")

    # Mehrfache Satzendemarker behandeln
    text = handle_multiple_end_markers(text)

    # Abkürzungen behandeln
    for abbr in common_abbreviations:
        if abbr in text:
            text = text.replace(abbr, abbr.replace(".", "ABBR_DOT"))

    return text


def handle_multiple_end_markers(text):
    """Behandelt mehrfache Satzendemarker"""
    # First, identify and mark all combinations as special tokens
    # This prevents them from being split during sentence detection
    for marker1 in ".!?":
        for marker2 in ".!?":
            if marker1 != "." or marker2 != ".":  # Skip '..', which is part of ellipsis
                text = text.replace(marker1 + marker2, "COMBINED_MARKER_" + marker1 + marker2)

    # Also handle triple markers like '!?.'
    for marker1 in ".!?":
        for marker2 in ".!?":
            for marker3 in ".!?":
                if len(set([marker1, marker2, marker3])) > 1:  # At least two different markers
                    text = text.replace(
                        marker1 + marker2 + marker3,
                        "TRIPLE_MARKER_" + marker1 + marker2 + marker3,
                    )

    return text


def restore_special_markers(sentences):
    """Stellt spezielle Marker wieder her"""
    # Ellipsen wiederherstellen
    sentences = [s.replace("ELLIPSIS_MARKER", "...") for s in sentences]

    # Kombinierte Marker behandeln
    for i, sentence in enumerate(sentences):
        # Handle combined markers (2 characters)
        while "COMBINED_MARKER_" in sentence:
            start_idx = sentence.find("COMBINED_MARKER_")
            if start_idx >= 0:
                # Replace the marker with the actual characters (without spaces)
                marker_text = sentence[
                    start_idx
                    + len("COMBINED_MARKER_") : start_idx
                    + len("COMBINED_MARKER_")
                    + 2
                ]
                sentence = sentence.replace("COMBINED_MARKER_" + marker_text, marker_text, 1)
            else:
                break

        # Handle triple markers (3 characters)
        while "TRIPLE_MARKER_" in sentence:
            start_idx = sentence.find("TRIPLE_MARKER_")
            if start_idx >= 0:
                # Replace the marker with the actual characters (without spaces)
                marker_text = sentence[
                    start_idx + len("TRIPLE_MARKER_") : start_idx + len("TRIPLE_MARKER_") + 3
                ]
                sentence = sentence.replace("TRIPLE_MARKER_" + marker_text, marker_text, 1)
            else:
                break

        sentences[i] = sentence

    # Abkürzungen wiederherstellen
    sentences = [s.replace("ABBR_DOT", ".") for s in sentences]

    return sentences
