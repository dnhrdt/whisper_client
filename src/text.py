"""
Text Processing Module for the Whisper Client
Version: 2.1
Timestamp: 2025-04-20 18:22 CET

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

# Direkte Importe aus den Untermodulen
from importlib import import_module

# Dynamische Importe, um zirkuläre Abhängigkeiten zu vermeiden
_text_buffer = import_module("src.text.buffer")
_text_manager = import_module("src.text.manager")
_text_output = import_module("src.text.output")
_text_processing = import_module("src.text.processing")
_text_segment = import_module("src.text.segment")

# Klassen und Funktionen aus den Modulen extrahieren
TextBuffer = _text_buffer.TextBuffer
TextManager = _text_manager.TextManager
send_message = _text_output.send_message
find_overlap = _text_processing.find_overlap
format_sentence = _text_processing.format_sentence
is_sentence_end = _text_processing.is_sentence_end
TextSegment = _text_segment.TextSegment

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
