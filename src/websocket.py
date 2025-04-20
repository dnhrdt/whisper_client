"""
WebSocket Communication Module for the Whisper Client (Fassade)
Version: 2.7
Timestamp: 2025-04-20 17:33 CET

Diese Datei dient als Fassade für das refaktorierte WebSocket-Modul.
Sie importiert und re-exportiert alle notwendigen Funktionen und Klassen
aus den neuen Modulen im ws_client-Paket.

Die ursprüngliche Implementierung wurde in mehrere spezialisierte Module aufgeteilt:
- ws_client/state.py: ConnectionState Enum und Zustandsverwaltung
- ws_client/connection.py: Verbindungsfunktionalität und Instance-Tracking
- ws_client/messaging.py: Nachrichtenverarbeitung und Datenübertragung
- ws_client/error_handling.py: Fehlerbehandlung und Recovery
- ws_client/manager.py: Hauptklasse WhisperWebSocket
- ws_client/__init__.py: API und Hauptklasse
- ws_client/callbacks.py: Callback-Funktionen für WebSocket-Events
- ws_client/cleanup.py: Aufräumfunktionen
- ws_client/connection_management.py: Verbindungsverwaltung
- ws_client/processing.py: Verarbeitung von WebSocket-Nachrichten
- ws_client/state_management.py: Zustandsverwaltung
"""

# Verwende explizite Importe mit vollständigem Pfad
# Importiere aus den einzelnen Modulen im ws_client-Paket
from src.ws_client.connection import (
    ConnectionManager,
    create_websocket_app,
    generate_client_id,
    generate_session_id,
)
from src.ws_client.error_handling import (
    handle_connection_close,
    handle_connection_error,
    wait_with_timeout,
)
from src.ws_client.manager import WhisperWebSocket
from src.ws_client.messaging import process_message, send_audio_data, send_config, send_end_of_audio
from src.ws_client.state import ConnectionState

# Exportiere alle Symbole, die von anderen Modulen verwendet werden könnten
__all__ = [
    # Hauptklasse
    "WhisperWebSocket",
    # Wichtige Typen
    "ConnectionState",
    "ConnectionManager",
    # Verbindungsfunktionen
    "create_websocket_app",
    "generate_client_id",
    "generate_session_id",
    # Fehlerbehandlung
    "handle_connection_close",
    "handle_connection_error",
    "wait_with_timeout",
    # Nachrichtenverarbeitung
    "process_message",
    "send_audio_data",
    "send_config",
    "send_end_of_audio",
]
