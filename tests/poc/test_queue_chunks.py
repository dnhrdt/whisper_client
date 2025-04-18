"""
Proof of Concept: Queue-basierte Chunk-Verwaltung
"""

import asyncio
import queue
import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional


@dataclass
class AudioChunk:
    """Repräsentiert einen Audio-Chunk mit Metadaten"""

    data: bytes
    timestamp: float
    sequence: int
    is_final: bool = False


class ChunkProcessor:
    def __init__(self, processing_callback: Optional[Callable] = None):
        self.chunk_queue = queue.Queue()
        self.processing = True
        self.sequence_counter = 0
        self.processing_callback = processing_callback
        self.processing_thread = None
        self._lock = threading.Lock()

    def start(self):
        """Startet den Verarbeitungs-Thread"""
        if self.processing_thread is None:
            self.processing = True
            self.processing_thread = threading.Thread(target=self._process_chunks)
            self.processing_thread.daemon = True
            self.processing_thread.start()

    def stop(self):
        """Stoppt die Verarbeitung sauber"""
        with self._lock:
            self.processing = False
        # Sende End-Marker
        self.add_chunk(b"", is_final=True)
        if self.processing_thread:
            self.processing_thread.join(timeout=2.0)

    def add_chunk(self, data: bytes, is_final: bool = False):
        """Fügt einen neuen Chunk zur Verarbeitung hinzu"""
        with self._lock:
            if not self.processing and not is_final:
                return

            chunk = AudioChunk(
                data=data, timestamp=time.time(), sequence=self.sequence_counter, is_final=is_final
            )
            self.sequence_counter += 1
            self.chunk_queue.put(chunk)

    def _process_chunks(self):
        """Verarbeitet Chunks aus der Queue"""
        while self.processing or not self.chunk_queue.empty():
            try:
                chunk = self.chunk_queue.get(timeout=0.1)

                if chunk.is_final:
                    print(f"Finaler Chunk empfangen (Sequenz: {chunk.sequence})")
                    break

                if self.processing_callback:
                    self.processing_callback(chunk)
                else:
                    # Standard-Verarbeitung
                    print(f"Chunk {chunk.sequence}: {len(chunk.data)} bytes")

                self.chunk_queue.task_done()

            except queue.Empty:
                continue
            except Exception as e:
                print(f"Fehler bei Chunk-Verarbeitung: {e}")

        print("Chunk-Verarbeitung beendet")


class AsyncChunkProcessor:
    """Asynchrone Version des ChunkProcessors"""

    def __init__(self):
        self.chunk_queue = asyncio.Queue()
        self.processing = True
        self.sequence_counter = 0

    async def start(self):
        """Startet die asynchrone Verarbeitung"""
        self.processing = True
        await self._process_chunks()

    async def stop(self):
        """Stoppt die Verarbeitung sauber"""
        self.processing = False
        await self.chunk_queue.put(AudioChunk(b"", time.time(), -1, is_final=True))

    async def add_chunk(self, data: bytes):
        """Fügt einen neuen Chunk zur Verarbeitung hinzu"""
        if not self.processing:
            return

        chunk = AudioChunk(data=data, timestamp=time.time(), sequence=self.sequence_counter)
        self.sequence_counter += 1
        await self.chunk_queue.put(chunk)

    async def _process_chunks(self):
        """Verarbeitet Chunks asynchron"""
        while self.processing:
            try:
                chunk = await self.chunk_queue.get()

                if chunk.is_final:
                    print(f"Finaler Chunk empfangen (Sequenz: {chunk.sequence})")
                    break

                # Simuliere Verarbeitung
                await asyncio.sleep(0.01)  # Realistische Verzögerung
                print(f"Async Chunk {chunk.sequence}: {len(chunk.data)} bytes")

                self.chunk_queue.task_done()

            except Exception as e:
                print(f"Fehler bei async Chunk-Verarbeitung: {e}")

        print("Async Chunk-Verarbeitung beendet")


def test_threaded_processor():
    """Test der Thread-basierten Implementierung"""
    print("\nTest 1: Thread-basierte Verarbeitung")
    processor = ChunkProcessor()
    processor.start()

    # Simuliere Audio-Chunks
    for i in range(5):
        processor.add_chunk(b"x" * 1024)  # 1KB dummy data
        time.sleep(0.1)  # Simuliere Aufnahme-Intervall

    processor.stop()
    print("Thread-Test abgeschlossen")


async def test_async_processor():
    """Test der Async-Implementierung"""
    print("\nTest 2: Async Verarbeitung")
    processor = AsyncChunkProcessor()

    # Start processor
    process_task = asyncio.create_task(processor.start())

    # Simuliere Audio-Chunks
    for i in range(5):
        await processor.add_chunk(b"x" * 1024)  # 1KB dummy data
        await asyncio.sleep(0.1)  # Simuliere Aufnahme-Intervall

    await processor.stop()
    await process_task
    print("Async-Test abgeschlossen")


def test_error_handling():
    """Test der Fehlerbehandlung"""
    print("\nTest 3: Fehlerbehandlung")

    def problematic_callback(chunk):
        if chunk.sequence == 2:
            raise Exception("Simulierter Fehler")
        print(f"Verarbeite Chunk {chunk.sequence}")

    processor = ChunkProcessor(processing_callback=problematic_callback)
    processor.start()

    for i in range(5):
        processor.add_chunk(b"test")
        time.sleep(0.1)

    processor.stop()
    print("Fehlerbehandlungs-Test abgeschlossen")


if __name__ == "__main__":
    # Thread-basierter Test
    test_threaded_processor()

    # Async Test
    asyncio.run(test_async_processor())

    # Fehlerbehandlungs-Test
    test_error_handling()
