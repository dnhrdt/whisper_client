"""
Audio Package for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 13:16 CET

This package provides audio recording, processing, and resampling functionality
for the Whisper Client. It includes classes and functions for microphone access,
audio capture, and conversion to the format required by the WhisperLive server.

The package now includes a Tumbling Window implementation for improved audio processing
with overlapping windows and better transitions between audio segments.
"""

from .device import check_device_availability, list_audio_devices, test_microphone_access
from .manager import AudioManager
from .processor import AudioProcessor

# Importiere alle Module und Funktionen, die exportiert werden sollen
from .resampling import normalize_audio, resample_to_16kHZ
from .window import TumblingWindow

# Definiere, welche Symbole bei "from audio import *" importiert werden
__all__ = [
    "resample_to_16kHZ",
    "normalize_audio",
    "TumblingWindow",
    "AudioProcessor",
    "AudioManager",
    "list_audio_devices",
    "check_device_availability",
    "test_microphone_access",
]
