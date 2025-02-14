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
    
    # Flag für Testabbruch
    test_running = True
    
    def stop_tests():
        nonlocal test_running
        test_running = False
        print("\nTests werden abgebrochen...")
    
    try:
        print("\nVorbereitung:")
        print("1. Stelle sicher, dass der WhisperLive Server läuft")
        print("2. Halte den Text aus Speech Test 1.2 bereit")
        print("3. F13 wird für Start/Stopp der Aufnahme verwendet")
        print("4. F14 zum Abbrechen der Tests")
        print("5. Timeout nach 120 Sekunden")
        input("\nDrücke Enter wenn bereit...")
        
        # Hotkey-Handler registrieren
        def register_recording_handler(toggle_recording):
            hotkey_manager.register_hotkey(config.HOTKEY_TOGGLE_RECORDING, toggle_recording)
        
        # F14 für Testabbruch registrieren
        hotkey_manager.register_hotkey(config.HOTKEY_EXIT, stop_tests)
        
        # Timer für Timeout starten
        start_time = time.time()
        
        while test_running and time.time() - start_time < config.TEST_SUITE_TIMEOUT:
            try:
                # Test-Suite mit Handler-Registrierung starten
                run_test_suite(register_recording_handler)
                break  # Tests erfolgreich beendet
            except Exception as e:
                print(f"\nFehler während der Tests: {e}")
                break
        
        if time.time() - start_time >= config.TEST_SUITE_TIMEOUT:
            print(f"\nTimeout nach {config.TEST_SUITE_TIMEOUT} Sekunden")
        
    except KeyboardInterrupt:
        print("\nTests abgebrochen")
    finally:
        hotkey_manager.stop()
        print("\nTests beendet")

if __name__ == "__main__":
    main()
