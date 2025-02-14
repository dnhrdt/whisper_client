"""
Hauptprogramm für Timing-Tests
"""
import sys
import time
from pathlib import Path

# Füge Projektverzeichnis zum Python-Path hinzu
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from src.hotkeys import HotkeyManager
from tests.timing_tests import test_complete_text_capture, test_quick_stop_handling
from tests.run_timing_tests import run_test_suite

def main():
    print("=== Whisper Client Timing Tests ===")
    
    # Hotkey-Manager initialisieren
    hotkey_manager = HotkeyManager()
    hotkey_manager.start()
    
    try:
        print("\nVorbereitung:")
        print("1. Stelle sicher, dass der WhisperLive Server läuft")
        print("2. Halte den Text aus Speech Test 1.2 bereit")
        print("3. F13 wird für Start/Stopp der Aufnahme verwendet")
        input("\nDrücke Enter wenn bereit...")
        
        print("\nStarte Test-Suite...")
        run_test_suite()
        
    except KeyboardInterrupt:
        print("\nTests abgebrochen")
    finally:
        hotkey_manager.stop()
        print("\nTests beendet")

if __name__ == "__main__":
    main()
