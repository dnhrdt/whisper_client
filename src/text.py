"""
Text-Verarbeitungsmodul für den Whisper-Client
"""
import time
import win32gui
import win32con
import win32api
import win32clipboard
import pyperclip
import config
from src import logger

class TextManager:
    def __init__(self):
        self.current_sentence = []  # Sammelt Segmente für vollständige Sätze
        self.last_output_time = 0  # Zeitstempel der letzten Ausgabe
        self.incomplete_sentence_time = 0  # Zeitstempel für unvollständige Sätze
        self.processed_segments = set()  # Menge der bereits verarbeiteten Segmente
        self.common_abbreviations = {
            "Dr.", "Prof.", "Hr.", "Fr.", "Nr.", "Tel.", "Str.", "z.B.", "d.h.", "u.a.",
            "etc.", "usw.", "bzw.", "ca.", "ggf.", "inkl.", "max.", "min.", "vs."
        }
        self.test_output = []  # Speichert Ausgaben während des Tests
    
    def is_duplicate(self, text):
        """Prüft, ob ein Text ein Duplikat ist"""
        # Normalisiere Text für Vergleich
        normalized_text = ' '.join(text.lower().split())
        return normalized_text in self.processed_segments

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
        self.current_sentence = []
        self.last_output_time = current_time
        self.incomplete_sentence_time = current_time
        
        # Leere die verarbeiteten Segmente
        self.processed_segments.clear()

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
        logger.info("\n🎯 Verarbeite neue Textsegmente:")
        current_time = time.time()
        
        # Hole den letzten Text aus den Segmenten
        if not segments:
            return
            
        last_segment = segments[-1]
        text = last_segment.get("text", "").strip()
        if not text:
            return
            
        logger.info(f"  → Segment: {text}")
        
        # Teile Text in Sätze
        sentences = []
        current_sentence = ""
        
        # Gehe durch jeden Buchstaben
        for i, char in enumerate(text):
            current_sentence += char
            
            # Prüfe auf Satzende
            if any(text[i-len(marker)+1:i+1] == marker for marker in config.SENTENCE_END_MARKERS if i >= len(marker)-1):
                # Prüfe auf Abkürzungen
                is_abbreviation = False
                for abbr in self.common_abbreviations:
                    if current_sentence.strip().lower().endswith(abbr.lower()):
                        is_abbreviation = True
                        break
                
                if not is_abbreviation:
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Rest hinzufügen
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Verarbeite jeden Satz einzeln
        for sentence in sentences:
            # Normalisiere Text für Duplikatserkennung
            normalized_text = ' '.join(sentence.lower().split())
            
            # Prüfe auf Duplikate
            if normalized_text in self.processed_segments:
                logger.info(f"    ⚠️ Duplikat übersprungen: {sentence}")
                continue
                
            # Speichere Text für Duplikatserkennung
            self.processed_segments.add(normalized_text)
            
            # Aktualisiere Zeitstempel für unvollständige Sätze
            if not self.current_sentence:
                self.incomplete_sentence_time = current_time
            
            # Füge Text zum aktuellen Satz hinzu
            if not self.current_sentence:
                self.current_sentence = [sentence]
            else:
                # Prüfe ob der neue Text den alten enthält
                old_text = ' '.join(self.current_sentence)
                if sentence.startswith(old_text):
                    self.current_sentence = [sentence]
                else:
                    self.current_sentence.append(sentence)
            logger.info(f"    ✓ Zum Satz hinzgefügt: {sentence}")
            
            # Prüfe ob Ausgabe nötig
            if self.should_force_output(current_time):
                logger.info("    ⚡ Ausgabe wird erzwungen")
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
        """Text ausgeben basierend auf konfiguriertem Modus"""
        try:
            # Text in Zwischenablage kopieren für alle Modi
            self._set_clipboard_text(text)
            logger.info(f"\n📋 Verarbeitet: {text}")
            logger.info(f"Ausgabemodus: {config.OUTPUT_MODE}")
            
            # Speichere Text für Tests
            self.test_output.append(text)
            
            # Schreibe in Test-Log-Datei
            with open("tests/speech_test_output.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
            
            # Aktives Fenster identifizieren
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                logger.warning("⚠️ Kein aktives Fenster gefunden")
                return
            
            # Text in aktives Fenster einfügen
            if config.OUTPUT_MODE in [config.OutputMode.PROMPT, config.OutputMode.BOTH]:
                self._send_text_to_prompt(text)
                logger.info("✓ Text an aktives Fenster gesendet")
            elif config.OUTPUT_MODE == config.OutputMode.CLIPBOARD:
                self._send_paste_command()
                logger.info("✓ In Zwischenablage eingefügt")
            
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Texteingabe: {e}")
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
            time.sleep(config.KEY_PRESS_DELAY)  # Verzögerung zwischen Tastendrücken
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V loslassen
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Strg loslassen
            time.sleep(config.KEY_PRESS_DELAY)  # Verzögerung für Verarbeitung
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Tastatureingabe: {e}")
            raise
    
    def _find_prompt_window(self):
        """Findet das Prompt-Fenster anhand des Titels"""
        try:
            def callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if config.PROMPT_WINDOW_TITLE.lower() in title.lower():
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(callback, windows)
            return windows[0] if windows else None
            
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Fenstersuche: {e}")
            return None
    
    def _send_text_to_prompt(self, text):
        """Sendet Text direkt an den Prompt"""
        try:
            # Text in Zwischenablage kopieren
            self._set_clipboard_text(text)
            
            # Strg+V zum Einfügen
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Strg drücken
            win32api.keybd_event(ord('V'), 0, 0, 0)  # V drücken
            time.sleep(config.KEY_PRESS_DELAY)  # Verzögerung zwischen Tastendrücken
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # V loslassen
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Strg loslassen
            
            # Enter drücken
            time.sleep(0.05)  # Kurze Pause
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(config.PROMPT_SUBMIT_DELAY)
            
        except Exception as e:
            logger.error(f"⚠️ Fehler bei Prompt-Eingabe: {e}")
            raise
    
    def get_test_output(self):
        """Gibt die gesammelten Test-Ausgaben zurück und leert den Puffer"""
        output = self.test_output.copy()
        self.test_output = []
        return output
