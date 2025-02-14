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

2. **Server-Streaming-Verhalten**
   - Server sendet kontinuierlich aktualisierte Transkriptionen
   - Jede Nachricht enthält den kompletten bisherigen Text
   - Segmente werden schrittweise erweitert und verfeinert
   - Beispiel:
     ```
     "Der Himmel..."
     "Der Himmel ist..."
     "Der Himmel ist blau."
     ```

### Timing-System

Der Client verwendet ein hierarchisches Timing-System für optimale Performance und Zuverlässigkeit:

#### 1. Basis-Konstanten

Fundamentale Zeiteinheiten, von denen sich andere Timing-Parameter ableiten:

- **BASE_DELAY (0.1s)**
  - Grundlegende Verzögerung für Polling und Checks
  - Basis für kurze, häufige Operationen
  - Beispiel: Tastendruck-Verzögerungen = BASE_DELAY * 0.5

- **BASE_TIMEOUT (2.0s)**
  - Standardtimeout für Thread-Operationen
  - Basis für Verbindungs- und Operationstimeouts
  - Beispiel: WS_CONNECT_TIMEOUT = BASE_TIMEOUT * 2.5

- **BASE_RETRY (2.0s)**
  - Grundlegende Wartezeit für Wiederholungsversuche
  - Basis für exponentielles Backoff
  - Beispiel: WS_MAX_RETRY_DELAY = BASE_RETRY * 15

- **BASE_WAIT (1.0s)**
  - Standardwartezeit für Nachrichtenverarbeitung
  - Basis für Puffer und Verarbeitungszeiten
  - Beispiel: WS_FINAL_WAIT = BASE_WAIT * 30

#### 2. Timing-Gruppen

Verwandte Parameter mit ähnlichen Zeitskalen:

1. **Thread-Management**
   ```python
   THREAD_TIMEOUT = BASE_TIMEOUT
   WS_THREAD_TIMEOUT = THREAD_TIMEOUT
   AUDIO_THREAD_TIMEOUT = THREAD_TIMEOUT
   HOTKEY_THREAD_TIMEOUT = THREAD_TIMEOUT
   ```

2. **Polling und Checks**
   ```python
   POLL_INTERVAL = BASE_DELAY
   WS_POLL_INTERVAL = POLL_INTERVAL
   HOTKEY_POLL_INTERVAL = POLL_INTERVAL
   ```

3. **Retry-Mechanismen**
   ```python
   RETRY_DELAY = BASE_RETRY
   WS_RETRY_DELAY = RETRY_DELAY
   WS_RECONNECT_DELAY = RETRY_DELAY * 1.5
   ```

4. **Nachrichtenverarbeitung**
   ```python
   MESSAGE_WAIT = BASE_WAIT
   WS_MESSAGE_WAIT = MESSAGE_WAIT
   WS_FINAL_WAIT = BASE_WAIT * 30
   ```

#### 3. Timing-Abhängigkeiten

Kritische Beziehungen zwischen Timing-Parametern:

1. **Hierarchische Abhängigkeiten**
   - Thread-Timeouts basieren auf BASE_TIMEOUT
   - Polling-Intervalle basieren auf BASE_DELAY
   - Retry-Delays skalieren mit BASE_RETRY

2. **Kausale Abhängigkeiten**
   - WS_FINAL_WAIT > WS_MESSAGE_WAIT (Nachrichten müssen verarbeitet sein)
   - RETRY_DELAY < WS_MAX_RETRY_DELAY (Exponentielles Backoff)
   - MIN_OUTPUT_INTERVAL < MAX_SENTENCE_WAIT (Satzverarbeitung)

3. **Performance-Abhängigkeiten**
   - Kürzere POLL_INTERVAL = bessere Reaktionszeit, höhere CPU-Last
   - Längere WS_FINAL_WAIT = mehr Texte, längere Wartezeit
   - Größerer AUDIO_BUFFER = stabilere Übertragung, höhere Latenz

#### 4. Optimierungsmöglichkeiten

Ansatzpunkte für Performance-Verbesserungen:

1. **Reaktionszeit**
   - POLL_INTERVAL und KEY_PRESS_DELAY für UI-Responsivität
   - WS_POLL_INTERVAL für Verbindungsstatus
   - HOTKEY_POLL_INTERVAL für Tastenerkennung

2. **Stabilität**
   - WS_FINAL_WAIT für Texterfassung
   - RETRY_DELAY für Reconnect-Verhalten
   - AUDIO_BUFFER_SECONDS für Streaming

3. **Ressourcennutzung**
   - THREAD_TIMEOUT für Thread-Cleanup
   - TERMINAL_MONITOR_INTERVAL für Systemlast
   - MESSAGE_WAIT für Verarbeitungspuffer

4. **Benutzererfahrung**
   - MIN_OUTPUT_INTERVAL für Textfluss
   - MAX_SENTENCE_WAIT für Echtzeitgefühl
   - PROMPT_INPUT_DELAY für Eingabegeschwindigkeit

### Verbindungsabbau

Der Verbindungsabbau erfolgt in mehreren Schritten:
1. END_OF_AUDIO Signal senden
2. FINAL_WAIT Sekunden auf letzte Segmente warten
3. MESSAGE_WAIT Sekunden für Nachrichtenverarbeitung
4. Audio-Verarbeitung deaktivieren
5. Nochmals MESSAGE_WAIT für letzte Verarbeitung
6. Verbindung sauber schließen

4. **Status-Meldungen**
   - "Aufnahme gestartet (F13)" beim Start
   - "Aufnahme gestoppt (F13)" beim Stopp
   - "Warte auf letzte Texte..." während der Wartezeit
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
```

### Automatische Dokumentation

Das Projekt verwendet einen pre-commit Hook, der automatisch das development_log.json aktualisiert. Der Hook:

1. Extrahiert Informationen aus der Commit-Message:
   - Typ der Änderung (feat, fix, docs, etc.)
   - Betroffene Komponente
   - Beschreibung der Änderung

2. Erstellt einen neuen Log-Eintrag mit:
   - Zeitstempel
   - Geänderte Dateien
   - Standardwerte für Test-Impact und Regression-Potential

3. Fügt den Eintrag dem development_log.json hinzu

Dies ermöglicht:
- Automatische Dokumentation von Änderungen
- Konsistente Struktur der Entwicklungshistorie
- Minimaler manueller Aufwand
- Basis für Analysen und Reports

Die Commit-Message muss dem Format folgen:
```
type(scope): description

- Detaillierte Beschreibung (optional)
- Weitere Details (optional)
```

Beispiel:
```
fix(websocket): Verbindungsabbau optimiert

- Zusätzliche Wartezeit für Nachrichten
- Verbesserte Fehlerbehandlung
- Status-Reset vor Verbindungsabbau
