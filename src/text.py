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
from text import TextManager
from text.segment import TextSegment
from text.buffer import TextBuffer
from text.output import send_message, set_clipboard_text, send_paste_command, send_text_to_prompt
from text.window import find_prompt_window, find_vscode_edit_control
from text.processing import is_sentence_end, format_sentence, find_overlap
from text.duplicate import is_duplicate, normalize_text
from text.sentence import output_sentence, should_force_output
from text.input_handler import process_segments
from text.test_handler import get_test_output

# Re-Export der öffentlichen API
__all__ = [
    "TextManager",
    "TextSegment",
    "TextBuffer",
    "send_message",
    "is_sentence_end",
    "format_sentence",
    "find_overlap"
]
