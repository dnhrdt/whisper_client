# Entwickler-Dokumentation

## Architektur

Der Whisper Client basiert auf einer WebSocket-Verbindung zum WhisperLive Server und verarbeitet Audio in Echtzeit.

### Hauptkomponenten

1. **WebSocket-Client**
   - Verbindungsaufbau und -management
   - Automatische Reconnects
   - JSON-Konfiguration

2. **Text-Insertion**
   - Windows API via pywin32
   - Automatische Fenstererkennung
   - Tastatureingabe-Simulation

3. **Audio-Aufnahme**
   - PyAudio für Mikrofonzugriff
   - Threaded Recording
   - Float32 Normalisierung (int16 zu float32, Division durch 32768.0)
   - Korrekte Datentypen für Server-Verarbeitung
   - Robuste Pufferung und Timing

4. **Logging-System**
   - Datei- und Konsolenausgabe
   - Tägliche Logrotation
   - Strukturierte Fehlerbehandlung

## Status-Codes

### Verbindung
- ✓ Verbunden
- ✗ Getrennt
- 🔄 Reconnecting

### Aufnahme
- 🎤 Aktiv
- ⏹️ Gestoppt
- ⚠️ Fehler

## Fehlerbehandlung

1. **Verbindungsfehler**
   - Timeout nach 5 Sekunden
   - 3 Sekunden Wartezeit vor Reconnect
   - Maximale Reconnect-Versuche: Unbegrenzt
   - 20-Sekunden-Wartezeit für letzte Segmente
   - Verbindung bleibt während Wartezeit offen
   - Klare Status-Meldungen für Benutzer
   - Intelligentes Reconnect nur bei unerwarteter Trennung
   - Verbindungsabbau nur wenn keine Verarbeitung aktiv

2. **Zwischenablage**
   - Robustes Leeren mit Retry-Mechanismus
   - Maximale Retry-Versuche: 3
   - Exponentielles Backoff zwischen Versuchen
   - Detaillierte Fehlermeldungen bei Zugriffsproblemen

2. **Audio-Fehler**
   - Overflow-Ignorierung
   - Automatischer Stream-Reset
   - Thread-Safe Aufnahmesteuerung

## Weiterentwicklung

### Geplante Features

1. **Windows-Integration**
   - System Tray Icon (pystray)
   - Autostart-Funktion
   - Globale Hotkeys

2. **Benutzeroberfläche**
   - Einstellungsdialog (tkinter/Qt)
   - Status-Visualisierung
   - Transkript-Historie

3. **Erweiterungen**
   - Text-Insertion (pywin32)
   - Sprachbefehle
   - Mehrsprachenunterstützung

### Code-Stil

- PEP 8 Konventionen
- Typisierte Funktionen (Python 3.12+)
- Ausführliche Docstrings
- Klare Fehlerbehandlung

## Deployment

### Windows Executable

```bash
# PyInstaller Installation
pip install pyinstaller

# Executable erstellen
pyinstaller --onefile --noconsole whisper_client.py
```

### Autostart-Einrichtung

1. Executable in Programme-Ordner kopieren
2. Verknüpfung erstellen
3. In Autostart-Ordner platzieren:
   `shell:startup`

## Server-Integration

### Audio-Verarbeitung

1. **Datenformat**
   - Client sendet normalisierte float32 Daten
   - Konvertierung: int16 → float32 / 32768.0
   - Server erwartet normalisierte [-1.0, 1.0] Werte

2. **Aufnahme-Ende**
   - END_OF_AUDIO Signal an Server
   - 30-Sekunden-Wartezeit für letzte Segmente
   - Verbindung bleibt für Nachzügler-Texte offen
   - Verarbeitung erst nach Empfang aller Texte deaktivieren
   - Sauberes Beenden der Verbindung

3. **Status-Meldungen**
   - "Aufnahme gestartet (F13)" beim Start
   - "Aufnahme gestoppt (F13)" beim Stopp
   - "Warte auf letzte Texte..." während der 30s
   - "Audio-Verarbeitung beendet" nach Wartezeit

### WhisperLive Server-Logs
- **Container-Zugriff**: 
  - Via `docker exec -it whisperlive bash`
  - Erweitertes Logging mit Timestamps und Details

- **Log-Mapping**:
  - Container: `/app/logs`
  - Host (WSL): `/home/michael/appdata/whisperlive/logs`
  - Symlink für einfachen Zugriff: `/logs/logs`
  - Volume-Mapping in Docker-Compose: `- /home/michael/appdata/whisperlive/logs:/app/logs`

- **Vorteile**:
  - Echtzeit-Log-Zugriff
  - Persistente Logs über Container-Neustarts
  - Vereinfachtes Debugging der Server-Komponente

### Debugging-Tools
- Server-Logs in Echtzeit verfolgen
- Audio-Verarbeitung überwachen (VAD, Transkription)
- Performance-Metriken sammeln

## Debugging

### Log-Levels

- DEBUG: Entwicklungsinformationen
  - WebSocket-Nachrichten
  - Audio-Daten-Details
  - Konfigurationsänderungen

- INFO: Standardereignisse
  - Verbindungsstatus
  - Aufnahmestatus
  - Transkriptionen

- WARNING: Nicht-kritische Probleme
  - Verbindungsverlust
  - Audio-Überläufe
  - Konfigurationsprobleme

- ERROR: Kritische Fehler
  - Verbindungsfehler
  - Audio-Gerätefehler
  - Systemfehler

### Entwicklungsumgebung

1. **VS Code Einstellungen**
   ```json
   {
     "python.linting.enabled": true,
     "python.linting.pylintEnabled": true,
     "python.formatting.provider": "black",
     "editor.formatOnSave": true
   }
   ```

2. **Empfohlene Extensions**
   - Python
   - Pylance
   - Black Formatter
   - Git History
   - GitLens

## GitHub Integration

### Repository-Struktur

```
.
├── .git/
├── .gitignore
├── .vscode/
│   └── settings.json
├── docs/
├── logs/
├── README.md
├── requirements.txt
└── whisper_client.py
```

### .gitignore

```
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
ENV/

# Logs
logs/
*.log

# VS Code
.vscode/
*.code-workspace

# PyInstaller
dist/
build/
*.spec

# Sonstiges
.DS_Store
```

### Branches

- `main`: Stabile Version
- `develop`: Entwicklungsversion
- `feature/*`: Neue Features
- `bugfix/*`: Fehlerbehebungen

### Commit-Konventionen

Format: `<typ>(<scope>): <beschreibung>`

Typen:
- feat: Neues Feature
- fix: Fehlerbehebung
- docs: Dokumentation
- style: Formatierung
- refactor: Code-Umstrukturierung
- test: Tests
- chore: Wartung

Beispiele:
```
feat(gui): System Tray Icon hinzugefügt
fix(audio): Overflow-Behandlung verbessert
docs(readme): Installation aktualisiert
