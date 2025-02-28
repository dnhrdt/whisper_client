"""
Text Processing Module for the Whisper Client
Version: 1.1
Timestamp: 2025-02-28 18:14 CET

This module handles text processing, formatting, and output for the Whisper Client.
It includes functionality for sentence detection, duplicate handling, and text insertion
using various methods including Windows SendMessage API.
"""
import time
import win32gui
import win32con
import win32api
import win32clipboard
import pyperclip
import config
from src import logger

def send_message(hwnd, text):
    """Sends text to a window using the SendMessage API."""
    try:
        # Get window class name
        class_name = win32gui.GetClassName(hwnd)
        logger.debug(f"Window class: {class_name}")
        
        # Send appropriate message based on control type
        if class_name in ["Edit", "RichEdit", "RichEdit20W", "RICHEDIT50W"]:
            # For edit controls, use EM_REPLACESEL
            win32gui.SendMessage(hwnd, win32con.EM_REPLACESEL, 1, text)
            logger.info(f"✓ Text sent to edit control {hwnd} using EM_REPLACESEL")
        else:
            # For other controls, use WM_SETTEXT
            win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
            logger.info(f"✓ Text sent to window {hwnd} using WM_SETTEXT")
        
        return True
    except Exception as e:
        logger.error(f"⚠️ Error sending text: {e}")
        return False

