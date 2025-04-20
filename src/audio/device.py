"""
Audio Device Management Module for the Whisper Client
Version: 1.0
Timestamp: 2025-04-20 13:17 CET

This module provides functions for audio device detection and management.
"""

import pyaudio

from src import logger


def list_audio_devices():
    """
    Lists all available audio input devices.

    Returns:
        List of (index, name, channels) tuples for all input devices
    """
    audio = pyaudio.PyAudio()
    devices = []

    try:
        info = audio.get_host_api_info_by_index(0)
        num_devices = info.get("deviceCount", 0)

        for i in range(num_devices):
            device_info = audio.get_device_info_by_index(i)
            max_input_channels = device_info.get("maxInputChannels", 0)

            if max_input_channels > 0:
                # Correct Windows umlauts
                name_raw = device_info.get("name", "")
                name = (
                    name_raw.encode("latin-1").decode("utf-8")
                    if isinstance(name_raw, str)
                    else "Unknown Device"
                )
                devices.append((i, name, max_input_channels))

        return devices

    finally:
        audio.terminate()


def check_device_availability(audio, device_index):
    """
    Checks if a specific audio device is available.

    Args:
        audio: PyAudio instance
        device_index: Device index to check

    Returns:
        True if device is available, False otherwise
    """
    try:
        device_info = audio.get_device_info_by_index(device_index)
        max_channels = device_info.get("maxInputChannels")
        return isinstance(max_channels, int) and max_channels > 0
    except Exception as e:
        logger.debug("Error checking device availability: %s", e)
        return False


def test_microphone_access(audio, device_index, format, channels, rate, chunk):
    """
    Tests microphone access by opening a stream.

    Args:
        audio: PyAudio instance
        device_index: Device index to test
        format: Audio format (e.g., pyaudio.paInt16)
        channels: Number of channels
        rate: Sample rate
        chunk: Chunk size

    Returns:
        True if test successful, False otherwise
    """
    try:
        test_stream = audio.open(
            format=format,
            channels=channels,
            rate=rate,
            input=True,
            input_device_index=device_index,
            frames_per_buffer=chunk,
        )
        test_stream.close()
        logger.info("✓ Microphone test successful")
        return True
    except Exception as e:
        logger.error("⚠️ Microphone test failed: %s", e)
        return False
