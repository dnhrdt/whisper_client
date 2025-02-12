"""
Testskript für die Textverarbeitung
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
# Setze Log-Level für Tests
config.LOG_LEVEL_CONSOLE = "DEBUG"

def simulate_segments(manager, segments, reset=True):
    """Simuliert eingehende Textsegmente"""
    if reset:
        manager.recent_transcriptions = []
        manager.current_sentence = []
        manager.last_output_time = 0
        manager.incomplete_sentence_time = 0
    
    for segment in segments:
        print(f"Eingabe: {segment}")
        manager.process_segments([{"text": segment}])
        time.sleep(0.2)  # Kleine Pause zwischen Segmenten

def run_tests():
    print("\n🧪 Starte Textverarbeitungs-Tests...")
    print("=" * 50 + "\n")
    
    # TextManager initialisieren
    manager = TextManager()
    
    print("\nTest 1: Normale Satzverarbeitung")
    print("-" * 30)
    segments = [
        "Dies ist ein",
        " Test für die",
        " normale Satzverarbeitung."
    ]
    simulate_segments(manager, segments)
    print("\n")
    
    print("\nTest 2: Deduplizierung")
    print("-" * 30)
    segments = [
        "Dies ist ein Text",
        "ist ein Text",  # Sollte als Duplikat erkannt werden
        " der Duplikate enthält.",
        "der Duplikate"  # Sollte als Duplikat erkannt werden
    ]
    simulate_segments(manager, segments)
    print("\n")
    
    print("\nTest 3: Abkürzungen")
    print("-" * 30)
    segments = [
        "Dr. Müller ist",
        " Prof. an der Uni",
        " in Berlin."
    ]
    simulate_segments(manager, segments)
    print("\n")
    
    print("\nTest 4: Unvollständige Sätze")
    print("-" * 30)
    segments = [
        "Dies ist ein unvollständiger"
    ]
    simulate_segments(manager, segments)
    print(f"Warte {config.MAX_SENTENCE_WAIT + 0.5} Sekunden auf Timeout...")
    time.sleep(config.MAX_SENTENCE_WAIT + 0.5)
    # Trigger die Verarbeitung erneut um den Timeout zu prüfen
    manager.process_segments([{"text": " "}])
    print("\n")
    
    print("\nTest 5: Satzzeichen und Formatierung")
    print("-" * 30)
    segments = [
        "hier kommt ein satz",
        " mit verschiedenen satzzeichen!",
        " und noch einer?",
        " und der letzte..."
    ]
    simulate_segments(manager, segments)
    print("\n")
    
    print("✅ Tests abgeschlossen!")

if __name__ == "__main__":
    # Deaktiviere tatsächliches Einfügen für Tests
    TextManager.insert_text = lambda self, text: print(f"Ausgabe: {text}")
    run_tests()
