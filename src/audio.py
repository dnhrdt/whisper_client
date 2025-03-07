"""
Audio Processing Module for the Whisper Client
Version: 1.2
Timestamp: 2025-03-07 21:45 CET

This module handles audio recording, processing, and resampling for the Whisper Client.
It provides functionality for microphone access, audio capture, and conversion to the
format required by the WhisperLive server.

The module now includes a Tumbling Window implementation for improved audio processing
with overlapping windows and better transitions between audio segments.
"""
import pyaudio
import numpy as np
import threading
import time
from queue import Queue, Empty
from collections import deque
import config
import librosa
from src import logger

def resample_to_16kHZ(audio_data, current_rate):
    """Resamples audio data to 16kHz using librosa."""
    y = np.frombuffer(audio_data, dtype=np.float32)
    resampled_audio = librosa.resample(y, orig_sr=current_rate, target_sr=16000)
    return resampled_audio.tobytes()


class TumblingWindow:
    """
    Implements a tumbling window approach for audio processing.
    
    This class manages audio data in windows with configurable size and overlap,
    providing a smooth transition between consecutive windows through linear
    crossfading in the overlap regions.
    """
    
    def __init__(self, window_size=config.TUMBLING_WINDOW_SIZE, overlap=config.TUMBLING_WINDOW_OVERLAP):
        """
        Initialize the tumbling window processor.
        
        Args:
            window_size: Size of each window in samples
            overlap: Overlap between windows as a fraction (0.0 - 1.0)
        """
        self.window_size = window_size
        self.overlap = max(0.0, min(1.0, overlap))  # Ensure overlap is between 0 and 1
        self.overlap_size = int(window_size * overlap)
        self.buffer = []
        self.previous_window = None
        logger.debug(f"TumblingWindow initialized: size={window_size}, overlap={overlap:.2f}")
    
    def add_chunk(self, chunk):
        """
        Add an audio chunk to the buffer.
        
        Args:
            chunk: Audio data as bytes or numpy array
        """
        # Convert bytes to numpy array if needed
        if isinstance(chunk, bytes):
            chunk = np.frombuffer(chunk, dtype=np.int16)
        
        # Add chunk to buffer
        self.buffer.extend(chunk)
        logger.debug(f"Added chunk of {len(chunk)} samples, buffer now {len(self.buffer)} samples")
    
    def get_windows(self):
        """
        Generator that yields available windows from the buffer.
        
        Each window is a numpy array of samples with size equal to window_size.
        Windows are removed from the buffer as they are yielded, with overlap
        preserved for the next window.
        
        Yields:
            numpy.ndarray: Audio window of size window_size
        """
        while len(self.buffer) >= self.window_size:
            # Extract a complete window
            window = np.array(self.buffer[:self.window_size])
            
            # Apply crossfade with previous window if available
            if self.previous_window is not None and self.overlap > 0:
                # Create linear fade curves
                fade_out = np.linspace(1, 0, self.overlap_size)
                fade_in = np.linspace(0, 1, self.overlap_size)
                
                # Get overlap regions
                overlap_region = self.previous_window[-self.overlap_size:]
                current_overlap = window[:self.overlap_size]
                
                # Blend the overlap regions
                blended = (overlap_region * fade_out) + (current_overlap * fade_in)
                window[:self.overlap_size] = blended
                
                logger.debug(f"Applied crossfade of {self.overlap_size} samples")
            
            # Yield the processed window
            yield window
            
            # Update buffer and previous window
            # Remove window from buffer, keeping overlap for next window
            self.buffer = self.buffer[self.window_size - self.overlap_size:]
            self.previous_window = window
            
            logger.debug(f"Window processed, buffer now {len(self.buffer)} samples")
    
    def clear(self):
        """Clear the buffer and reset state."""
        self.buffer = []
        self.previous_window = None
        logger.debug("TumblingWindow buffer cleared")


class AudioProcessor:
    """
    Processes audio data using the tumbling window approach.
    
    This class integrates with the AudioManager to process audio chunks
    and prepare them for the WhisperLive server.
    """
    
    def __init__(self, test_mode=False):
        """
        Initialize the audio processor.
        
        Args:
            test_mode: If True, operates in test mode without sending data
        """
        self.tumbling_window = TumblingWindow()
        self.test_mode = test_mode
        self.processed_windows = []
        self.window_callback = None
        self.processing_lock = threading.Lock()
        self.processing_queue = Queue()
        self.processing_thread = None
        self.running = False
        logger.debug("AudioProcessor initialized")
    
    def start_processing(self, callback):
        """
        Start the audio processing thread.
        
        Args:
            callback: Function to call with processed audio windows
        """
        with self.processing_lock:
            if self.running:
                return
            
            self.window_callback = callback
            self.running = True
            
            # Start processing thread
            self.processing_thread = threading.Thread(
                target=self._process_queue
            )
            self.processing_thread.daemon = True
            self.processing_thread.start()
            
            logger.info("🔄 Audio processing started")
    
    def stop_processing(self):
        """Stop the audio processing thread."""
        with self.processing_lock:
            if not self.running:
                return
            
            self.running = False
            
            # Wait for processing thread to finish
            if self.processing_thread and self.processing_thread.is_alive():
                self.processing_thread.join(timeout=config.AUDIO_THREAD_TIMEOUT)
                if self.processing_thread.is_alive():
                    logger.warning("Processing thread not responding - will terminate")
            
            # Clear state
            self.tumbling_window.clear()
            self.processing_queue = Queue()
            
            logger.info("🛑 Audio processing stopped")
    
    def process_audio(self, audio_data):
        """
        Process audio data through the tumbling window.
        
        Args:
            audio_data: Audio data as bytes
        """
        # Add to processing queue
        self.processing_queue.put(audio_data)
        
        # If in test mode, process immediately
        if self.test_mode:
            self._process_audio_data(audio_data)
    
    def _process_queue(self):
        """Process audio data from the queue."""
        logger.debug("Processing thread started")
        
        try:
            while self.running:
                try:
                    # Get audio data from queue with timeout
                    try:
                        audio_data = self.processing_queue.get(timeout=0.1)
                        self._process_audio_data(audio_data)
                        self.processing_queue.task_done()
                    except Empty:
                        continue
                        
                except Exception as e:
                    logger.error(f"Error processing audio: {e}")
                    
        finally:
            logger.debug("Processing thread terminated")
    
    def _process_audio_data(self, audio_data):
        """
        Process a chunk of audio data.
        
        Args:
            audio_data: Audio data as bytes
        """
        # Add to tumbling window
        self.tumbling_window.add_chunk(audio_data)
        
        # Get windows and process
        windows = list(self.tumbling_window.get_windows())
        
        # In test mode, store windows
        if self.test_mode:
            self.processed_windows.extend(windows)
            return
        
        # Process each window
        for window in windows:
            # Convert to bytes
            window_bytes = window.tobytes()
            
            # Call callback with window
            if self.window_callback and self.running:
                self.window_callback(window_bytes)

