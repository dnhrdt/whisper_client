"""
Text Processing Package for the Whisper Client
Version: 1.2
Timestamp: 2025-04-20 14:00 CET

Dieses Paket stellt Textverarbeitungsfunktionalität für den Whisper Client bereit.
Es enthält Klassen und Funktionen für Textsegmentierung, Pufferung, Verarbeitung
und Ausgabe.
"""

from .manager import TextManager

# Öffentliche API
__all__ = ["TextManager"]
