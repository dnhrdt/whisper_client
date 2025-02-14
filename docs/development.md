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

## Neue Erkenntnisse (2025-02-14)

### Timing-Analyse

Die detaillierte Analyse der Timing-Komponenten hat wichtige Erkenntnisse gebracht:

1. **Server-Kommunikation Unklarheiten**
   - Interne Buffer-Größe des Servers unbekannt
   - Verarbeitungs-Trigger nicht dokumentiert
   - Batch-Processing-Strategie unklar

2. **Whisper-Konfiguration**
   - Modell-Parameter und Einstellungen unbekannt
   - Segmentierungslogik nicht dokumentiert
   - VAD-Einstellungen unklar

3. **Antwortformat**
   - JSON-Struktur nicht vollständig dokumentiert
   - Timestamps und Confidence-Scores?
   - Satzgrenzen-Markierung?

4. **Timing-Garantien**
   - Min/Max Verzögerungen nicht spezifiziert
   - Update-Frequenz unbekannt
   - Nachträgliche Korrekturen möglich?

### Dokumentations-Update

Neue Diagramme wurden erstellt:
- `docs/diagrams/architecture/`: Systemarchitektur
- `docs/diagrams/sequence/`: Ablaufdiagramme
- `docs/diagrams/timing/`: Timing-Übersichten
- `docs/diagrams/state/`: Zustandsdiagramme

### Nächste Schritte

1. **Server-Dokumentation**
   - WhisperLive Server-Code analysieren
   - Whisper-Dokumentation prüfen
   - VAD-Implementierung verstehen

2. **Test-Strategie**
   - Minimale Textlänge ermitteln
   - Update-Frequenz messen
   - Korrektur-Verhalten testen

3. **Timing-Optimierung**
   - Server-Parameter dokumentieren
   - Client-Timing anpassen
   - Tests entsprechend aktualisieren

## Timing-System

Der Client verwendet ein hierarchisches Timing-System für optimale Performance und Zuverlässigkeit:

### 1. Basis-Konstanten

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

### 2. Timing-Gruppen

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

### 3. Timing-Abhängigkeiten

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

### 4. Optimierungsmöglichkeiten

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

## Verbindungsabbau und Status-Meldungen

### Verbindungsabbau

Der Verbindungsabbau erfolgt in mehreren Schritten:
1. END_OF_AUDIO Signal senden
2. FINAL_WAIT Sekunden auf letzte Segmente warten
3. MESSAGE_WAIT Sekunden für Nachrichtenverarbeitung
4. Audio-Verarbeitung deaktivieren
5. Nochmals MESSAGE_WAIT für letzte Verarbeitung
6. Verbindung sauber schließen

### Status-Meldungen
- "Aufnahme gestartet (F13)" beim Start
- "Aufnahme gestoppt (F13)" beim Stopp
- "Warte auf letzte Texte..." während der Wartezeit
- "Audio-Verarbeitung beendet" nach Wartezeit

## Server-Integration

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

## Commit-Konventionen

### Format
```
type(scope): description

- Detail 1
- Detail 2
- ...weitere Details
```

### Typen
- `feat`: Neue Features
- `fix`: Fehlerbehebungen
- `docs`: Dokumentation
- `style`: Formatierung
- `refactor`: Code-Umstrukturierung
- `test`: Tests
- `chore`: Wartung

### Scopes
- `audio`: Audio-Verarbeitung
- `ws`: WebSocket
- `text`: Text-Verarbeitung
- `config`: Konfiguration
- `repo`: Repository-Management
- `test`: Test-Framework
- `docs`: Dokumentation

### Beispiele
```bash
# Einfacher Commit
git commit -m "feat(audio): Overflow-Handling implementiert"

# Ausführlicher Commit (Bewährtes Template)
git commit -m "refactor(timing): Timing-Parameter zentralisiert

- Alle Timing-Parameter in config.py ausgelagert
- Dokumentation in development.md erweitert
- Module angepasst:
  - WebSocket-Timing (Verbindung, Reconnects)
  - Audio-Timing (Puffer, Threads)
  - Text-Timing (Tastatureingaben, Clipboard)
  - Hotkey-Timing (Polling, Threads)
  - Terminal-Timing (Inaktivität, Monitoring)"
```

### Template für komplexe Änderungen
```
type(scope): kurze prägnante beschreibung

- Hauptänderung 1 beschreiben
- Hauptänderung 2 beschreiben
- Betroffene Module:
  - Modul 1 (spezifische Änderungen)
  - Modul 2 (spezifische Änderungen)
  - Modul 3 (spezifische Änderungen)"
```

Wichtig:
- Erste Zeile: `type(scope): description` exakt in diesem Format
- Leerzeile nach der ersten Zeile
- Details mit Bindestrichen aufzählen
- Bei vielen Moduländerungen eingerückte Liste verwenden

### Automatische Dokumentation
Der pre-commit Hook und update_dev_log.py:
1. Prüfen das Commit-Message-Format
2. Extrahieren Metadaten (Typ, Scope, Beschreibung)
3. Aktualisieren development_log.json
4. Fügen Zeitstempel und Impact-Analyse hinzu

### VSCode Snippets

Für einfache und korrekte Commit-Messages stehen zwei Snippets zur Verfügung:

1. **Standardformat** (Trigger: `commit⏎`)
   ```
   feat(audio): overflow-handling implementiert

   - Buffer-Größe optimiert
   - Overflow-Erkennung hinzugefügt
   - Logging verbessert
   ```

2. **Komplexe Änderungen** (Trigger: `commitc⏎`)
   ```
   refactor(timing): timing-parameter zentralisiert

   - Alle Parameter in config.py ausgelagert
   - Dokumentation erweitert
   - Module angepasst:
     - WebSocket: Verbindungs-Timing
     - Audio: Buffer-Timing
     - Text: Ausgabe-Timing
   ```

Nutzung:
1. Git Staging-Bereich öffnen
2. Commit-Message eingeben
3. `commit⏎` oder `commitc⏎` tippen
4. Tab-Taste für Navigation zwischen Feldern
5. Platzhalter ausfüllen

### Best Practices
1. Klare, präzise Beschreibungen
2. Ein Feature/Fix pro Commit
3. Details für größere Änderungen
4. Korrekte Scope-Zuordnung
5. Aussagekräftige Commit-Messages
6. Snippets für konsistentes Format nutzen
