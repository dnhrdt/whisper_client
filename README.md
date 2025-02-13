# WhisperLive Client

Ein Python-Client für die Echtzeit-Spracherkennung mit WhisperLive.

## Installation

1. Python 3.8 oder höher installieren
2. Repository klonen
3. Virtuelle Umgebung erstellen und aktivieren:
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/macOS
```
4. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## WhisperLive Server

Der Client benötigt einen laufenden WhisperLive Server. Der Server ist ein separates Projekt:
- Repository: https://github.com/collabora/WhisperLive
- Lokale Installation: d:/dev/WhisperLive

### Server starten (Docker)
```bash
# GPU Version mit Faster-Whisper Backend
docker run -it --gpus all -p 9090:9090 ghcr.io/collabora/whisperlive-gpu:latest

# CPU Version
docker run -it -p 9090:9090 ghcr.io/collabora/whisperlive-cpu:latest
```

## Verwendung

1. WhisperLive Server starten (siehe oben)

2. Client starten:
```bash
python main.py
```

3. Steuerung:
- F13: Aufnahme starten/stoppen
- F14: Programm beenden

## Projektstruktur

```
whisper_client/
├── main.py              # Hauptprogramm
├── config.py            # Zentrale Konfiguration
├── src/
│   ├── audio.py        # Audio-Aufnahme
│   ├── websocket.py    # Server-Kommunikation
│   ├── text.py         # Textverarbeitung
│   ├── logging.py      # Logging-System
│   └── utils.py        # Hilfsfunktionen
└── tests/
    └── test_text_processing.py  # Testfälle
```

## Features

- Echtzeit-Spracherkennung via WhisperLive
- Intelligente Textverarbeitung:
  - Satzweise Ausgabe
  - Deduplizierung
  - Abkürzungserkennung
  - Automatische Formatierung
- Robuste Fehlerbehandlung
- Ausführliches Logging

## Debugging

Für detailliertere Ausgaben Debug-Level in config.py aktivieren:
```python
LOG_LEVEL_CONSOLE = "DEBUG"
```

Die Debug-Ausgabe zeigt:
- 🔍 Server-Ausgabe: Rohe Segmente vom WhisperLive Server
- 📋 Verarbeitet: Finale, formatierte Texte
- ✓ Erfolgsmeldungen
- ⚠️ Warnungen und Fehler

### Server-Logs
Die Server-Logs sind wichtig für die Fehleranalyse:
```bash
# In WSL2
docker logs -f whisperlive
```

## Tests

Textverarbeitung testen:
```bash
python tests/test_text_processing.py
```

## Tipps für die Spracherkennung

1. Sprachtest durchführen:
   - Debug-Modus aktivieren in config.py
   - Client starten: `python main.py`
   - Verschiedene Satztypen testen (siehe unten)
   - Debug-Ausgabe beobachten

2. Testszenarios:
   - Normale Sätze: "Dies ist ein Testatz."
   - Abkürzungen: "Dr. Müller und Prof. Schmidt."
   - Pausen: "Dies ist... ein Test... mit Pausen."
   - Schnelle Sätze: "Erster Satz! Zweiter Satz! Dritter Satz!"

3. Probleme identifizieren:
   - 🔍 Server-Ausgabe zeigt Erkennungsprobleme
   - 📋 Verarbeitet zeigt Textverarbeitungsprobleme
   - Timing-Probleme in den Log-Zeitstempeln sichtbar

4. Konfiguration anpassen:
   - MIN_OUTPUT_INTERVAL: Pause zwischen Ausgaben
   - MAX_SENTENCE_WAIT: Timeout für unvollständige Sätze
   - SENTENCE_END_MARKERS: Satzende-Erkennung
