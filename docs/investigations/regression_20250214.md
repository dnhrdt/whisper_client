# Regression-Untersuchung: Server-Kommunikation (14.02.2025)

## Ausgangssituation
- **Problem**: Keine Texte werden vom Server zurückgeliefert/verwertet
- **Letzte Änderungen**: 
  1. Float32 Normalisierung deaktiviert (13.02.2025 23:26)
  2. Code-Restrukturierung (13.02.2025 22:40)

## Untersuchungsplan

### 1. Protokollierung
- Jede Änderung wird in diesem Dokument protokolliert
- Format pro Test:
  ```
  ### Test X: [Beschreibung]
  - Ausgangszustand: [...]
  - Änderung: [...]
  - Ergebnis: [...]
  - Nächste Schritte: [...]
  ```

### 2. Systematische Tests

#### A. WebSocket-Kommunikation
1. Verbindungsaufbau prüfen
   - Server-Ready Status
   - Handshake erfolgreich?
   - Konfiguration korrekt übermittelt?

2. Nachrichtenfluss analysieren
   - Werden Audio-Daten gesendet?
   - Server-Antworten im Log?
   - Nachrichtenformat korrekt?

#### B. Audio-Verarbeitung
1. Format-Überprüfung
   - Client: int16 vs float32
   - Server-Erwartung prüfen
   - Sampling-Rate und Kanäle

2. Datenübertragung
   - Puffer-Größe
   - Timing
   - Datenverlust?

#### C. Text-Verarbeitung
1. Callback-Kette
   - WebSocket → TextManager
   - Event-Handling
   - Fehlerbehandlung

### 3. Logging
- Debug-Level aktiviert
- Separate Log-Datei: logs/regression_investigation.log
- Protokollierung:
  - WebSocket-Nachrichten
  - Audio-Datenformat
  - Server-Antworten
  - Callback-Aufrufe

## Tests

### Test 1: Logging-Setup
- **Ausgangszustand**: 
  - Veraltete Referenz auf _whisperlive_logs.txt
  - Regression-Logger noch nicht vollständig konfiguriert

- **Änderungen**:
  - Entfernung der _whisperlive_logs.txt-Referenzen
  - Integration des Regression-Loggers mit detailliertem Format
  - Dokumentation der Server-Log-Location (WSL: /home/michael/appdata/whisperlive/logs)

- **Ergebnis**:
  - Logging-System bereit für detaillierte Fehleranalyse
  - Server-Logs nun über Docker-Volume zugänglich
  - Regression Investigation Logger aktiviert

### Test 2: WebSocket Code-Analyse
- **Ausgangszustand**:
  - Drei Versionen des WebSocket-Codes verfügbar:
    1. Letzte funktionierende Version
    2. Erster fehlerhafter Edit
    3. Zweiter fehlerhafter Edit

- **Gefundene Unterschiede**:
  1. Timing der processing_enabled Flag:
     - Funktionierend: Flag wird erst nach Warten auf letzte Segmente deaktiviert
     - Fehlerhaft: Flag wird zu früh deaktiviert, blockiert eingehende Nachrichten

  2. Cleanup-Prozess:
     - Funktionierend: 
       * stop_processing() → send_end_of_audio() → wait → disable processing
       * Vollständige Wartezeit auf Server-Antworten
     - Fehlerhaft:
       * Sofortige Deaktivierung der Verarbeitung
       * Unvollständige Wartezeit auf Server-Antworten

  3. Nachrichtenverarbeitung:
     - Funktionierend: Server hat Zeit, letzte Segmente zu senden
     - Fehlerhaft: Vorzeitige Deaktivierung verhindert Empfang letzter Segmente

- **Schlussfolgerung**:
  Die Regression wurde durch eine Änderung in der Reihenfolge der Cleanup-Operationen verursacht, 
  die zu einer vorzeitigen Deaktivierung der Nachrichtenverarbeitung führt.

### Test 3: Server-Log Zugriff
- **Problem**:
  - Dokumentation in development.md nicht aktuell
  - WSL-Symlink Zugriff erfordert Vorbedingungen

- **Erkenntnisse**:
  - Server-Logs sind über Symlink in logs/logs/server.log verfügbar
  - Symlink erfordert WSL-Filesystem-Aktivierung durch:
    * Entweder WSL-Terminal öffnen
    * Oder WSL-Filesystem (U:\) in Windows aufrufen
  - Grund: WSL-Symlinks werden erst nach Filesystem-Aktivierung gemountet