class AudioManager:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.recording_lock = threading.Lock()
        
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
            logger.error("⚠️ Microphone not available!")
            raise RuntimeError("No microphone found")
            
        # Teste Mikrofonzugriff
        try:
            test_stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.rate,
                input=True,
                input_device_index=self.device_index,
                frames_per_buffer=self.chunk
            )
            test_stream.close()
            logger.info("✓ Microphone test successful")
        except Exception as e:
            logger.error(f"⚠️ Microphone test failed: {e}")
            raise
    
    def _check_microphone(self):
        """Checks if the configured microphone is available"""
        try:
            info = self.audio.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            if self.device_index < num_devices:
                device_info = self.audio.get_device_info_by_index(self.device_index)
                if device_info.get('maxInputChannels') > 0:
                    # Correct Windows umlauts
                    name = device_info.get('name', '').encode('latin-1').decode('utf-8')
                    logger.info(f"✓ Microphone found: {name}")
                    return True
            
            logger.error("⚠️ Microphone not available")
            return False
            
        except Exception as e:
            logger.error(f"⚠️ Error checking microphone: {e}")
            return False
    
    def is_device_available(self):
        """Checks if the audio device is still available"""
        try:
            device_info = self.audio.get_device_info_by_index(self.device_index)
            return device_info.get('maxInputChannels') > 0
        except:
            return False
    
    def start_recording(self, callback):
        """Starts audio recording"""
        with self.recording_lock:
            if self.recording:
                return
            
            # Check if microphone is still available
            if not self.is_device_available():
                logger.warning("⚠️ Microphone no longer available")
                if not self._check_microphone():
                    logger.error("⚠️ No microphone found!")
                    return
            
            try:
                self.stream = self.audio.open(
                    format=self.format,
                    channels=self.channels,
                    rate=self.rate,
                    input=True,
                    input_device_index=self.device_index,
                    frames_per_buffer=self.chunk
                )
                self.recording = True
                logger.info("🎤 Recording started...")
                
                # Start recording thread
                self.record_thread = threading.Thread(
                    target=self._record_audio,
                    args=(callback,)
                )
                self.record_thread.daemon = True
                self.record_thread.start()
                
            except Exception as e:
                logger.error(f"⚠️ Error starting recording: {e}")
                self.recording = False
    
    def stop_recording(self):
        """Stops audio recording"""
        with self.recording_lock:
            if not self.recording:
                return
            
            logger.debug("Stopping recording...")
            self.recording = False
            
            # Close stream immediately to prevent further data
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    logger.debug("Audio stream closed")
                except Exception as e:
                    logger.error(f"Error closing stream: {e}")
            
            # Wait for audio thread with longer timeout
            if hasattr(self, 'record_thread') and self.record_thread.is_alive():
                logger.debug("Waiting for audio thread...")
                self.record_thread.join(timeout=config.AUDIO_THREAD_TIMEOUT)
                if self.record_thread.is_alive():
                    logger.warning("Audio thread not responding - Terminating thread...")
                    # Thread marked as daemon, will be terminated when program ends
                    self.record_thread = None
            
            logger.info("\n⏹️ Recording stopped")
    
    def _record_audio(self, callback):
        """Record audio and send to callback"""
        buffer = []  # Audio buffer for more stable transmission
        logger.debug("Audio thread started")
        
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
                    logger.error(f"⚠️ Error during recording: {e}")
                    break
                    
        finally:
            # Send remaining buffer data
            if buffer:
                try:
                    combined_data = np.concatenate(buffer)
                    # Resample to 16kHz
                    resampled_data = resample_to_16kHZ(combined_data.tobytes(), self.rate)
                    callback(resampled_data)
                    logger.debug(f"Last {len(buffer)} buffer chunks sent")
                except Exception as e:
                    logger.error(f"Error sending last buffer data: {e}")
            
            buffer = []
            logger.debug("Audio thread terminated")
            self.recording = False
    
    def cleanup(self):
        """Release resources"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
