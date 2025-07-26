"""
Sentence Splitter Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 14:00 CET

Dieses Modul enthält Funktionen zur Aufteilung von Text in Sätze.
"""

import config


def split_into_sentences(text, common_abbreviations):
    """Teilt Text in Sätze auf."""
    # Prüfen, ob der Text sehr lang ist
    is_very_long = len(text) > 500

    if is_very_long:
        # Für sehr langen Text, einfach als einzelnes Segment hinzufügen
        return [text]
    else:
        # Text in Sätze aufteilen
        sentences = []
        current_sentence = ""

        # Durch jeden Buchstaben gehen
        for i, char in enumerate(text):
            current_sentence += char

            # Auf Satzende prüfen
            if check_sentence_end(text, i, current_sentence):
                sentences.append(current_sentence.strip())
                current_sentence = ""

        # Rest hinzufügen
        if current_sentence.strip():
            sentences.append(current_sentence.strip())

        return sentences


def check_sentence_end(text, i, current_sentence):
    """Prüft, ob an der aktuellen Position ein Satzende ist."""
    # Check for sentence end
    if any(
        text[i - len(marker) + 1 : i + 1] == marker
        for marker in config.SENTENCE_END_MARKERS
        if i >= len(marker) - 1
    ):
        # Check for abbreviations (using the marker)
        is_abbreviation = False
        if "ABBR_DOT" in current_sentence:
            is_abbreviation = True

        # Check for combined markers
        is_combined_marker = (
            "COMBINED_MARKER_" in current_sentence or "TRIPLE_MARKER_" in current_sentence
        )

        if not is_abbreviation and not is_combined_marker:
            return True

    return False
