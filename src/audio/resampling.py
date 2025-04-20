"""
Audio Resampling Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:38 CET

This module provides functions for audio resampling and conversion.
"""

import librosa
import numpy as np

from src import logger
from src.logging import log_warning


def resample_to_16kHZ(audio_data, current_rate):
    """Resamples audio data to 16kHz using librosa."""
    y = np.frombuffer(audio_data, dtype=np.float32)
    resampled_audio = librosa.resample(y, orig_sr=current_rate, target_sr=16000)
    return resampled_audio.tobytes()


def normalize_audio(audio_data, dtype=np.int16):
    """
    Normalizes audio data to float32 in range [-1.0, 1.0].

    Args:
        audio_data: Audio data as bytes or numpy array
        dtype: Original data type of the audio

    Returns:
        Normalized audio as float32 numpy array
    """
    if isinstance(audio_data, bytes):
        audio_array = np.frombuffer(audio_data, dtype=dtype)
    else:
        audio_array = audio_data

    # Normalize based on data type
    if dtype == np.int16:
        normalized = audio_array.astype(np.float32) / 32768.0
    elif dtype == np.int32:
        normalized = audio_array.astype(np.float32) / 2147483648.0
    elif dtype == np.float32:
        normalized = audio_array  # Already normalized
    else:
        log_warning(logger, "Unsupported audio dtype: %s, using default normalization", dtype)
        normalized = audio_array.astype(np.float32) / np.max(np.abs(audio_array))

    return normalized
