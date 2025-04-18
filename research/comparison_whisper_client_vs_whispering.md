# Vergleich: whisper_client vs. Whispering
Version: 1.0
Timestamp: 2025-04-14 22:15 CET

Dieses Dokument vergleicht den `whisper_client` (unser Projekt) mit der Anwendung `Whispering` (https://github.com/braden-w/whispering), basierend auf einer initialen Code-Analyse von "Whispering".

## 1. Technologie-Stack

*   **whisper_client:**
    *   Sprache: Python
    *   Kernbibliotheken: PyAudio, websocket-client, pywin32
*   **Whispering:**
    *   Sprachen: TypeScript, Rust
    *   Frontend (Web & Desktop UI): Svelte 5, SvelteKit
    *   Desktop App Framework: Tauri
    *   Browser Extension: React, Plasmo
    *   Desktop Backend (Audio etc.): Rust (`cpal` für Audio)
    *   Build/Monorepo: pnpm, turborepo, biome

## 2. Architektur & Plattform

*   **whisper_client:**
    *   Standalone Python-Anwendung
    *   Nur für Windows (wegen pywin32 für Texteingabe)
    *   Keine separate UI
*   **Whispering:**
    *   Monorepo mit mehreren Teilen: Web App, Desktop App, Browser Extension
    *   Plattformübergreifend: Windows, macOS, Linux (Desktop), Web, Chrome Extension
    *   Tauri nutzt Rust für native Desktop-Funktionen

## 3. Benutzeroberfläche (UI)

*   **whisper_client:**
    *   Keine eigene UI. Fokus auf direkte Texteingabe in andere Anwendungen.
*   **Whispering:**
    *   Vollständige UI (Web/Desktop) für:
        *   Aufnahme-Steuerung (manuell, VAD)
        *   Anzeige/Bearbeitung von Transkripten
        *   Verwaltung von Aufnahmen (lokal in IndexedDB)
        *   Detaillierte Einstellungen
    *   Zusätzliche UI in der Browser Extension und Integration in ChatGPT/Claude.

## 4. Audio-Aufnahme

*   **whisper_client:**
    *   Nutzt PyAudio direkt in Python.
    *   Implementiert Tumbling Window und Crossfading in Python.
*   **Whispering:**
    *   Desktop: Nutzt die `cpal`-Bibliothek in Rust (via Tauri) für nativen Zugriff.
    *   Web: Nutzt die Web Audio API (`RecorderService.web.ts`).
    *   Kein explizites Tumbling Window im analysierten Code gefunden (könnte im Server oder implizit sein).

## 5. Transkriptions-Backend & Kommunikation

*   **whisper_client:**
    *   Fest an **WhisperLive** gebunden.
    *   Kommunikation: **WebSocket-Streaming** von Audio-Chunks.
*   **Whispering:**
    *   Unterstützt **mehrere Backends** (konfigurierbar): OpenAI API, Groq API, `faster-whisper-server`, (potenziell weitere Whisper-kompatible APIs).
    *   Kommunikation: Sendet die **komplette Audiodatei** per **HTTP POST** (FormData) an das ausgewählte Backend.

## 6. Konfiguration & Einstellungen

*   **whisper_client:**
    *   Über `config.json` / `config.py`.
    *   Fokus auf Kernparameter (Gerät, Server, Timing).
*   **Whispering:**
    *   Sehr umfangreich, über UI konfigurierbar.
    *   Einstellungen im `shared`-Paket definiert (`zod`-Schema, versioniert).
    *   Umfasst Dienstauswahl, API-Keys, Shortcuts, Verhalten (Sounds, Clipboard), Datenspeicherung etc.

## 7. Kern-Features

*   **whisper_client:**
    *   Echtzeit-Diktat via WhisperLive.
    *   Direkte Texteingabe (SendMessage/Clipboard).
    *   Fokus auf geringe Latenz durch Streaming.
*   **Whispering:**
    *   Transkription über verschiedene Backends.
    *   Globale Hotkeys (Desktop).
    *   Automatisches Kopieren/Einfügen.
    *   Voice Activity Detection (VAD).
    *   Transkriptions-Management (Anzeige, Bearbeitung).
    *   Sound-Feedback.
    *   Browser-Integration (Extension).
    *   Lokale Speicherung von Aufnahmen/Transkripten.

## 8. Potenzielle Stärken & Schwächen (Initial)

*   **whisper_client:**
    *   (+) Potenziell geringere Latenz durch Streaming-Ansatz.
    *   (+) Schlankerer Ansatz, direkter Fokus auf Diktat.
    *   (+) Python-Stack (falls bevorzugt).
    *   (-) Nur Windows.
    *   (-) Feste Bindung an WhisperLive.
    *   (-) Keine UI / weniger Features.
*   **Whispering:**
    *   (+) Plattformübergreifend.
    *   (+) Flexibilität bei der Wahl des Transkriptions-Backends (inkl. lokaler Optionen).
    *   (+) Umfangreiche Features und UI.
    *   (+) Moderne Technologie, aktive Entwicklung (scheinbar).
    *   (-) Potenziell höhere Latenz durch Senden ganzer Dateien.
    *   (-) Komplexerer Technologie-Stack (JS/TS/Rust).

## 9. Fazit (Vorläufig)

"Whispering" ist eine deutlich umfangreichere, plattformübergreifende Anwendung mit Fokus auf Flexibilität beim Backend und einer vollwertigen UI. Der Kernunterschied liegt im Kommunikationsansatz (HTTP POST ganzer Dateien vs. WebSocket-Streaming) und der Backend-Bindung. Die Wahl hängt stark von den Prioritäten ab: geringstmögliche Latenz und Einfachheit (`whisper_client`) vs. Plattformunabhängigkeit, Feature-Reichtum und Backend-Flexibilität (`Whispering`).
