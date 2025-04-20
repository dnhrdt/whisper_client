"""
Audio Recording and Management Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:35 CET

This module handles audio recording and management for the Whisper Client.
It provides functionality for microphone access and audio capture.
"""

import threading
from typing import Callable, Optional

import numpy as np
import pyaudio

import config
from src import logger
from src.logging import log_debug, log_error, log_info, log_warning

from .device import check_device_availability, test_microphone_access
from .resampling import resample_to_16kHZ


class AudioManager:
    """
    Manages audio recording and device access.

    This class handles microphone initialization, audio recording,
    and provides the captured audio data to a callback function.
    """

    def __init__(self):
        """Initialize the audio manager."""
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.recording_lock = threading.Lock()
        self.record_thread: Optional[threading.Thread] = None

        # Load audio format from config
        self.chunk = config.AUDIO_CHUNK
        self.format = getattr(pyaudio, config.AUDIO_FORMAT)
        self.channels = config.AUDIO_CHANNELS
        self.rate = config.AUDIO_RATE
        self.device_index = config.AUDIO_DEVICE_INDEX

        # Initialize microphone
        self._init_microphone()

    def _init_microphone(self):
        """Initialize and test microphone access"""
        if not self._check_microphone():
            log_error(logger, "⚠️ Microphone not available!")
            raise RuntimeError("No microphone found")

        # Test microphone access
        if not test_microphone_access(
            self.audio, self.device_index, self.format, self.channels, self.rate, self.chunk
        ):
            raise RuntimeError("Microphone test failed")

    def _check_microphone(self):
        """Checks if the configured microphone is available"""
        try:
            info = self.audio.get_host_api_info_by_index(0)
            num_devices = info.get("deviceCount")  # Can be None or str

            # Ensure num_devices is an integer before comparison
            if isinstance(num_devices, int) and self.device_index < num_devices:
                device_info = self.audio.get_device_info_by_index(self.device_index)
                max_channels = device_info.get("maxInputChannels")  # Can be None or str

                # Ensure max_channels is an integer before comparison
                if isinstance(max_channels, int) and max_channels > 0:
                    # Correct Windows umlauts, ensure name is a string before encoding
                    name_raw = device_info.get("name", "")
                    name = (
                        name_raw.encode("latin-1").decode("utf-8")
                        if isinstance(name_raw, str)
                        else "Unknown Device"
                    )
                    log_info(logger, "✓ Microphone found: %s", name)
                    return True

            log_error(logger, "⚠️ Microphone not available")
            return False

        except Exception as e:
            log_error(logger, "⚠️ Error checking microphone: %s", e)
            return False

    def is_device_available(self):
        """Checks if the audio device is still available"""
        return check_device_availability(self.audio, self.device_index)

    def start_recording(self, callback: Callable[[bytes], None]):
        """
        Starts audio recording.

        Args:
            callback: Function to call with recorded audio data
        """
        with self.recording_lock:
            if self.recording:
                return

            # Check if microphone is still available
            if not self.is_device_available():
                log_warning(logger, "⚠️ Microphone no longer available")
                if not self._check_microphone():
                    log_error(logger, "⚠️ No microphone found!")
                    return

            try:
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.chunk,
                )
                self.recording = True
                log_info(logger, "🎤 Recording started...")

                # Start recording thread
                self.record_thread = threading.Thread(target=self._record_audio, args=(callback,))
                self.record_thread.daemon = True
                self.record_thread.start()

            except Exception as e:
                log_error(logger, "⚠️ Error starting recording: %s", e)
                self.recording = False

    def stop_recording(self):
        """Stops audio recording"""
        with self.recording_lock:
            if not self.recording:
                return

            log_debug(logger, "Stopping recording...")
            self.recording = False

            # Close stream immediately to prevent further data
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    log_debug(logger, "Audio stream closed")
                except Exception as e:
                    log_error(logger, "Error closing stream: %s", e)

            # Wait for audio thread with longer timeout
            # Check if record_thread exists and is not None before accessing attributes
            if hasattr(self, "record_thread") and self.record_thread is not None:
                if self.record_thread.is_alive():
                    log_debug(logger, "Waiting for audio thread...")
                    self.record_thread.join(timeout=config.AUDIO_THREAD_TIMEOUT)
                    if self.record_thread.is_alive():
                        # Break long line for flake8 E501
                        log_warning(
                            logger, "Audio thread not responding - will be terminated on exit"
                        )
                        # Don't set to None here, just let the daemon thread property handle termination

            log_info(logger, "\n⏹️ Recording stopped")

    def _record_audio(self, callback: Callable[[bytes], None]):
        """
        Record audio and send to callback.

        Args:
            callback: Function to call with recorded audio data
        """
        buffer = []  # Audio buffer for more stable transmission
        log_debug(logger, "Audio thread started")

        try:
            while self.recording and self.stream and self.stream.is_active():
                try:
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    # Convert to float32 array
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0

                    # Add normalized float32 data to buffer
                    buffer.append(audio_array)

                    # Check if enough audio is available for a buffer
                    buffer_size = int(config.AUDIO_BUFFER_SECONDS * 4)  # 4 chunks per second
                    if len(buffer) >= buffer_size:
                        combined_data = np.concatenate(buffer)

                        # Resample to 16kHz
                        resampled_data = resample_to_16kHZ(combined_data.tobytes(), self.rate)
                        if self.recording:  # Nochmal prüfen vor dem Senden
                            callback(resampled_data)
                        buffer = []  # Clear buffer

                except Exception as e:
                    log_error(logger, "Error during recording: %s", e)
                    break

        finally:
            # Send remaining buffer data
            if buffer:
                try:
                    combined_data = np.concatenate(buffer)
                    # Resample to 16kHz
                    resampled_data = resample_to_16kHZ(combined_data.tobytes(), self.rate)
                    callback(resampled_data)
                    log_debug(logger, "Last %d buffer chunks sent", len(buffer))
                except Exception as e:
                    log_error(logger, "Error sending last buffer data: %s", e)

            buffer = []
            log_debug(logger, "Audio thread terminated")
            self.recording = False

    def cleanup(self):
        """Release resources"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
