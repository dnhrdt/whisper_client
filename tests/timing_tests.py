"""
Systematische Tests für das Timing-System
"""
import time
import json
import threading
from pathlib import Path
from src.websocket import WhisperWebSocket
from src.audio import AudioManager
from src.text import TextManager
import config

class TimingTest:
    def __init__(self):
        self.ws = WhisperWebSocket()
        self.audio = AudioManager()
        self.text = TextManager()
        self.received_texts = []
        self.test_log = []
        
    def log_event(self, event_type: str, message: str, timestamp: float = None):
        """Event mit Timestamp loggen"""
        if timestamp is None:
            timestamp = time.time()
        
        self.test_log.append({
            "timestamp": timestamp,
            "type": event_type,
            "message": message
        })
    
    def on_text_received(self, segments):
        """Callback für empfangene Textsegmente"""
        timestamp = time.time()
        for segment in segments:
            text = segment.get('text', '').strip()
            if text:
                self.received_texts.append({
                    "timestamp": timestamp,
                    "text": text
                })
                self.log_event("text", f"Received: {text}", timestamp)
    
    def save_test_results(self, test_name: str):
        """Testergebnisse speichern"""
        results = {
            "test_name": test_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": {
                "WS_FINAL_WAIT": config.WS_FINAL_WAIT,
                "WS_MESSAGE_WAIT": config.WS_MESSAGE_WAIT,
                "AUDIO_BUFFER_SECONDS": config.AUDIO_BUFFER_SECONDS
            },
            "events": self.test_log,
            "received_texts": self.received_texts
        }
        
        # Speichere in tests/results
        results_dir = Path("tests/results")
        results_dir.mkdir(exist_ok=True)
        
        result_file = results_dir / f"{test_name}_{int(time.time())}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
    
    def analyze_results(self):
        """Analysiere Testergebnisse"""
        if not self.test_log:
            return "Keine Testergebnisse vorhanden"
            
        analysis = []
        
        # Zeitliche Abstände zwischen Events
        events = sorted(self.test_log, key=lambda x: x["timestamp"])
        for i in range(1, len(events)):
            delta = events[i]["timestamp"] - events[i-1]["timestamp"]
            analysis.append(f"Δt {events[i-1]['type']} → {events[i]['type']}: {delta:.3f}s")
        
        # Text-Vollständigkeit
        if self.received_texts:
            total_chars = sum(len(t["text"]) for t in self.received_texts)
            analysis.append(f"Empfangene Texte: {len(self.received_texts)}")
            analysis.append(f"Gesamtzeichen: {total_chars}")
            
            # Zeitliche Verteilung
            if len(self.received_texts) > 1:
                start = self.received_texts[0]["timestamp"]
                end = self.received_texts[-1]["timestamp"]
                duration = end - start
                analysis.append(f"Gesamtdauer: {duration:.3f}s")
                analysis.append(f"Durchschnittliche Zeit pro Text: {duration/len(self.received_texts):.3f}s")
        
        return "\n".join(analysis)

def test_complete_text_capture():
    """Test: Alle Texte müssen vollständig zurückkommen"""
    test = TimingTest()
    test.ws.set_text_callback(test.on_text_received)
    
    # Verbindung aufbauen
    test.log_event("connection", "Connecting to server")
    assert test.ws.connect(), "Verbindungsaufbau fehlgeschlagen"
    test.log_event("connection", "Connected to server")
    
    # Audio-Aufnahme starten
    test.log_event("audio", "Starting recording")
    test.ws.start_processing()
    test.audio.start_recording(test.ws.send_audio)
    
    print("\nBitte Text aus Speech Test 1.2 vorlesen.")
    print("F13 drücken zum Starten der Aufnahme")
    print("Nach dem Vorlesen F13 drücken zum Stoppen")
    
    # Warte auf Benutzer-Interaktion
    input("Drücke Enter wenn fertig...")
    
    # Ergebnisse speichern und analysieren
    test.save_test_results("complete_text_capture")
    analysis = test.analyze_results()
    print("\nTest-Analyse:")
    print(analysis)

def test_quick_stop_handling():
    """Test: Texte müssen auch bei schnellem Stopp zurückkommen"""
    test = TimingTest()
    test.ws.set_text_callback(test.on_text_received)
    
    # Verbindung aufbauen
    test.log_event("connection", "Connecting to server")
    assert test.ws.connect(), "Verbindungsaufbau fehlgeschlagen"
    test.log_event("connection", "Connected to server")
    
    # Audio-Aufnahme starten
    test.log_event("audio", "Starting recording")
    test.ws.start_processing()
    test.audio.start_recording(test.ws.send_audio)
    
    print("\nBitte einen kurzen Satz sagen (2-3 Wörter).")
    print("F13 drücken zum Starten der Aufnahme")
    print("SOFORT nach dem Satz F13 drücken zum Stoppen")
    
    # Warte auf Benutzer-Interaktion
    input("Drücke Enter wenn fertig...")
    
    # Ergebnisse speichern und analysieren
    test.save_test_results("quick_stop_handling")
    analysis = test.analyze_results()
    print("\nTest-Analyse:")
    print(analysis)

if __name__ == "__main__":
    print("Starte Timing-Tests...")
    
    print("\n1. Test: Vollständige Texterfassung")
    test_complete_text_capture()
    
    print("\n2. Test: Schnellstop-Handling")
    test_quick_stop_handling()
