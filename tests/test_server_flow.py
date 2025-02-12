"""
Test für den Datenfluss vom Server zur Textverarbeitung
"""
import sys
import time
from pathlib import Path
import json

# Füge Projektverzeichnis zum Python-Pfad hinzu
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.text import TextManager
from src import logging
import config

# Logger für Tests konfigurieren
logger = logging.get_logger()
config.LOG_LEVEL_CONSOLE = "DEBUG"

def simulate_server_message():
    """Simuliert eine typische Server-Nachricht"""
    return {
        "segments": [
            {"text": "Dies ist ein Test."},
            {"text": "Noch ein Test."},
            {"text": "Und noch einer?"},
            {"text": "Ja!"},
            {"text": "Okay."}
        ]
    }

def test_server_flow():
    """Testet den Datenfluss vom Server zur Textverarbeitung"""
    print("\n🔍 Teste Server-Datenfluss...")
    print("=" * 50)
    
    # TextManager initialisieren
    manager = TextManager()
    
    # Server-Nachricht simulieren
    server_message = simulate_server_message()
    
    print("\n1️⃣ Server sendet JSON-Nachricht:")
    print("-" * 30)
    print(json.dumps(server_message, indent=2))
    
    print("\n2️⃣ WebSocket empfängt und loggt Segmente:")
    print("-" * 30)
    for segment in server_message["segments"]:
        print(f"  → {segment['text']}")
    
    print("\n3️⃣ Textverarbeitung verarbeitet Segmente:")
    print("-" * 30)
    
    # Originale insert_text Methode speichern
    original_insert = manager.insert_text
    output_history = []
    
    def mock_insert_text(self, text):
        """Mock für insert_text, der Ausgaben protokolliert"""
        output_history.append({
            'timestamp': time.time(),
            'text': text
        })
        print(f"Ausgabe: {text}")
    
    # Mock-Funktion einsetzen
    TextManager.insert_text = mock_insert_text
    
    try:
        # Segmente verarbeiten
        manager.process_segments(server_message["segments"])
        
        print("\n4️⃣ Analyse:")
        print("-" * 30)
        print(f"• Eingabe-Segmente: {len(server_message['segments'])}")
        print(f"• Ausgegebene Sätze: {len(output_history)}")
        print("\nZeitlicher Ablauf:")
        for i, output in enumerate(output_history, 1):
            if i > 1:
                time_diff = output['timestamp'] - output_history[i-2]['timestamp']
                print(f"\nZeit seit letzter Ausgabe: {time_diff:.2f}s")
            print(f"Satz {i}: {output['text']}")
        
    finally:
        # Original-Methode wiederherstellen
        TextManager.insert_text = original_insert
    
    print("\n✅ Test abgeschlossen!")

if __name__ == "__main__":
    test_server_flow()
