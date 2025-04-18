# Audio-Verarbeitung und Server-Kommunikation

```mermaid
sequenceDiagram
    box Client
    participant AM as AudioManager
    participant WS as WebSocket
    participant TM as TextManager
    end
    box Server
    participant S as Server
    participant W as Whisper
    end

    Note over AM,W: Bekannte Audio-Parameter
    AM->>WS: send_audio()
    Note right of AM: ✓ AUDIO_CHUNK: 4096<br/>✓ AUDIO_RATE: 16000<br/>✓ FORMAT: paInt16<br/>✓ BUFFER: 1.0s

    WS->>S: stream_audio

    Note over S,W: ❓ Unbekannte Server-Verarbeitung
    Note over S,W: • Wie groß ist der interne Buffer?<br/>• Wann startet die Verarbeitung?<br/>• Gibt es Batch-Processing?

    S->>W: process_audio

    Note over W: ❓ Whisper-Parameter
    Note over W: • Modell-Konfiguration?<br/>• Segmentierungslogik?<br/>• VAD-Einstellungen?

    W-->>S: text_segments

    Note over S: ❓ Server-Antwortformat
    Note over S: • JSON-Struktur?<br/>• Timestamps?<br/>• Confidence-Scores?<br/>• Satzgrenzen?

    S-->>WS: response
    Note over WS,TM: ❓ Timing-Garantien
    Note over WS,TM: • Min/Max Verzögerung?<br/>• Update-Frequenz?<br/>• Nachträgliche Korrekturen?

    WS->>TM: process_text()

    Note over TM: ❓ Text-Verarbeitung
    Note over TM: • Wie mit Überlappungen umgehen?<br/>• Wann ist ein Satz "final"?<br/>• Buffer-Strategie?
```

## Offene Fragen zur Server-Kommunikation

### Server-Verarbeitung
- Größe des internen Audio-Buffers
- Trigger für Start der Verarbeitung
- Batch-Processing-Strategie

### Whisper-Konfiguration
- Verwendetes Modell und Parameter
- Segmentierungslogik
- VAD (Voice Activity Detection) Einstellungen

### Antwortformat
- Genaue JSON-Struktur
- Vorhandensein von Timestamps
- Confidence-Scores für Erkennungen
- Markierung von Satzgrenzen

### Timing-Garantien
- Minimale/Maximale Verzögerungen
- Frequenz der Updates
- Möglichkeit nachträglicher Korrekturen

### Client-seitige Verarbeitung
- Strategie für überlappende Texte
- Definition von "finalen" Sätzen
- Buffer-Management
