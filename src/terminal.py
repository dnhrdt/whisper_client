"""
Terminal-Management für den Whisper-Client
"""
import time
import threading
from dataclasses import dataclass
from typing import Dict, Optional
from enum import Enum
from src import logger
import config

class TerminalStatus(Enum):
    """Status eines Terminals"""
    ACTIVE = "active"          # Terminal ist aktiv und wird verwendet
    INACTIVE = "inactive"      # Terminal ist inaktiv (keine Aktivität für INACTIVITY_TIMEOUT)
    CLOSING = "closing"        # Terminal wird geschlossen
    CLOSED = "closed"         # Terminal wurde geschlossen

@dataclass
class TerminalInfo:
    """Informationen über ein Terminal"""
    id: str                    # Eindeutige ID des Terminals
    name: str                  # Benutzerfreundlicher Name (z.B. "Audio-Terminal")
    status: TerminalStatus     # Aktueller Status
    last_activity: float       # Zeitstempel der letzten Aktivität
    process: Optional[object]  # Prozess-Handle (optional)

class TerminalManager:
    """Zentrale Verwaltung aller Terminals"""
    
    def __init__(self):
        self.terminals: Dict[str, TerminalInfo] = {}
        self.lock = threading.Lock()
        
        # Monitoring-Thread starten
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_terminals)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        logger.info("Terminal-Manager gestartet")
    
    def register_terminal(self, id: str, name: str, process: Optional[object] = None) -> TerminalInfo:
        """
        Registriert ein neues Terminal
        
        Args:
            id: Eindeutige ID des Terminals
            name: Benutzerfreundlicher Name
            process: Optional, Prozess-Handle
            
        Returns:
            TerminalInfo: Informationen über das registrierte Terminal
        """
        with self.lock:
            if id in self.terminals:
                raise ValueError(f"Terminal mit ID {id} existiert bereits")
            
            terminal = TerminalInfo(
                id=id,
                name=name,
                status=TerminalStatus.ACTIVE,
                last_activity=time.time(),
                process=process
            )
            self.terminals[id] = terminal
            logger.debug(f"Terminal registriert: {name} (ID: {id})")
            return terminal
    
    def update_activity(self, id: str):
        """Aktualisiert den Zeitstempel der letzten Aktivität"""
        with self.lock:
            if id in self.terminals:
                self.terminals[id].last_activity = time.time()
                if self.terminals[id].status == TerminalStatus.INACTIVE:
                    self.terminals[id].status = TerminalStatus.ACTIVE
                    logger.debug(f"Terminal reaktiviert: {self.terminals[id].name}")
    
    def close_terminal(self, id: str):
        """
        Schließt ein Terminal
        
        Args:
            id: ID des zu schließenden Terminals
        """
        with self.lock:
            if id in self.terminals:
                terminal = self.terminals[id]
                if terminal.status not in [TerminalStatus.CLOSING, TerminalStatus.CLOSED]:
                    terminal.status = TerminalStatus.CLOSING
                    logger.debug(f"Terminal wird geschlossen: {terminal.name}")
                    
                    # Prozess beenden falls vorhanden
                    if terminal.process:
                        try:
                            terminal.process.terminate()
                        except:
                            pass
                    
                    terminal.status = TerminalStatus.CLOSED
                    logger.debug(f"Terminal geschlossen: {terminal.name}")
    
    def get_terminal_info(self, id: str) -> Optional[TerminalInfo]:
        """
        Gibt Informationen über ein Terminal zurück
        
        Args:
            id: Terminal-ID
            
        Returns:
            Optional[TerminalInfo]: Terminal-Informationen oder None wenn nicht gefunden
        """
        with self.lock:
            return self.terminals.get(id)
    
    def get_active_terminals(self) -> Dict[str, TerminalInfo]:
        """
        Gibt alle aktiven Terminals zurück
        
        Returns:
            Dict[str, TerminalInfo]: Dictionary mit Terminal-IDs und Informationen
        """
        with self.lock:
            return {
                id: info for id, info in self.terminals.items()
                if info.status == TerminalStatus.ACTIVE
            }
    
    def _monitor_terminals(self):
        """
        Überwacht Terminals auf Inaktivität
        Läuft in eigenem Thread
        """
        while self.monitoring:
            try:
                current_time = time.time()
                
                # Liste der zu schließenden Terminals
                to_close = []
                
                with self.lock:
                    for id, terminal in self.terminals.items():
                        if terminal.status == TerminalStatus.ACTIVE:
                            inactive_time = current_time - terminal.last_activity
                            if inactive_time > config.TERMINAL_INACTIVITY_TIMEOUT:
                                terminal.status = TerminalStatus.INACTIVE
                                logger.debug(f"Terminal inaktiv: {terminal.name}")
                                to_close.append(id)
                
                # Inaktive Terminals schließen
                for id in to_close:
                    self.close_terminal(id)
                    
            except Exception as e:
                logger.error(f"Fehler im Terminal-Monitor: {e}")
            
            time.sleep(config.TERMINAL_MONITOR_INTERVAL)  # Intervall für Terminal-Überwachung
    
    def cleanup(self):
        """Ressourcen freigeben"""
        self.monitoring = False
        
        # Alle Terminals schließen
        with self.lock:
            for id in list(self.terminals.keys()):
                self.close_terminal(id)
        
        # Auf Monitor-Thread warten
        if self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=config.TERMINAL_THREAD_TIMEOUT)
        
        logger.info("Terminal-Manager beendet")