class TextManager:
    def __init__(self):
        self.current_sentence = []  # Collects segments for complete sentences
        self.last_output_time = 0  # Timestamp of the last output
        self.incomplete_sentence_time = 0  # Timestamp for incomplete sentences
        self.processed_segments = set()  # Set of already processed segments
        self.common_abbreviations = {
            "Dr.", "Prof.", "Hr.", "Fr.", "Nr.", "Tel.", "Str.", "z.B.", "d.h.", "u.a.",
            "etc.", "usw.", "bzw.", "ca.", "ggf.", "inkl.", "max.", "min.", "vs."
        }
        self.test_output = []  # Stores outputs during testing
    
    def is_duplicate(self, text):
        """Checks if a text is a duplicate"""
        # Normalize text for comparison
        normalized_text = ' '.join(text.lower().split())
        return normalized_text in self.processed_segments

    def is_sentence_end(self, text):
        """Checks if a text marks the end of a sentence"""
        # Check for abbreviations at the end of the text
        text_lower = text.lower()
        for abbr in self.common_abbreviations:
            if text_lower.endswith(abbr.lower()) and not any(
                text_lower.endswith(abbr.lower() + p) 
                for p in config.SENTENCE_END_MARKERS
            ):
                return False
        # Check for sentence punctuation
        return any(text.endswith(p) for p in config.SENTENCE_END_MARKERS)

    def output_sentence(self, current_time=None):
        """Outputs the current sentence"""
        if not self.current_sentence:
            return
            
        if current_time is None:
            current_time = time.time()
            
        complete_text = self.format_sentence(' '.join(self.current_sentence))
        self.insert_text(complete_text)
        self.current_sentence = []
        self.last_output_time = current_time
        self.incomplete_sentence_time = current_time
        
        # Clear the processed segments
        self.processed_segments.clear()

    def should_force_output(self, current_time):
        """Checks if the current sentence should be output"""
        if not self.current_sentence:
            return False
            
        # Check for timeout
        if current_time - self.incomplete_sentence_time > config.MAX_SENTENCE_WAIT:
            return True
            
        # Check for complete sentence
        current_text = ' '.join(self.current_sentence)
        if any(current_text.endswith(marker) for marker in config.SENTENCE_END_MARKERS):
            return True
            
        return False

    def process_segments(self, segments):
        """Processes received text segments"""
        logger.info("\n🎯 Processing new text segments:")
        current_time = time.time()
        
        # Get the last text from the segments
        if not segments:
            return
            
        last_segment = segments[-1]
        text = last_segment.get("text", "").strip()
        if not text:
            return
            
        logger.info(f"  → Segment: {text}")
        
        # Split text into sentences
        sentences = []
        current_sentence = ""
        
        # Go through each character
        for i, char in enumerate(text):
            current_sentence += char
            
            # Check for sentence end
            if any(text[i-len(marker)+1:i+1] == marker for marker in config.SENTENCE_END_MARKERS if i >= len(marker)-1):
                # Check for abbreviations
                is_abbreviation = False
                for abbr in self.common_abbreviations:
                    if current_sentence.strip().lower().endswith(abbr.lower()):
                        is_abbreviation = True
                        break
                
                if not is_abbreviation:
                    sentences.append(current_sentence.strip())
                    current_sentence = ""
        
        # Add the rest
        if current_sentence.strip():
            sentences.append(current_sentence.strip())
        
        # Process each sentence individually
        for sentence in sentences:
            # Normalize text for duplicate detection
            normalized_text = ' '.join(sentence.lower().split())
            
            # Check for duplicates
            if normalized_text in self.processed_segments:
                logger.info(f"    ⚠️ Duplicate skipped: {sentence}")
                continue
                
            # Save text for duplicate detection
            self.processed_segments.add(normalized_text)
            
            # Update timestamp for incomplete sentences
            if not self.current_sentence:
                self.incomplete_sentence_time = current_time
            
            # Add text to the current sentence
            if not self.current_sentence:
                self.current_sentence = [sentence]
            else:
                # Check if the new text contains the old one
                old_text = ' '.join(self.current_sentence)
                if sentence.startswith(old_text):
                    self.current_sentence = [sentence]
                else:
                    self.current_sentence.append(sentence)
            logger.info(f"    ✓ Added to sentence: {sentence}")
            
            # Check if output is necessary
            if self.should_force_output(current_time):
                logger.info("    ⚡ Output is forced")
                # Wait only if necessary
                wait_time = config.MIN_OUTPUT_INTERVAL - (current_time - self.last_output_time)
                if wait_time > 0:
                    time.sleep(wait_time)
                self.output_sentence(current_time)

    def format_sentence(self, text):
        """Formats a sentence for output"""
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Ensure that punctuation marks are set correctly
        for marker in config.SENTENCE_END_MARKERS:
            if marker in text and not text.endswith(marker):
                text = text.replace(marker, marker + ' ')
        
        # Check if the text is part of a larger sentence
        starts_sentence = not any(
            text.lower().startswith(word) for word in ['und', 'oder', 'aber', 'denn']
        )
        
        # First letter uppercase if it's the beginning of a sentence
        if text and starts_sentence and not any(text.startswith(abbr) for abbr in self.common_abbreviations):
            text = text[0].upper() + text[1:]
            
        return text
    
    def insert_text(self, text):
        """Output text based on configured mode"""
        try:
            # Copy text to clipboard for all modes (as fallback)
            self._set_clipboard_text(text)
            logger.info(f"\n📋 Processed: {text}")
            logger.info(f"Output mode: {config.OUTPUT_MODE}")
            
            # Save text for tests
            self.test_output.append(text)
            
            # Write to test log file
            with open("tests/speech_test_output.log", "a", encoding="utf-8") as f:
                f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")
            
            # Identify active window
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                logger.warning("⚠️ No active window found")
                return
            
            # Check if it's VS Code
            window_title = win32gui.GetWindowText(hwnd)
            is_vscode = "Visual Studio Code" in window_title
            if is_vscode:
                logger.debug(f"Detected VS Code window: {window_title}")
            
            # Find edit control for VS Code
            edit_hwnd = None
            if is_vscode:
                edit_hwnd = self._find_vscode_edit_control(hwnd)
                if edit_hwnd:
                    logger.debug(f"Found VS Code edit control: {edit_hwnd}")
            
            # Insert text into active window
            if config.OUTPUT_MODE == config.OutputMode.PROMPT:
                self._send_text_to_prompt(text)
                logger.info("✓ Text sent to active window using prompt mode")
            elif config.OUTPUT_MODE == config.OutputMode.SENDMESSAGE:
                # Try SendMessage with the appropriate window handle
                target_hwnd = edit_hwnd if edit_hwnd else hwnd
                success = send_message(target_hwnd, text)
                
                # Fallback to clipboard if SendMessage fails
                if not success:
                    logger.warning("⚠️ SendMessage failed, falling back to clipboard")
                    self._send_paste_command()
                    logger.info("✓ Inserted using clipboard fallback")
                else:
                    logger.info("✓ Text sent using SendMessage API")
            elif config.OUTPUT_MODE == config.OutputMode.CLIPBOARD:
                self._send_paste_command()
                logger.info("✓ Inserted using clipboard")
            elif config.OUTPUT_MODE == config.OutputMode.BOTH:
                # Try SendMessage first
                target_hwnd = edit_hwnd if edit_hwnd else hwnd
                success = send_message(target_hwnd, text)
                
                # Always do prompt mode
                self._send_text_to_prompt(text)
                
                logger.info("✓ Text sent using both methods")
            
        except Exception as e:
            logger.error(f"⚠️ Error during text input: {e}")
            logger.info("⌨️  Alternative: Press Ctrl+V to paste manually")
    
    def _set_clipboard_text(self, text):
        """Copy text to clipboard using multiple methods"""
        # Primary method: Win32 API
        try:
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
            win32clipboard.CloseClipboard()
            return
        except Exception as e:
            logger.debug(f"Win32 Clipboard error: {e}")
            
        # Backup: pyperclip
        try:
            pyperclip.copy(text)
        except Exception as e:
            logger.error(f"⚠️ Clipboard error: {e}")
    
    def _send_paste_command(self):
        """Sends Ctrl+V key combination"""
        try:
            # Simulate Ctrl+V
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Press Ctrl
            win32api.keybd_event(ord('V'), 0, 0, 0)  # Press V
            time.sleep(config.KEY_PRESS_DELAY)  # Delay between key presses
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # Release V
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Ctrl
            time.sleep(config.KEY_PRESS_DELAY)  # Delay for processing
        except Exception as e:
            logger.error(f"⚠️ Error during keyboard input: {e}")
            raise
    
    def _find_prompt_window(self):
        """Finds the prompt window by title"""
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
            logger.error(f"⚠️ Error during window search: {e}")
            return None
    
    def _send_text_to_prompt(self, text):
        """Sends text directly to the prompt"""
        try:
            # Copy text to clipboard
            self._set_clipboard_text(text)
            
            # Ctrl+V to paste
            win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Press Ctrl
            win32api.keybd_event(ord('V'), 0, 0, 0)  # Press V
            time.sleep(config.KEY_PRESS_DELAY)  # Delay between key presses
            win32api.keybd_event(ord('V'), 0, win32con.KEYEVENTF_KEYUP, 0)  # Release V
            win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Ctrl
            
            # Press Enter
            time.sleep(0.05)  # Short pause
            win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
            win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
            time.sleep(config.PROMPT_SUBMIT_DELAY)
            
        except Exception as e:
            logger.error(f"⚠️ Error during prompt input: {e}")
            raise
    
    def _find_vscode_edit_control(self, parent_hwnd):
        """Find the edit control within VS Code"""
        result = []
        
        # VS Code uses a complex structure with Electron/Chromium
        # We need to search more deeply for potential edit areas
        def callback(hwnd, controls):
            class_name = win32gui.GetClassName(hwnd)
            # Log all controls for debugging
            text = win32gui.GetWindowText(hwnd)
            if text or class_name not in ["", "Static"]:
                logger.debug(f"Control: {hwnd}, Class: {class_name}, Text: {text[:20] + '...' if len(text) > 20 else text}")
            
            # Look for potential edit controls
            if class_name in ["Edit", "RichEdit", "RichEdit20W", "RICHEDIT50W"]:
                controls.append((hwnd, class_name, "standard_edit"))
            # VS Code's main editor might be in Chromium's structure
            elif class_name == "Chrome_RenderWidgetHostHWND":
                controls.append((hwnd, class_name, "chrome_render"))
            # Electron apps often use Atom as a base
            elif "Atom" in class_name:
                controls.append((hwnd, class_name, "atom"))
            # Look for the Monaco editor component
            elif "Monaco" in text or "monaco" in text.lower():
                controls.append((hwnd, class_name, "monaco"))
            return True
        
        try:
            # First try direct children
            win32gui.EnumChildWindows(parent_hwnd, callback, result)
            
            if not result:
                # If no results, try a recursive approach to find deeper controls
                def recursive_find(hwnd, depth=0, max_depth=5):
                    if depth > max_depth:
                        return
                    
                    try:
                        win32gui.EnumChildWindows(hwnd, lambda child_hwnd, _: (
                            callback(child_hwnd, result),
                            recursive_find(child_hwnd, depth + 1, max_depth)
                        ), None)
                    except Exception:
                        pass  # Some windows might not allow enumeration
                
                recursive_find(parent_hwnd)
            
            if result:
                logger.debug(f"Found {len(result)} potential edit controls in VS Code")
                for i, (hwnd, class_name, control_type) in enumerate(result):
                    logger.debug(f"  {i+1}. Handle: {hwnd}, Class: {class_name}, Type: {control_type}")
                
                # Prioritize standard edit controls if found
                for hwnd, _, control_type in result:
                    if control_type == "standard_edit":
                        return hwnd
                
                # Otherwise return the first control found
                return result[0][0]
            else:
                logger.debug("No potential edit controls found in VS Code")
                # If no edit control found, return the parent window as fallback
                return parent_hwnd
        except Exception as e:
            logger.error(f"⚠️ Error finding VS Code edit control: {e}")
            # Return parent window as fallback
            return parent_hwnd
    
    def get_test_output(self):
        """Returns the collected test outputs and clears the buffer"""
        output = self.test_output.copy()
        self.test_output = []
        return output
