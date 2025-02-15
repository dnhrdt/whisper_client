"""
Hilfsskript zum Aktualisieren des Testfortschritts
"""
import json
from datetime import datetime
import sys
from pathlib import Path

def load_progress():
    """Lädt den aktuellen Testfortschritt"""
    try:
        with open("tests/speech_test_progress.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Fortschrittsdatei nicht gefunden!")
        sys.exit(1)

def save_progress(data):
    """Speichert den aktualisierten Testfortschritt"""
    data["meta"]["last_updated"] = datetime.now().isoformat()
    with open("tests/speech_test_progress.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def update_test_result(stage_id, test_id, success, notes):
    """Aktualisiert das Ergebnis eines Tests"""
    data = load_progress()
    
    # Finde Stage und Test
    stage = next((s for s in data["test_stages"] if s["id"] == stage_id), None)
    if not stage:
        print(f"❌ Stage {stage_id} nicht gefunden!")
        return
    
    test = next((t for t in stage["test_cases"] if t["id"] == test_id), None)
    if not test:
        print(f"❌ Test {test_id} nicht gefunden!")
        return
    
    # Füge Ergebnis hinzu
    result = {
        "timestamp": datetime.now().isoformat(),
        "success": success,
        "notes": notes
    }
    test["results"].append(result)
    test["status"] = "passed" if success else "failed"
    
    # Aktualisiere Stage-Status
    if all(t["status"] == "passed" for t in stage["test_cases"]):
        stage["status"] = "completed"
        # Setze nächste Stage auf "in_progress"
        next_stage = next((s for s in data["test_stages"] if s["status"] == "pending"), None)
        if next_stage:
            next_stage["status"] = "in_progress"
            data["meta"]["current_stage"] = next_stage["id"]
            data["meta"]["current_test"] = next_stage["test_cases"][0]["id"]
    
    # Speichern
    save_progress(data)
    
    # Status ausgeben
    print(f"\n📝 Test {test_id} aktualisiert:")
    print(f"Status: {'✅ Erfolgreich' if success else '❌ Fehlgeschlagen'}")
    print(f"Notizen: {notes}")
    
    if stage["status"] == "completed":
        print(f"\n🎉 Stage {stage_id} abgeschlossen!")
        if next_stage:
            print(f"Nächste Stage: {next_stage['id']} - {next_stage['name']}")

def show_current_test():
    """Zeigt den aktuellen Teststatus"""
    data = load_progress()
    current_stage = next((s for s in data["test_stages"] if s["status"] == "in_progress"), None)
    
    if not current_stage:
        print("✅ Alle Tests abgeschlossen!")
        return
    
    current_test = next((t for t in current_stage["test_cases"] if t["status"] == "pending"), None)
    if not current_test:
        print(f"✅ Stage {current_stage['id']} abgeschlossen!")
        return
    
    print("\n🎯 Aktueller Test:")
    print("=" * 50)
    print(f"Stage {current_stage['id']}: {current_stage['name']}")
    print(f"Test {current_test['id']}: {current_test['description']}")
    print(f"\nBeispiel: {current_test['example']}")
    print("\nErwartete Ergebnisse:")
    for exp in current_test['expected']:
        print(f"• {exp}")
    print("\nBisherige Ergebnisse:")
    for result in current_test['results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['timestamp']}: {result['notes']}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        show_current_test()
    elif len(sys.argv) == 4:
        stage_id = int(sys.argv[1])
        test_id = sys.argv[2]
        success = sys.argv[3].lower() == "true"
        notes = input("Notizen zum Testergebnis: ")
        update_test_result(stage_id, test_id, success, notes)
    else:
        print("Verwendung:")
        print("python update_test_progress.py                    # Zeigt aktuellen Test")
        print("python update_test_progress.py 1 1.1 true/false  # Aktualisiert Testergebnis")
