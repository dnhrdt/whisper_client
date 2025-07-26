"""
Segment Processor Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:41 CET

Dieses Modul enthält Funktionen zur Verarbeitung einzelner Textsegmente.
"""

import time

import config
from src import logger
from src.logging import log_info

from .processing import find_overlap


def process_single_sentence(manager, sentence, current_time):
    """Verarbeitet einen einzelnen Satz."""
    # Leere Sätze überspringen
    if not sentence.strip():
        return

    # Text für Duplikaterkennung normalisieren
    normalized_text = " ".join(sentence.lower().split())

    # Auf Duplikate prüfen
    if manager.is_duplicate(normalized_text):
        log_info(logger, "    ⚠️ Duplicate skipped: %s", sentence)
        return

    # Zum Textpuffer hinzufügen
    with manager.lock:
        manager.text_buffer.add_segment(sentence)

    # Legacy: Für Duplikaterkennung speichern
    manager.processed_segments.add(normalized_text)

    # Zeitstempel für unvollständige Sätze aktualisieren
    if not manager.current_sentence:
        manager.incomplete_sentence_time = current_time

    # Text zum aktuellen Satz hinzufügen
    add_to_current_sentence(manager, sentence)

    log_info(logger, "    ✓ Added to sentence: %s", sentence)

    # Prüfen, ob Ausgabe notwendig ist
    if manager.should_force_output(current_time):
        log_info(logger, "    ⚡ Output is forced")
        # Nur warten, wenn nötig
        wait_time = config.MIN_OUTPUT_INTERVAL - (current_time - manager.last_output_time)
        if wait_time > 0:
            time.sleep(wait_time)
        manager.output_sentence(current_time)


def add_to_current_sentence(manager, sentence):
    """Fügt Text zum aktuellen Satz hinzu."""
    if not manager.current_sentence:
        manager.current_sentence = [sentence]
    else:
        # Improved handling of overlapping segments
        old_text = " ".join(manager.current_sentence)

        # Check for overlapping content
        if sentence.startswith(old_text) or old_text.startswith(sentence):
            # Use the longer text
            if len(sentence) > len(old_text):
                manager.current_sentence = [sentence]
            # Otherwise keep the current sentence
        else:
            # Check for partial overlap
            overlap = find_overlap(old_text, sentence)
            if overlap and len(overlap) > 3:  # Significant overlap
                # Merge the texts
                merged = old_text + sentence[len(overlap) :]
                manager.current_sentence = [merged]
            else:
                # No significant overlap, just append
                manager.current_sentence.append(sentence)
