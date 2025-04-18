"""
Test-Runner für Timing-Tests mit verschiedenen Konfigurationen
"""

import json
import time
from pathlib import Path

import config
from tests.timing_tests import TimingTest, test_complete_text_capture, test_quick_stop_handling

# Test-Konfigurationen
TIMING_CONFIGS = [
    {"name": "default", "description": "Standard-Konfiguration", "config": {}},  # Keine Änderungen
    {
        "name": "fast_response",
        "description": "Schnelle Reaktionszeit, höhere CPU-Last",
        "config": {"BASE_DELAY": 0.05, "BASE_WAIT": 0.5, "AUDIO_BUFFER_SECONDS": 0.5},
    },
    {
        "name": "stable_streaming",
        "description": "Stabilere Übertragung, höhere Latenz",
        "config": {"BASE_DELAY": 0.2, "BASE_WAIT": 2.0, "AUDIO_BUFFER_SECONDS": 2.0},
    },
    {
        "name": "quick_stop",
        "description": "Optimiert für schnelles Stoppen",
        "config": {"WS_FINAL_WAIT": 10.0, "WS_MESSAGE_WAIT": 0.5, "BASE_WAIT": 0.5},
    },
]


def backup_config():
    """Aktuelle Konfiguration sichern"""
    backup = {}
    for config_name in TIMING_CONFIGS[1]["config"].keys():
        backup[config_name] = getattr(config, config_name)
    return backup


def restore_config(backup):
    """Konfiguration wiederherstellen"""
    for name, value in backup.items():
        setattr(config, name, value)


def apply_config(test_config):
    """Test-Konfiguration anwenden"""
    for name, value in test_config.items():
        setattr(config, name, value)


def run_test_suite(register_recording_handler):
    """Führt alle Tests mit verschiedenen Konfigurationen aus"""
    results_dir = Path("tests/results")
    results_dir.mkdir(exist_ok=True)

    # Aktuelle Konfiguration sichern
    config_backup = backup_config()

    try:
        for timing_config in TIMING_CONFIGS:
            print(f"\n=== Test-Suite mit {timing_config['name']} ===")
            print(f"Beschreibung: {timing_config['description']}")

            # Konfiguration anwenden
            apply_config(timing_config["config"])

            # Aktuelle Konfiguration loggen
            config_file = results_dir / f"config_{timing_config['name']}_{int(time.time())}.json"
            with open(config_file, "w", encoding="utf-8") as f:
                json.dump(
                    {
                        "name": timing_config["name"],
                        "description": timing_config["description"],
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "config": timing_config["config"],
                    },
                    f,
                    indent=2,
                )

            print("\nStarte Tests...")

            try:
                # Vollständigkeitstest
                print("\n1. Vollständige Texterfassung")
                test = TimingTest()
                test.ws.set_text_callback(test.on_text_received)

                # F13 Handler für Aufnahmesteuerung
                recording = False

                def toggle_recording():
                    nonlocal recording
                    if not recording:
                        test.ws.start_processing()
                        test.audio.start_recording(test.ws.send_audio)
                        recording = True
                    else:
                        test.audio.stop_recording()
                        test.ws.stop_processing()
                        recording = False

                # Handler registrieren
                register_recording_handler(toggle_recording)

                # Test durchführen
                test_complete_text_capture()

                # Warte zwischen Tests
                time.sleep(5)

                # Schnellstop-Test
                print("\n2. Schnellstop-Handling")
                test = TimingTest()
                test.ws.set_text_callback(test.on_text_received)

                # F13 Handler für Aufnahmesteuerung
                recording = False

                def toggle_recording():
                    nonlocal recording
                    if not recording:
                        test.ws.start_processing()
                        test.audio.start_recording(test.ws.send_audio)
                        recording = True
                    else:
                        test.audio.stop_recording()
                        test.ws.stop_processing()
                        recording = False

                # Handler registrieren
                register_recording_handler(toggle_recording)

                # Test durchführen
                test_quick_stop_handling()

            except Exception as e:
                print(f"Fehler während der Tests: {e}")

            print(f"\n=== Ende der Test-Suite {timing_config['name']} ===")

            # Warte zwischen Konfigurationen
            time.sleep(10)

    finally:
        # Ursprüngliche Konfiguration wiederherstellen
        restore_config(config_backup)


if __name__ == "__main__":
    print("=== Timing-Test-Runner ===")
    print(f"Starte Tests mit {len(TIMING_CONFIGS)} verschiedenen Konfigurationen")

    # Dummy-Handler für direkten Start
    def register_recording_handler(toggle_recording):
        pass

    run_test_suite(register_recording_handler)
