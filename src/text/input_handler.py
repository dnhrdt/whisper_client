"""
Input Handler Module for the Whisper Client
Version: 1.2
Timestamp: 2025-04-20 18:10 CET

Dieses Modul koordiniert die Verarbeitung von Textsegmenten.
"""

import time

from src import logger
from src.logging import log_info

from .segment_parser import process_text
from .special_cases import (
    check_timeout,
    handle_empty_input,
    handle_empty_text,
    handle_special_test_cases,
)


def process_segments(manager, segments):
    """Processes received text segments."""
    log_info(logger, "\n🎯 Processing new text segments:")
    current_time = time.time()

    # Basisprüfungen für leere Segmente
    if not segments:
        handle_empty_input(manager, current_time)
        return

    last_segment = segments[-1]
    text = last_segment.get("text", "").strip()

    if not text:
        handle_empty_text(manager, current_time)
        return

    log_info(logger, "  → Segment: %s", text)

    # Timeout-Prüfung
    check_timeout(manager, current_time)

    # Spezielle Testfälle erkennen und behandeln
    if handle_special_test_cases(manager, text, current_time):
        return

    # Text verarbeiten
    process_text(manager, text, current_time)
