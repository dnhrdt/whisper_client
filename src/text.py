"""
Text-Verarbeitungsmodul für den Whisper-Client
"""
import time
import win32gui
import win32con
import win32api
import win32clipboard
import pyperclip
from src import logging
import config

logger = logging.get_logger()

class TextManager:
    def __init__(self):
        self.recent_transcriptions = []  # Liste der letzten Transkriptionen
        self.current_sentence = []  # Sammelt Segmente für vollständige Sätze
        self.last_output_time = 0  # Zeitstempel der letzten Ausgabe
        self.incomplete_sentence_time = 0  # Zeitstempel für unvollständige Sätze
        self.common_abbreviations = {
            "Dr.", "Prof.", "Hr.", "Fr.", "Nr.", "Tel.", "Str.", "z.B.", "d.h.", "u.a.",
            "etc.", "usw.", "bzw.", "ca.", "ggf.", "inkl.", "max.", "min.", "vs."
        }
    
    def is_duplicate(self, text):
        """Prüft, ob ein Text ein Duplikat ist"""
        # Normalisiere Text für Vergleich
        normalized_text = ' '.join(text.lower().split())
        
        # Prüfe auch gegen den aktuellen unvollständigen Satz
        current_text = ' '.join(self.current_sentence).lower()
        if normalized_text in current_text:
            return True
        
        for recent in self.recent_transcriptions:
            normalized_recent = ' '.join(recent.lower().split())
            # Prüfe auf exakte Übereinstimmung
            if normalized_text == normalized_recent:
                return True
            # Prüfe auf Teilstring-Übereinstimmung
            if len(normalized_text) > 5:
                if normalized_text in normalized_recent:
                    return True
        return False

    def is_sentence_end(self, text):
        """Prüft, ob ein Text ein Satzende markiert"""
        # Prüfe auf Abkürzungen am Ende des Texts
        text_lower = text.lower()
        for abbr in self.common_abbreviations:
            if text_lower.endswith(abbr.lower()) and not any(
                text_lower.endswith(abbr.lower() + p) 
                for p in config.SENTENCE_END_MARKERS
            ):
                return False
        # Prüfe auf Satzzeichen
        return any(text.endswith(p) for p in config.SENTENCE_END_MARKERS)

    def output_sentence(self, current_time=None):
        """Gibt den aktuellen Satz aus"""
        if not self.current_sentence:
            return
            
        if current_time is None:
            current_time = time.time()
            
        complete_text = self.format_sentence(' '.join(self.current_sentence))
        self.insert_text(complete_text)
        self.recent_transcriptions.append(complete_text)
        if len(self.recent_transcriptions) > config.MAX_RECENT_TRANSCRIPTIONS:
            self.recent_transcriptions.pop(0)
        self.current_sentence = []
        self.last_output_time = current_time
        self.incomplete_sentence_time = current_time

    def should_force_output(self, current_time):
        """Prüft ob der aktuelle Satz ausgegeben werden soll"""
        if not self.current_sentence:
            return False
            
        # Prüfe auf Timeout
        if current_time - self.incomplete_sentence_time > config.MAX_SENTENCE_WAIT:
            return True
            
        # Prüfe auf kompletten Satz
        current_text = ' '.join(self.current_sentence)
        if any(current_text.endswith(marker) for marker in config.SENTENCE_END_MARKERS):
            return True
            
        return False

    def process_segments(self, segments):
        """Verarbeitet empfangene Textsegmente"""
        current_time = time.time()
        
        for segment in segments:
            text = segment.get("text", "").strip()
            if not text:
                continue
                
            if self.is_duplicate(text):
                continue
            
            # Aktualisiere Zeitstempel für unvollständige Sätze
            if not self.current_sentence:
                self.incomplete_sentence_time = current_time
            
            # Füge Text zum aktuellen Satz hinzu
            if self.current_sentence and not text.startswith(" "):
                text = " " + text
            self.current_sentence.append(text)
            
            # Prüfe ob Ausgabe nötig
            if self.should_force_output(current_time):
                # Warte nur wenn nötig
                wait_time = config.MIN_OUTPUT_INTERVAL - (current_time - self.last_output_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                self.output_sentence(current_time)

    def format_sentence(self, text):
        """Formatiert einen Satz für die Ausgabe"""
        # Entferne mehrfache Leerzeichen
        text = ' '.join(text.split())
        
        # Stelle sicher, dass Satzzeichen korrekt gesetzt sind
        for marker in config.SENTENCE_END_MARKERS:
            if marker in text and not text.endswith(marker):
                text = text.replace(marker, marker + ' ')
        
        # Prüfe ob der Text Teil eines größeren Satzes ist
        starts_sentence = not any(
            text.lower().startswith(word) for word in ['und', 'oder', 'aber', 'denn']
        )
        
        # Erste Buchstabe groß wenn es ein Satzanfang ist
        if text and starts_sentence and not any(text.startswith(abbr) for abbr in self.common_abbreviations):
            text = text[0].upper() + text[1:]
            
        return text
    
    def insert_text(self, text):
        """Text in die Zwischenablage kopieren und einfügen"""
        try:
            # Text in Zwischenablage kopieren (mit Backup-Methode)
            self._set_clipboard_text(text)
            logger.info(f"\n📋 Verarbeitet: {text}")
            
            # Aktives Fenster identifizieren
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                logger.warning("⚠️ Kein aktives Fenster gefunden")
                return
                
            # Text einfügen
            self._send_paste_command()
            logger.info("✓ Eingefügt")
            
        except Exception as e:
            logger.error(f"⚠️ Fehler beim Einfügen: {e}")
            logger.info("⌨️  Alternativ: Drücke Strg+V zum manuellen Einfügen")
    
    def _set_clipboard_text(self, text):
        """Text in die Zwischenablage kopieren mit mehreren Methoden"""
        # Primäre Methode: Win32 API
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return
        except Exception as e:
            logger.debug(f"Win32 Clipboard Fehler: {e}")
            
        # Backup: pyperclip
        try:
            pyperclip.copy(text)
        except Exception as e:
            logger.error(f"⚠️ Clipboard Fehler: {e}")
    
    def _send_paste_command(self):
        """Sendet Strg+V Tastenkombination"""
        try:
            # Simuliere Strg+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Strg drücken
            win32api.keybd_event(ord('V'), 0, 0, 0)  # V drücken
            time.sleep(0.05)  # Kurze Pause
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V loslassen
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Strg loslassen
            time.sleep(0.05)  # Kurze Pause für Verarbeitung
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Tastatureingabe: {e}")
            raise
