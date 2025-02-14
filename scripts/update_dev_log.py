#!/usr/bin/env python3
"""
Git pre-commit Hook für automatische development_log.json Updates
"""
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

def get_commit_message() -> Optional[str]:
    """Liest die Commit-Message aus .git/COMMIT_EDITMSG"""
    try:
        with open(".git/COMMIT_EDITMSG", "r", encoding="utf-8") as f:
            return f.read().strip()
    except Exception as e:
        print(f"Fehler beim Lesen der Commit-Message: {e}", file=sys.stderr)
        return None

def parse_commit_message(message: str) -> Optional[Dict]:
    """Extrahiert Informationen aus der Commit-Message"""
    pattern = r"^([a-z]+)\(([a-z]+)\):\s+(.+)"
    match = re.match(pattern, message)
    if not match:
        print("Commit-Message entspricht nicht dem Format: type(scope): description", file=sys.stderr)
        return None
    
    return {
        "type": match.group(1),
        "scope": match.group(2),
        "description": match.group(3)
    }

def get_changed_files() -> List[str]:
    """Holt die Liste der geänderten Dateien aus Git"""
    import subprocess
    try:
        result = subprocess.run(
            ["git", "diff", "--cached", "--name-only"],
            capture_output=True,
            text=True,
            check=True
        )
        return result.stdout.strip().split("\n")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Abrufen der geänderten Dateien: {e}", file=sys.stderr)
        return []

def update_development_log(commit_info: Dict) -> bool:
    """Aktualisiert development_log.json"""
    try:
        log_path = Path("development_log.json")
        if not log_path.exists():
            print("development_log.json nicht gefunden", file=sys.stderr)
            return False
        
        # Lade existierendes Log
        with open(log_path, "r", encoding="utf-8") as f:
            log = json.load(f)
        
        # Erstelle neuen Entry
        timestamp = datetime.now().astimezone().isoformat()
        new_entry = {
            "timestamp": timestamp,
            "type": commit_info["type"],
            "component": commit_info["scope"],
            "description": commit_info["description"],
            "details": [],
            "files_changed": get_changed_files(),
            "commit_hash": "",
            "test_impact": {
                "tests_affected": [],
                "tests_added": []
            },
            "regression_potential": "medium"
        }
        
        # Füge Entry hinzu und aktualisiere Timestamp
        log["entries"].insert(0, new_entry)
        log["meta"]["last_updated"] = timestamp
        
        # Speichere aktualisiertes Log
        with open(log_path, "w", encoding="utf-8") as f:
            json.dump(log, f, indent=2, ensure_ascii=False)
        
        # Füge Datei zum Commit hinzu
        import subprocess
        subprocess.run(["git", "add", "development_log.json"], check=True)
        
        return True
        
    except Exception as e:
        print(f"Fehler beim Aktualisieren des Logs: {e}", file=sys.stderr)
        return False

def main():
    # Hole Commit-Message
    message = get_commit_message()
    if not message:
        sys.exit(1)
    
    # Parse Commit-Message
    commit_info = parse_commit_message(message)
    if not commit_info:
        sys.exit(1)
    
    # Update Log
    if not update_development_log(commit_info):
        sys.exit(1)
    
    print("development_log.json erfolgreich aktualisiert")
    sys.exit(0)

if __name__ == "__main__":
    main()
