"""
Test für die Ausgabe im Prompt-Fenster
"""
import sys
import time
from pathlib import Path

# Füge Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.text import TextManager
from src import logging
import config

# Logger für Tests konfigurieren
logger = logging.get_logger()
config.LOG_LEVEL_CONSOLE = "DEBUG"

def test_prompt_output():
    """Testet die Ausgabe im Prompt-Fenster"""
    print("\n🧪 Teste Prompt-Ausgabe...")
    print("=" * 50)
    
    # TextManager initialisieren
    manager = TextManager()
    
    # Originale insert_text Methode speichern
    original_insert = manager.insert_text
    output_history = []
    
    def mock_insert_text(self, text):
        """Mock für insert_text, der Ausgaben protokolliert"""
        output_history.append({
            'timestamp': time.time(),
            'text': text
        })
        print(f"\n[{len(output_history)}] Ausgabe:")
        print("-" * 20)
        print(text)
        print("-" * 20)
    
    # Mock-Funktion einsetzen
    TextManager.insert_text = mock_insert_text
    
    try:
        print("\nTest 1: Mehrere kurze Sätze")
        print("-" * 30)
        segments = [
            {"text": "Dies ist der erste Satz."},
            {"text": "Dies ist der zweite Satz."},
            {"text": "Und der dritte Satz."}
        ]
        
        for segment in segments:
            print(f"\nEingabe: {segment['text']}")
            manager.process_segments([segment])
            time.sleep(0.5)  # Pause zwischen Segmenten
        
        print("\nTest 2: Satz mit Pausen")
        print("-" * 30)
        segments = [
            {"text": "Dies ist ein Satz"},
            {"text": " mit einer Pause"},
            {"text": " dazwischen."}
        ]
        
        for segment in segments:
            print(f"\nEingabe: {segment['text']}")
            manager.process_segments([segment])
            time.sleep(1.0)  # Längere Pause
        
        # Analyse der Ausgaben
        print("\n📊 Analyse:")
        print("-" * 30)
        for i, output in enumerate(output_history, 1):
            if i > 1:
                time_diff = output['timestamp'] - output_history[i-2]['timestamp']
                print(f"\nZeit seit letzter Ausgabe: {time_diff:.2f}s")
            print(f"Ausgabe {i}: {output['text']}")
        
    finally:
        # Original-Methode wiederherstellen
        TextManager.insert_text = original_insert
    
    print("\n✅ Test abgeschlossen!")

if __name__ == "__main__":
    test_prompt_output()
