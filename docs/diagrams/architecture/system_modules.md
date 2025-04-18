# System-Modulstruktur

```mermaid
flowchart TD
    classDef core fill:#b3d9ff,stroke:#000,color:#000
    classDef util fill:#c1f0c1,stroke:#000,color:#000
    classDef test fill:#fff2cc,stroke:#000,color:#000
    classDef config fill:#e6ccff,stroke:#000,color:#000

    %% Hauptmodule
    MAIN[main.py<br/>Hauptanwendung]:::core
    CONFIG[config.py<br/>Konfiguration]:::config

    %% Core Module
    AUDIO[audio.py<br/>AudioManager]:::core
    WS[websocket.py<br/>WhisperWebSocket]:::core
    TEXT[text.py<br/>TextManager]:::core
    HOTKEY[hotkeys.py<br/>HotkeyManager]:::core
    TERMINAL[terminal.py<br/>TerminalManager]:::core

    %% Utility Module
    UTILS[utils.py<br/>Hilfsfunktionen]:::util
    LOGGING[logging.py<br/>Logger]:::util

    %% Test Module
    TEST_TIMING[timing_tests.py<br/>Timing-Tests]:::test
    TEST_SERVER[test_server_flow.py<br/>Server-Tests]:::test
    TEST_TEXT[test_text_processing.py<br/>Text-Tests]:::test

    %% Abhängigkeiten
    CONFIG --> MAIN
    CONFIG --> AUDIO
    CONFIG --> WS
    CONFIG --> TEXT
    CONFIG --> HOTKEY
    CONFIG --> TERMINAL

    MAIN --> AUDIO
    MAIN --> WS
    MAIN --> TEXT
    MAIN --> HOTKEY
    MAIN --> TERMINAL

    AUDIO --> LOGGING
    WS --> LOGGING
    TEXT --> LOGGING
    HOTKEY --> LOGGING
    TERMINAL --> LOGGING

    AUDIO --> UTILS
    WS --> UTILS
    TEXT --> UTILS

    %% Test-Abhängigkeiten
    TEST_TIMING --> AUDIO
    TEST_TIMING --> WS
    TEST_TIMING --> TEXT
    TEST_SERVER --> WS
    TEST_TEXT --> TEXT

    %% Gruppierung
    subgraph Core [Core Module]
        MAIN
        AUDIO
        WS
        TEXT
        HOTKEY
        TERMINAL
    end

    subgraph Utils [Utility Module]
        UTILS
        LOGGING
    end

    subgraph Tests [Test Module]
        TEST_TIMING
        TEST_SERVER
        TEST_TEXT
    end

    subgraph Conf [Konfiguration]
        CONFIG
    end
