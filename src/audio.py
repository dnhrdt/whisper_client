"""
Audio Processing Module for the Whisper Client
Version: 2.2
Timestamp: 2025-04-20 18:23 CET

This module handles audio recording, processing, and resampling for the Whisper Client.
It provides functionality for microphone access, audio capture, and conversion to the
format required by the WhisperLive server.

REFACTORING NOTICE: Diese Datei wurde in mehrere Module aufgeteilt.
Die aktuelle Version dient als Fassade für die neuen Module.

Neue Struktur:
- audio/resampling.py: Audio-Resampling und -Konvertierung
- audio/window.py: TumblingWindow-Klasse und Überlappungslogik
- audio/processor.py: AudioProcessor-Klasse und Thread-basierte Verarbeitung
- audio/manager.py: AudioManager-Klasse und Mikrofonverwaltung
- audio/device.py: Geräteerkennungs- und -verwaltungsfunktionen
- audio/__init__.py: API und Hauptklassen
"""

# Direkte Importe aus den Untermodulen
from importlib import import_module

import config

# Dynamische Importe, um zirkuläre Abhängigkeiten zu vermeiden
_audio_manager = import_module("src.audio.manager")
_audio_processor = import_module("src.audio.processor")
_audio_window = import_module("src.audio.window")
_audio_resampling = import_module("src.audio.resampling")

# Klassen und Funktionen aus den Modulen extrahieren
AudioManagerImpl = _audio_manager.AudioManager
AudioProcessorImpl = _audio_processor.AudioProcessor
TumblingWindowImpl = _audio_window.TumblingWindow
resample_impl = _audio_resampling.resample_to_16kHZ


# MOVED TO: audio/resampling.py
def resample_to_16kHZ(audio_data, current_rate):
    """Resamples audio data to 16kHz using librosa."""
    # Weiterleitung an die neue Implementierung
    return resample_impl(audio_data, current_rate)


# MOVED TO: audio/window.py
class TumblingWindow:
    """Implements a tumbling window approach for audio processing.

    This class manages audio data in windows with configurable size and
    overlap, providing a smooth transition between consecutive windows
    through linear crossfading in the overlap regions.

    """

    # Weiterleitung an die neue Implementierung
    def __init__(self, window_size=None, overlap=None):
        window_size = window_size or config.TUMBLING_WINDOW_SIZE
        overlap = overlap or config.TUMBLING_WINDOW_OVERLAP
        self._instance = TumblingWindowImpl(window_size, overlap)

    def __getattr__(self, name):
        # Leite alle Attributzugriffe an die Instanz weiter
        return getattr(self._instance, name)


# MOVED TO: audio/processor.py
class AudioProcessor:
    """Processes audio data using the tumbling window approach.

    This class integrates with the AudioManager to process audio chunks
    and prepare them for the WhisperLive server.

    """

    # Weiterleitung an die neue Implementierung
    def __init__(self, test_mode=False):
        self._instance = AudioProcessorImpl(test_mode)

    def __getattr__(self, name):
        # Leite alle Attributzugriffe an die Instanz weiter
        return getattr(self._instance, name)


# MOVED TO: audio/manager.py
class AudioManager:
    """Manages audio recording and device access.

    This class handles microphone initialization, audio recording, and
    provides the captured audio data to a callback function.

    """

    # Weiterleitung an die neue Implementierung
    def __init__(self):
        self._instance = AudioManagerImpl()

    def __getattr__(self, name):
        # Leite alle Attributzugriffe an die Instanz weiter
        return getattr(self._instance, name)
