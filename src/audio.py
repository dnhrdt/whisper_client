"""
Audio Processing Module for the Whisper Client
Version: 1.0
Timestamp: 2025-02-27 17:12 CET

This module handles audio recording, processing, and resampling for the Whisper Client.
It provides functionality for microphone access, audio capture, and conversion to the
format required by the WhisperLive server.
"""
import pyaudio
import numpy as np
import threading
import config
import librosa
from src import logger

def resample_to_16kHZ(audio_data, current_rate):
    """Resamples audio data to 16kHz using librosa."""
    y = np.frombuffer(audio_data, dtype=np.float32)
    resampled_audio = librosa.resample(y, orig_sr=current_rate, target_sr=16000)
    return resampled_audio.tobytes()

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
