"""
Proof of Concept: Verbesserte Audio-Segmentierung
"""

import time
from dataclasses import dataclass
from typing import List, Optional

import numpy as np


@dataclass
class AudioSegment:
    """Repräsentiert ein Audio-Segment mit Metadaten"""

    data: np.ndarray
    start_time: float
    end_time: float
    energy: float
    is_speech: bool = False


class AudioSegmenter:
    def __init__(
        self,
        sample_rate: int = 16000,
        min_segment_duration: float = 0.5,
        energy_threshold: float = 0.1,
        padding_duration: float = 0.2,
    ):
        self.sample_rate = sample_rate
        self.min_samples = int(min_segment_duration * sample_rate)
        self.energy_threshold = energy_threshold
        self.padding_samples = int(padding_duration * sample_rate)

        self.current_segment: List[np.ndarray] = []
        self.segments: List[AudioSegment] = []
        self.start_time: Optional[float] = None

    def calculate_energy(self, audio_data: np.ndarray) -> float:
        """Berechnet die Energie eines Audio-Chunks"""
        return np.mean(np.abs(audio_data))

    def add_audio(self, audio_data: np.ndarray):
        """Fügt Audio-Daten zur Segmentierung hinzu"""
        if self.start_time is None:
            self.start_time = time.time()

        self.current_segment.append(audio_data)

        # Prüfe ob genug Daten für ein Segment
        total_samples = sum(len(chunk) for chunk in self.current_segment)
        if total_samples >= self.min_samples:
            self._process_segment()

    def _process_segment(self):
        """Verarbeitet das aktuelle Segment"""
        if not self.current_segment:
            return

        # Kombiniere Chunks
        combined_audio = np.concatenate(self.current_segment)

        # Berechne Energie
        energy = self.calculate_energy(combined_audio)

        # Erstelle Segment
        segment = AudioSegment(
            data=combined_audio,
            start_time=self.start_time,
            end_time=time.time(),
            energy=energy,
            is_speech=energy > self.energy_threshold,
        )

        # Füge Padding hinzu wenn nötig
        if segment.is_speech and self.segments:
            last_segment = self.segments[-1]
            gap_duration = segment.start_time - last_segment.end_time

            if gap_duration < (self.padding_samples / self.sample_rate):
                # Fülle Lücke mit Padding
                padding_samples = int(gap_duration * self.sample_rate)
                if padding_samples > 0:
                    padding = np.zeros(padding_samples)
                    segment.data = np.concatenate([padding, segment.data])
                    segment.start_time = last_segment.end_time

        self.segments.append(segment)

        # Reset für nächstes Segment
        self.current_segment = []
        self.start_time = None

    def get_segments(self, only_speech: bool = True) -> List[AudioSegment]:
        """Gibt alle verarbeiteten Segmente zurück"""
        if only_speech:
            return [s for s in self.segments if s.is_speech]
        return self.segments


def test_basic_segmentation():
    """Test grundlegende Segmentierung"""
    print("\nTest 1: Basis-Segmentierung")
    segmenter = AudioSegmenter(sample_rate=16000)

    # Generiere Test-Audio (Sinuswelle mit verschiedenen Amplituden)
    duration = 3.0  # Sekunden
    t = np.linspace(0, duration, int(16000 * duration))

    # Erstelle Audio mit abwechselnder Lautstärke
    audio = np.zeros_like(t)
    # Lauter Abschnitt
    audio[int(0.5 * 16000) : int(1.0 * 16000)] = (
        np.sin(2 * np.pi * 440 * t[int(0.5 * 16000) : int(1.0 * 16000)]) * 0.8
    )
    # Leiser Abschnitt
    audio[int(1.5 * 16000) : int(2.0 * 16000)] = (
        np.sin(2 * np.pi * 440 * t[int(1.5 * 16000) : int(2.0 * 16000)]) * 0.05
    )
    # Lauter Abschnitt
    audio[int(2.2 * 16000) : int(2.7 * 16000)] = (
        np.sin(2 * np.pi * 440 * t[int(2.2 * 16000) : int(2.7 * 16000)]) * 0.7
    )

    # Teile in Chunks und verarbeite
    chunk_size = 1600  # 100ms chunks
    for i in range(0, len(audio), chunk_size):
        chunk = audio[i : i + chunk_size]
        segmenter.add_audio(chunk)

    # Analysiere Ergebnisse
    speech_segments = segmenter.get_segments(only_speech=True)
    all_segments = segmenter.get_segments(only_speech=False)

    print(
        f"Gefunden: {len(speech_segments)} Sprach-Segmente von {len(all_segments)} Gesamt-Segmenten"
    )
    for i, segment in enumerate(speech_segments):
        duration = segment.end_time - segment.start_time
        print(f"Sprach-Segment {i+1}: Dauer={duration:.2f}s, Energie={segment.energy:.3f}")


def test_continuous_audio():
    """Test kontinuierliche Audio-Verarbeitung"""
    print("\nTest 2: Kontinuierliche Verarbeitung")
    segmenter = AudioSegmenter(
        sample_rate=16000, min_segment_duration=0.3, energy_threshold=0.08, padding_duration=0.1
    )

    # Simuliere kontinuierlichen Audio-Stream
    chunk_duration = 0.1  # 100ms chunks
    total_duration = 2.0  # 2 Sekunden
    sample_rate = 16000

    chunks_count = int(total_duration / chunk_duration)
    for i in range(chunks_count):
        # Generiere Chunk
        t = np.linspace(
            i * chunk_duration, (i + 1) * chunk_duration, int(sample_rate * chunk_duration)
        )

        # Amplitude variiert je nach Position
        if 0.5 <= i * chunk_duration <= 1.0 or 1.5 <= i * chunk_duration <= 1.8:
            amplitude = 0.8  # "Sprache"
        else:
            amplitude = 0.02  # "Stille"

        chunk = np.sin(2 * np.pi * 440 * t) * amplitude

        # Verarbeite Chunk
        segmenter.add_audio(chunk)
        time.sleep(0.02)  # Simuliere Echtzeit-Verarbeitung

    # Analysiere Ergebnisse
    segments = segmenter.get_segments(only_speech=True)
    print(f"Gefunden: {len(segments)} Sprach-Segmente")
    for i, segment in enumerate(segments):
        duration = segment.end_time - segment.start_time
        print(f"Segment {i+1}: Dauer={duration:.2f}s, Energie={segment.energy:.3f}")


if __name__ == "__main__":
    test_basic_segmentation()
    test_continuous_audio()
