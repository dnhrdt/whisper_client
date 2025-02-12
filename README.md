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

## Verwendung

1. WhisperLive Server starten (siehe Server-Repository)

2. Client starten:
```bash
python main.py
```

3. Steuerung:
- Alt+Space: Aufnahme starten/stoppen
- ESC: Programm beenden

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
