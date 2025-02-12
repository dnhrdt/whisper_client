# Whisper Client

Ein Python-Client für WhisperLive zur Echtzeit-Spracherkennung.

## Beschreibung

Dieser Client verbindet sich mit einem WhisperLive Server und ermöglicht die Echtzeit-Transkription von Sprache über das Mikrofon. Die Transkription erfolgt in Deutsch und kann später in verschiedene Anwendungen eingefügt werden.

## Funktionen

- 🎤 Echtzeit-Audioaufnahme
- 🔄 Automatische Reconnects
- 📝 Deutsche Spracherkennung
- ⌨️ Automatische Text-Insertion
- 🚀 Einfache Steuerung via Hotkey
- 📊 Status-Anzeigen und Logging

## Installation

1. Python 3.12+ installieren
2. Repository klonen
3. Windows: pywin32 wird für Text-Insertion benötigt
4. Virtuelle Umgebung erstellen:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```
4. Abhängigkeiten installieren:
```bash
pip install -r requirements.txt
```

## Konfiguration

### Server-Verbindung
- Host: localhost
- Port: 9090
- WebSocket URL: ws://localhost:9090

### Audio-Einstellungen
- Chunk-Größe: 4096
- Format: paInt16
- Kanäle: 1 (Mono)
- Samplerate: 16000 Hz

### Whisper-Konfiguration
```json
{
    "language": "de",
    "task": "transcribe",
    "use_vad": true,
    "backend": "faster_whisper"
}
```

## Verwendung

1. WhisperLive Server in Docker/WSL2 starten
2. Client starten:
```bash
python whisper_client.py
```
3. Steuerung:
   - Alt+Space: Aufnahme starten/stoppen
   - Strg+C: Programm beenden

## Projektstruktur

```
whisper_client/
├── README.md              # Projektdokumentation
├── requirements.txt       # Python Abhängigkeiten
├── whisper_client.py      # Hauptprogramm
├── docs/                  # Zusätzliche Dokumentation
│   └── development.md     # Entwickler-Dokumentation
└── logs/                  # Log-Dateien
    └── whisper_client_YYYYMMDD.log
```

## Entwicklung

Siehe [docs/development.md](docs/development.md) für detaillierte Informationen zur Weiterentwicklung.

## Lizenz

Private Nutzung
