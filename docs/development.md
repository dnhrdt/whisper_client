# Entwickler-Dokumentation

## Entwicklungshistorie

Die Entwicklungshistorie wird in inkrementellen Log-Dateien dokumentiert:
- `docs/development/logs/development_log_000.json`: Basis-Version
- `docs/development/logs/development_log_001.json` und folgende: Inkrementelle Updates

Weitere Details und Referenzen:
- Architektur-Diagramme: `docs/diagrams/architecture/`
- Sequenz-Diagramme: `docs/diagrams/sequence/`
- Zustandsdiagramme: `docs/diagrams/state/`
- Untersuchungen: `docs/investigations/`

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
   - Float32 Normalisierung (int16 zu float32 Division durch 32768.0)
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

## Neue Erkenntnisse (2025-02-15)

### Audio-Verarbeitungs-PoCs

Drei Proof-of-Concept Tests für Audio-Optimierungen wurden durchgeführt:

1. **Tumbling Window**
   - 130ms durchschnittliche Latenz
   - Stabile Verarbeitung (27 Fenster in 3.5s)
   - Überlappende Fenster für Audio-Übergänge
   - Status: Implementierungsbereit

2. **Queue-basierte Chunk-Verwaltung**
   - Thread- und Async-Implementierungen
   - AudioChunk Datenmodell mit Metadaten
   - Verbesserte WebSocket-Integration möglich
   - Status: Konzeptionell validiert

3. **Audio-Segmentierung**
   - Erfolgreiche Sprach-Segment-Erkennung
   - Energie-basierte Klassifizierung
   - Parameteroptimierung erforderlich
   - Status: Teilweise validiert

Diese Optimierungen werden für spätere Integration vorgemerkt, während der Fokus zunächst auf den Speech-Tests bleibt.

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
