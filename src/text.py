"""
Text Processing Module for the Whisper Client
Version: 1.8
Timestamp: 2025-04-20 14:30 CET

This module handles text processing, formatting, and output for the Whisper Client.
It includes functionality for sentence detection, duplicate handling, and text insertion
using various methods including Windows SendMessage API.

REFACTORING NOTICE: Diese Datei wurde in mehrere Module aufgeteilt.
Diese Version dient als Fassade für die neue Modulstruktur.
Siehe docs/refactoring.md für den vollständigen Plan.

Neue Struktur:
- text/segment.py: TextSegment Dataclass
- text/buffer.py: TextBuffer-Klasse und Speicherverwaltung
- text/processing.py: Satzverarbeitung und Formatierung
- text/output.py: Text-Ausgabemethoden
- text/window.py: Fenstererkennung und -manipulation
- text/__init__.py: API und Hauptklasse
"""

# Imports aus den neuen Modulen
from src.text import TextManager
from src.text.buffer import TextBuffer
from src.text.duplicate import is_duplicate, normalize_text
from src.text.input_handler import process_segments
from src.text.output import (
    send_message,
    send_paste_command,
    send_text_to_prompt,
    set_clipboard_text,
)
from src.text.processing import find_overlap, format_sentence, is_sentence_end
from src.text.segment import TextSegment
from src.text.sentence import output_sentence, should_force_output
from src.text.test_handler import get_test_output
from src.text.window import find_prompt_window, find_vscode_edit_control

# Re-Export der öffentlichen API
__all__ = [
    "TextManager",
    "TextSegment",
    "TextBuffer",
    "send_message",
    "is_sentence_end",
    "format_sentence",
    "find_overlap",
]
