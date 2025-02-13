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
from src.websocket import WhisperWebSocket
import logging
import config

# Logger für Tests konfigurieren
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

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

def test_websocket_connection():
    """Testet die WebSocket-Verbindung mit Server-Ready-Check und END_OF_AUDIO Signal"""
    print("\n🔌 Teste WebSocket-Verbindung...")
    print("=" * 50)
    
    # WebSocket initialisieren
    ws = WhisperWebSocket()
    
    print("\n1️⃣ Verbindungsaufbau:")
    print("-" * 30)
    
    # Verbindung aufbauen
    try:
        connected = ws.connect()
        print(f"Verbindung erfolgreich: {connected}")
        print(f"Server bereit: {ws.is_ready()}")
        
        print("\n2️⃣ Audio-Übertragung:")
        print("-" * 30)
        
        # Teste Audio-Übertragung ohne Server-Ready
        ws.server_ready = False
        audio_sent = ws.send_audio(b"test_audio")
        print(f"Audio ohne Server-Ready gesendet: {audio_sent} (sollte False sein)")
        
        # Teste Audio-Übertragung mit Server-Ready
        ws.server_ready = True
        audio_sent = ws.send_audio(b"test_audio")
        print(f"Audio mit Server-Ready gesendet: {audio_sent}")
        
        print("\n3️⃣ END_OF_AUDIO Signal:")
        print("-" * 30)
        
        # Teste END_OF_AUDIO Signal
        signal_sent = ws.send_end_of_audio()
        print(f"END_OF_AUDIO Signal gesendet: {signal_sent}")
        
        print("\n4️⃣ Cleanup:")
        print("-" * 30)
        
        # Teste Cleanup
        ws.cleanup()
        print(f"Verbindung nach Cleanup: {ws.connected}")
        print(f"Server-Ready nach Cleanup: {ws.server_ready}")
        
    except Exception as e:
        print(f"⚠️ Test fehlgeschlagen: {e}")
        raise
    finally:
        if ws.connected:
            ws.cleanup()
    
    print("\n✅ Test abgeschlossen!")

if __name__ == "__main__":
    test_server_flow()
    test_websocket_connection()
