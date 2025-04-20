"""
WebSocket Communication Module for the Whisper Client (Fassade)
Version: 2.0
Timestamp: 2025-04-20 14:22 CET

Diese Datei dient als Fassade für das refaktorierte WebSocket-Modul.
Sie importiert und re-exportiert alle notwendigen Funktionen und Klassen
aus den neuen Modulen im websocket-Paket.

Die ursprüngliche Implementierung wurde in mehrere spezialisierte Module aufgeteilt:
- websocket/state.py: ConnectionState Enum und Zustandsverwaltung
- websocket/connection.py: Verbindungsfunktionalität und Instance-Tracking
- websocket/messaging.py: Nachrichtenverarbeitung und Datenübertragung
- websocket/error_handling.py: Fehlerbehandlung und Recovery
- websocket/manager.py: Hauptklasse WhisperWebSocket
- websocket/__init__.py: API und Hauptklasse
- websocket/callbacks.py: Callback-Funktionen für WebSocket-Events
- websocket/cleanup.py: Aufräumfunktionen
- websocket/connection_management.py: Verbindungsverwaltung
- websocket/processing.py: Verarbeitung von WebSocket-Nachrichten
- websocket/state_management.py: Zustandsverwaltung
"""

# Importiere die Hauptklasse und wichtige Typen aus dem websocket-Paket
from websocket.manager import WhisperWebSocket
from websocket.state import ConnectionState
from websocket.connection import ConnectionManager

# Für Abwärtskompatibilität, re-exportiere alle zuvor öffentlichen Funktionen
from websocket.connection import (
    create_websocket_app,
    generate_client_id,
    generate_session_id,
)
from websocket.error_handling import (
    handle_connection_close,
    handle_connection_error,
    wait_with_timeout,
)
from websocket.messaging import (
    process_message,
    send_audio_data,
    send_config,
    send_end_of_audio,
)

# Exportiere alle Symbole, die von anderen Modulen verwendet werden könnten
__all__ = [
    # Hauptklasse
    'WhisperWebSocket',

    # Wichtige Typen
    'ConnectionState',
    'ConnectionManager',

    # Verbindungsfunktionen
    'create_websocket_app',
    'generate_client_id',
    'generate_session_id',

    # Fehlerbehandlung
    'handle_connection_close',
    'handle_connection_error',
    'wait_with_timeout',

    # Nachrichtenverarbeitung
    'process_message',
    'send_audio_data',
    'send_config',
    'send_end_of_audio',
]
