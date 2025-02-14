# WhisperClient

## Grundregeln & Konventionen

### 1. Dokumentation & Commits
- Jede Änderung MUSS dokumentiert werden
- Commits nach jeder funktionalen Änderung
- Commit-Format: `<typ>(<scope>): <beschreibung>`
  * typ: feat|fix|docs|style|refactor|test|chore
  * scope: audio|text|websocket|config|etc.
  * Beispiel: `fix(audio): Overflow-Behandlung verbessert`

### 2. Projektdokumentation
- [Roadmap](roadmap.md): Entwicklungsplan und Meilensteine
- config.json: Technische Konfiguration & Komponenten-Mapping
- development_log.json: Chronologische Entwicklungshistorie & Fehler
- context.json: Aktueller Stand & Known Issues

### 3. Testprozesse
- Jede Änderung erfordert Testaktualisierung
- Regressionstests vor jedem Commit
- Testfortschritt in development_log.json dokumentieren

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
   - Float32 Normalisierung

4. **Logging-System**
   - Datei- und Konsolenausgabe
   - Tägliche Logrotation
   - Strukturierte Fehlerbehandlung

## Entwicklungsrichtlinien

### Code-Stil
- PEP 8 Konventionen
- Typisierte Funktionen (Python 3.12+)
- Ausführliche Docstrings
- Klare Fehlerbehandlung

### Fehlerbehandlung
1. **Verbindungsfehler**
   - Timeout nach 5 Sekunden
   - 3 Sekunden Wartezeit vor Reconnect
   - Maximale Reconnect-Versuche: Unbegrenzt

2. **Audio-Fehler**
   - Overflow-Ignorierung
   - Automatischer Stream-Reset
   - Thread-Safe Aufnahmesteuerung

### Logging-Levels
- DEBUG: Entwicklungsinformationen
  * WebSocket-Nachrichten
  * Audio-Daten-Details
  * Konfigurationsänderungen

- INFO: Standardereignisse
  * Verbindungsstatus
  * Aufnahmestatus
  * Transkriptionen

- WARNING: Nicht-kritische Probleme
  * Verbindungsverlust
  * Audio-Überläufe
  * Konfigurationsprobleme

- ERROR: Kritische Fehler
  * Verbindungsfehler
  * Audio-Gerätefehler
  * Systemfehler

## Entwicklungsumgebung

### VS Code Einstellungen
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true
}
```

### Empfohlene Extensions
- Python
- Pylance
- Black Formatter
- Git History
- GitLens

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
3. In Autostart-Ordner platzieren: `shell:startup`

## Repository-Struktur
```
.
├── docs/
│   ├── project.md       # Diese Datei - Hauptdokumentation
│   ├── roadmap.md       # Entwicklungsplan und Meilensteine
│   └── development.md   # Detaillierte Entwicklerdokumentation
├── src/
│   ├── audio.py        # Audio-Aufnahme
│   ├── websocket.py    # Server-Kommunikation
│   ├── text.py         # Textverarbeitung
│   ├── logging.py      # Logging-System
│   └── utils.py        # Hilfsfunktionen
├── tests/              # Testfälle und -framework
│   ├── speech_test_cases.md      # Testfall-Definitionen
│   ├── speech_test_progress.json # Testfortschritt-Tracking
│   ├── test_prompt_output.py     # Prompt-Tests
│   ├── test_server_flow.py       # Server-Kommunikation-Tests
│   ├── test_text_processing.py   # Textverarbeitung-Tests
│   └── update_test_progress.py   # Test-Management
├── config.json         # Konfiguration
├── development_log.json # Entwicklungshistorie
├── context.json        # Aktueller Zustand
├── list_devices.py     # Audio-Geräte Auflistung
├── requirements.txt    # Python Dependencies
└── README.md          # Öffentliche Projektbeschreibung
```

## Hilfsprogramme

### list_devices.py
Dieses Skript listet alle verfügbaren Audio-Eingabegeräte auf und hilft bei der Konfiguration des korrekten Mikrofons.

Verwendung:
```bash
python list_devices.py
```

### Test-Framework
Das Test-Framework besteht aus mehreren Komponenten:
- speech_test_cases.md: Dokumentation der Testfälle
- speech_test_progress.json: Aktueller Testfortschritt
- update_test_progress.py: Tool zum Aktualisieren des Testfortschritts
- Verschiedene Testmodule für spezifische Komponenten

## Dependencies
Alle Projektabhängigkeiten sind in requirements.txt dokumentiert. Installation:
```bash
pip install -r requirements.txt
