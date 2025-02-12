"""
Hilfsfunktionen für den Whisper-Client
"""
import socket
import json
import os
from datetime import datetime
import config
from src import logging

logger = logging.get_logger()

def check_server_status(host=config.WS_HOST, port=config.WS_PORT):
    """Prüft ob der WhisperLive Server läuft"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host, port))
        sock.close()
        return result == 0
    except:
        return False

def update_project_status(description=None, changes=None, status=None, files=None):
    """Aktualisiert den Projektstatus und die Task-Historie"""
    try:
        # Projekte-Datei aktualisieren
        projects_file = "projects.json"
        if os.path.exists(projects_file):
            with open(projects_file, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            
            # Aktuelles Projekt finden
            project_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
            for project in projects["projects"]:
                if project["path"] == project_path:
                    # Status aktualisieren
                    if status:
                        project["status"] = status
                    
                    # Task hinzufügen
                    if description and changes:
                        task = {
                            "description": description,
                            "status": "completed",
                            "details": changes[0]["description"] if changes else None
                        }
                        project["current_tasks"].insert(0, task)  # Neuster Task zuerst
                    
                    # Zeitstempel aktualisieren
                    current_time = datetime.now().isoformat()
                    project["last_updated"] = current_time
                    projects["meta"]["last_updated"] = current_time
                    break
            
            # Speichern
            with open(projects_file, 'w', encoding='utf-8') as f:
                json.dump(projects, f, indent=2, ensure_ascii=False)
    
    except Exception as e:
        logger.error(f"⚠️ Fehler beim Aktualisieren des Projektstatus: {e}")
    
    # Task-Historie aktualisieren
    if description and changes:
        update_task_history(description, changes, "completed", files)

def update_task_history(description, changes, status="completed", files=None):
    """Aktualisiert die Task-Historie"""
    history_file = "task_history.json"
    
    try:
        # Lade bestehende Historie
        if os.path.exists(history_file):
            with open(history_file, 'r', encoding='utf-8') as f:
                history = json.load(f)
        else:
            history = {"tasks": []}
        
        # Neuen Task hinzufügen
        task = {
            "timestamp": datetime.now().isoformat(),
            "description": description,
            "changes": changes,
            "status": status
        }
        if files:
            task["files"] = files
        
        history["tasks"].insert(0, task)  # Neuster Task zuerst
        
        # Speichern
        with open(history_file, 'w', encoding='utf-8') as f:
            json.dump(history, f, indent=2, ensure_ascii=False)
            
    except Exception as e:
        logger.error(f"⚠️ Fehler beim Aktualisieren der Task-Historie: {e}")

def show_startup_message():
    """Zeigt die Startmeldung an"""
    logger.info("\n=== Whisper Client ===")
    logger.info("🔥 Client gestartet!")
    logger.info(f"⌨️  Drücke {config.HOTKEY_TOGGLE_RECORDING} zum Starten/Stoppen der Aufnahme")
    logger.info(f"⚡ Drücke {config.HOTKEY_EXIT} zum Beenden")
    logger.info("-" * 50)

def show_server_error():
    """Zeigt Fehlermeldung bei nicht erreichbarem Server"""
    print("\n⚠️ WhisperLive Server ist nicht erreichbar!")
    print("\nBitte starte den Server mit einem der folgenden Befehle:")
    print("\n1. Direkt aus dem Quellcode:")
    print("   cd path/to/whisperlive")
    print("   python server.py")
    print("\n2. Oder als Docker Container:")
    print("   docker run -p 9090:9090 whisperlive")
    print("\nDanach starte diesen Client erneut.")
