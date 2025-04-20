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

# Importiere alle Module und Funktionen, die exportiert werden sollen
from audio.resampling import resample_to_16kHZ, normalize_audio
from audio.window import TumblingWindow
from audio.processor import AudioProcessor
from audio.manager import AudioManager
from audio.device import list_audio_devices, check_device_availability, test_microphone_access

# Definiere, welche Symbole bei "from audio import *" importiert werden
__all__ = [
    'resample_to_16kHZ',
    'normalize_audio',
    'TumblingWindow',
    'AudioProcessor',
    'AudioManager',
    'list_audio_devices',
    'check_device_availability',
    'test_microphone_access',
]