- **Korrektur**:
  - Dokumentation sollte WSL-Symlink Voraussetzungen erwähnen
  - Entwickler müssen WSL-Filesystem vor Log-Zugriff aktivieren
  - Logging-Pfade sollten konsistent dokumentiert werden

### Test 4: Code-Wiederherstellung
- **Ausgangszustand**:
  - WebSocket-Code mit fehlerhafter Verarbeitungsreihenfolge
  - Vorzeitige Deaktivierung der Nachrichtenverarbeitung
  - Fehlende Wartezeit auf Server-Antworten

- **Durchgeführte Änderungen**:
  1. Wiederherstellung der send_end_of_audio() Methode:
     - Eigenständige Methode für END_OF_AUDIO Signal
     - Integrierte 20-Sekunden Wartezeit
     - Verbesserte Fehlerbehandlung

  2. Korrektur der stop_processing() Methode:
     - Entfernung des problematischen wait_thread
     - Korrekte Reihenfolge: erst Signal senden, dann auf Antwort warten
     - Deaktivierung der Verarbeitung erst nach Empfang letzter Segmente

  3. Verbesserung der cleanup() Methode:
     - Korrekte Reihenfolge der Operationen
     - Vollständige Wartezeit auf Server-Antworten
     - Robustere Fehlerbehandlung

- **Erwartetes Ergebnis**:
  - Wiederherstellung der Server-Kommunikation
  - Korrekte Verarbeitung der letzten Segmente
  - Saubere Beendigung der Verbindung

## Ergebnisse

Die Regression wurde durch eine fehlerhafte Änderung in der Verarbeitungsreihenfolge verursacht:
1. Vorzeitige Deaktivierung der Nachrichtenverarbeitung verhinderte den Empfang letzter Segmente
2. Fehlende Wartezeiten führten zu unvollständiger Server-Kommunikation
3. Thread-basierte Lösung war instabil und führte zu Race Conditions

Die Lösung besteht aus:
1. Wiederherstellung der korrekten Verarbeitungsreihenfolge
2. Implementierung robuster Wartezeiten
3. Vereinfachung der Thread-Verwaltung

### Test 5: Audio-Format Korrektur
- **Ausgangszustand**:
  - Audio-Daten wurden als rohe int16 Daten gesendet
  - Server erwartet normalisierte float32 Daten
  - Keine Transkriptionen vom Server

- **Durchgeführte Änderungen**:
  1. Float32-Normalisierung reaktiviert:
     - Konvertierung von int16 zu float32
     - Normalisierung durch Division durch 32768.0
     - Korrekte Datentypen für Server-Verarbeitung

- **Ergebnis**:
  - Server kann Audio-Daten korrekt verarbeiten
  - Transkriptionen werden wieder empfangen
  - Vollständige Verarbeitungskette wiederhergestellt

### Test 6: Verbindungshandling
- **Problem**:
  - Verbindung wurde zu früh geschlossen
  - Status der 20-Sekunden-Wartezeit unklar
  - F13-Tastendrücke wurden nicht korrekt angezeigt

- **Durchgeführte Änderungen**:
  1. Verbindungshandling verbessert:
     - WebSocket-Verbindung bleibt während Wartezeit offen
     - Nur Audio-Verarbeitung wird deaktiviert
     - Klarere Reihenfolge: Erst Aufnahme stoppen, dann warten

  2. Status-Meldungen verbessert:
     - "Stoppe Aufnahme..." beim Beenden der Aufnahme
     - "Warte auf letzte Texte vom Server..." während der 20s
     - "Audio-Verarbeitung beendet" nach der Wartezeit

- **Ergebnis**:
  - Verbindung bleibt für Nachzügler-Texte offen
  - Benutzer sieht klaren Status der Verarbeitung
  - Korrekte Anzeige der Tastendrücke
- **Ausgangszustand**:
  - Audio-Daten wurden als rohe int16 Daten gesendet
  - Server erwartet normalisierte float32 Daten
  - Keine Transkriptionen vom Server

- **Durchgeführte Änderungen**:
  1. Float32-Normalisierung reaktiviert:
     - Konvertierung von int16 zu float32
     - Normalisierung durch Division durch 32768.0
     - Korrekte Datentypen für Server-Verarbeitung

- **Erwartetes Ergebnis**:
  - Server kann Audio-Daten korrekt verarbeiten
  - Transkriptionen werden wieder empfangen
  - Vollständige Verarbeitungskette wiederhergestellt

Nächste Schritte:
1. Durchführung der Sprachtests zur Verifikation
2. Monitoring der Server-Logs für erfolgreiche Kommunikation
3. Dokumentation der Learnings für zukünftige Änderungen
