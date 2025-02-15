"""
Proof of Concept: Tumbling Window für Audio-Verarbeitung
"""
import numpy as np
from queue import Queue
from threading import Event
import time

class TumblingWindow:
    def __init__(self, window_size=4096, overlap=0.5):
        """
        window_size: Größe des Fensters in Samples
        overlap: Überlappung zwischen Fenstern (0.0 - 1.0)
        """
        self.window_size = window_size
        self.overlap = max(0.0, min(1.0, overlap))
        self.overlap_size = int(window_size * overlap)
        self.buffer = []
        self.previous_window = None
        
    def add_chunk(self, chunk):
        """Fügt einen Audio-Chunk zum Buffer hinzu"""
        # Konvertiere bytes zu numpy array wenn nötig
        if isinstance(chunk, bytes):
            chunk = np.frombuffer(chunk, dtype=np.int16)
        self.buffer.extend(chunk)
        
    def get_windows(self):
        """Generator für verfügbare Fenster"""
        while len(self.buffer) >= self.window_size:
            # Extrahiere ein komplettes Fenster
            window = np.array(self.buffer[:self.window_size])
            
            # Überlappung mit vorherigem Fenster wenn vorhanden
            if self.previous_window is not None and self.overlap > 0:
                # Lineare Überblendung im Überlappungsbereich
                fade_out = np.linspace(1, 0, self.overlap_size)
                fade_in = np.linspace(0, 1, self.overlap_size)
                
                overlap_region = self.previous_window[-self.overlap_size:]
                current_overlap = window[:self.overlap_size]
                
                blended = (overlap_region * fade_out) + (current_overlap * fade_in)
                window[:self.overlap_size] = blended
            
            yield window
            
            # Aktualisiere Buffer und vorheriges Fenster
            self.buffer = self.buffer[self.window_size - self.overlap_size:]
            self.previous_window = window

def test_basic_windowing():
    """Test grundlegende Fensterung"""
    window = TumblingWindow(window_size=1000, overlap=0.2)
    
    # Simuliere Audio-Chunks (Sinuswelle)
    sample_rate = 16000
    duration = 1.0  # Sekunden
    t = np.linspace(0, duration, int(sample_rate * duration))
    audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz Ton
    audio = (audio * 32767).astype(np.int16)  # Konvertiere zu int16
    
    # Teile in Chunks
    chunk_size = 100
    chunks = [audio[i:i+chunk_size] for i in range(0, len(audio), chunk_size)]
    
    # Verarbeite Chunks
    processed_windows = []
    for chunk in chunks:
        window.add_chunk(chunk)
        for w in window.get_windows():
            processed_windows.append(w)
    
    # Prüfe Ergebnisse
    assert len(processed_windows) > 0, "Keine Fenster erzeugt"
    assert all(len(w) == 1000 for w in processed_windows), "Falsche Fenstergröße"
    print(f"Erfolgreich {len(processed_windows)} Fenster verarbeitet")

def test_realtime_simulation():
    """Simuliert Echtzeit-Verarbeitung"""
    window = TumblingWindow(window_size=2048, overlap=0.25)
    audio_queue = Queue()
    stop_event = Event()
    
    def audio_producer():
        """Simuliert Audio-Eingabe"""
        sample_rate = 16000
        chunk_size = 512
        duration = 3.0  # Sekunden
        
        t = np.linspace(0, duration, int(sample_rate * duration))
        audio = np.sin(2 * np.pi * 440 * t)  # 440 Hz Ton
        audio = (audio * 32767).astype(np.int16)
        
        chunks = [audio[i:i+chunk_size] for i in range(0, len(audio), chunk_size)]
        
        for chunk in chunks:
            if stop_event.is_set():
                break
            audio_queue.put(chunk)
            time.sleep(chunk_size / sample_rate)  # Simuliere Echtzeit
    
    def audio_consumer():
        """Verarbeitet Audio-Fenster"""
        windows_processed = 0
        start_time = time.time()
        
        while not stop_event.is_set() or not audio_queue.empty():
            if not audio_queue.empty():
                chunk = audio_queue.get()
                window.add_chunk(chunk)
                
                for w in window.get_windows():
                    windows_processed += 1
                    # Hier würde normalerweise die Whisper-Verarbeitung stattfinden
                    
        duration = time.time() - start_time
        print(f"Verarbeitet: {windows_processed} Fenster in {duration:.2f} Sekunden")
        print(f"Durchschnittliche Latenz pro Fenster: {(duration/windows_processed*1000):.2f}ms")

    import threading
    producer = threading.Thread(target=audio_producer)
    consumer = threading.Thread(target=audio_consumer)
    
    producer.start()
    consumer.start()
    
    time.sleep(3.5)  # Lasse Test für 3.5 Sekunden laufen
    stop_event.set()
    
    producer.join()
    consumer.join()

if __name__ == "__main__":
    print("Test 1: Basis-Fensterung")
    test_basic_windowing()
    print("\nTest 2: Echtzeit-Simulation")
    test_realtime_simulation()
