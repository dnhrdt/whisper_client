"""
Audio-Verarbeitungsmodul für den Whisper-Client
"""
import pyaudio
import numpy as np
import threading
import config
from src import logging

logger = logging.get_logger()

class AudioManager:
    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.recording = False
        self.recording_lock = threading.Lock()
        
        # Audio-Format aus Config laden
        self.chunk = config.AUDIO_CHUNK
        self.format = getattr(pyaudio, config.AUDIO_FORMAT)
        self.channels = config.AUDIO_CHANNELS
        self.rate = config.AUDIO_RATE
        self.device_index = config.AUDIO_DEVICE_INDEX
        
        # Mikrofon initialisieren
        self._init_microphone()
    
    def _init_microphone(self):
        """Mikrofonzugriff initialisieren und testen"""
        if not self._check_microphone():
            logger.error("⚠️ Mikrofon nicht verfügbar!")
            raise RuntimeError("Kein Mikrofon gefunden")
            
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
            logger.info("✓ Mikrofontest erfolgreich")
        except Exception as e:
            logger.error(f"⚠️ Mikrofontest fehlgeschlagen: {e}")
            raise
    
    def _check_microphone(self):
        """Prüft ob das konfigurierte Mikrofon verfügbar ist"""
        try:
            info = self.audio.get_host_api_info_by_index(0)
            num_devices = info.get('deviceCount')
            
            if self.device_index < num_devices:
                device_info = self.audio.get_device_info_by_index(self.device_index)
                if device_info.get('maxInputChannels') > 0:
                    # Korrigiere Windows-Umlaute
                    name = device_info.get('name', '').encode('latin-1').decode('utf-8')
                    logger.info(f"✓ Mikrofon gefunden: {name}")
                    return True
            
            logger.error("⚠️ Mikrofon nicht verfügbar")
            return False
            
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Mikrofonprüfung: {e}")
            return False
    
    def is_device_available(self):
        """Prüft ob das Audiogerät noch verfügbar ist"""
        try:
            device_info = self.audio.get_device_info_by_index(self.device_index)
            return device_info.get('maxInputChannels') > 0
        except:
            return False
    
    def start_recording(self, callback):
        """Startet die Audio-Aufnahme"""
        with self.recording_lock:
            if self.recording:
                return
            
            # Prüfe ob Mikrofon noch verfügbar
            if not self.is_device_available():
                logger.warning("⚠️ Mikrofon nicht mehr verfügbar")
                if not self._check_microphone():
                    logger.error("⚠️ Kein Mikrofon gefunden!")
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
                logger.info("🎤 Aufnahme gestartet...")
                
                # Aufnahme-Thread starten
                self.record_thread = threading.Thread(
                    target=self._record_audio,
                    args=(callback,)
                )
                self.record_thread.daemon = True
                self.record_thread.start()
                
            except Exception as e:
                logger.error(f"⚠️ Fehler beim Starten der Aufnahme: {e}")
                self.recording = False
    
    def stop_recording(self):
        """Stoppt die Audio-Aufnahme"""
        with self.recording_lock:
            if not self.recording:
                return
            
            logger.debug("Stoppe Aufnahme...")
            self.recording = False
            
            # Warte auf Audio-Thread
            if hasattr(self, 'record_thread') and self.record_thread.is_alive():
                logger.debug("Warte auf Audio-Thread...")
                self.record_thread.join(timeout=1.0)
                if self.record_thread.is_alive():
                    logger.warning("Audio-Thread reagiert nicht!")
            
            # Stream schließen
            if self.stream:
                try:
                    self.stream.stop_stream()
                    self.stream.close()
                    self.stream = None
                    logger.debug("Audio-Stream geschlossen")
                except Exception as e:
                    logger.error(f"Fehler beim Schließen des Streams: {e}")
            
            logger.info("\n⏹️ Aufnahme gestoppt")
    
    def _record_audio(self, callback):
        """Audio aufnehmen und an Callback senden"""
        buffer = []  # Audio-Puffer für stabilere Übertragung
        logger.debug("Audio-Thread gestartet")
        
        try:
            while self.recording:
                try:
                    # Prüfe ob Stream noch aktiv
                    if not self.stream or not self.stream.is_active():
                        logger.error("Audio-Stream nicht aktiv!")
                        break
                    
                    data = self.stream.read(self.chunk, exception_on_overflow=False)
                    # Konvertiere zu float32 Array
                    audio_array = np.frombuffer(data, dtype=np.int16).astype(np.float32) / 32768.0
                    
                    # Füge Daten zum Puffer hinzu
                    buffer.append(audio_array)
                    
                    # Sende gepufferte Daten wenn genug vorhanden
                    if len(buffer) >= 4:  # ca. 1 Sekunde Audio
                        combined_array = np.concatenate(buffer)
                        callback(combined_array.tobytes())
                        buffer = []  # Puffer leeren
                        
                except Exception as e:
                    logger.error(f"⚠️ Fehler bei der Aufnahme: {e}")
                    break
                    
        finally:
            logger.debug("Audio-Thread beendet")
            # Stelle sicher, dass Aufnahme gestoppt wird
            self.recording = False
    
    def cleanup(self):
        """Ressourcen freigeben"""
        self.stop_recording()
        if self.audio:
            self.audio.terminate()
