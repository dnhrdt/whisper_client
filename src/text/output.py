"""
Text Output Module for the Whisper Client
Version: 1.2
Timestamp: 2025-04-20 16:41 CET

Dieses Modul enthält Funktionen zur Textausgabe, einschließlich SendMessage API
Integration und Zwischenablage-Operationen.
"""

import time

import pyperclip
import win32api
import win32clipboard
import win32con
import win32gui

import config
from src import logger
from src.logging import log_debug, log_error, log_info, log_warning

from .test_handler import handle_test_mode_output
from .window import find_vscode_edit_control


def send_message(hwnd, text):
    """Sends text to a window using the SendMessage API."""
    try:
        # Get window class name
        class_name = win32gui.GetClassName(hwnd)
        log_debug(logger, "Window class: %s", class_name)

        # Send appropriate message based on control type
        if class_name in ["Edit", "RichEdit", "RichEdit20W", "RICHEDIT50W"]:
            # For edit controls, use EM_REPLACESEL
            win32gui.SendMessage(hwnd, win32con.EM_REPLACESEL, 1, text)
            log_info(logger, "✓ Text sent to edit control %d using EM_REPLACESEL", hwnd)
        else:
            # For other controls, use WM_SETTEXT
            win32gui.SendMessage(hwnd, win32con.WM_SETTEXT, 0, text)
            log_info(logger, "✓ Text sent to window %d using WM_SETTEXT", hwnd)

        return True
    except Exception as e:
        log_error(logger, "⚠️ Error sending text: %s", e)
        return False


def set_clipboard_text(text):
    """Copy text to clipboard using multiple methods"""
    # Primary method: Win32 API
    try:
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardText(text, win32clipboard.CF_UNICODETEXT)
        win32clipboard.CloseClipboard()
        return
    except Exception as e:
        log_debug(logger, "Win32 Clipboard error: %s", e)

    # Backup: pyperclip
    try:
        pyperclip.copy(text)
    except Exception as e:
        log_error(logger, "⚠️ Clipboard error: %s", e)


def send_paste_command():
    """Sends Ctrl+V key combination"""
    try:
        # Simulate Ctrl+V
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Press Ctrl
        win32api.keybd_event(ord("V"), 0, 0, 0)  # Press V
        time.sleep(config.KEY_PRESS_DELAY)  # Delay between key presses
        win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)  # Release V
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Ctrl
        time.sleep(config.KEY_PRESS_DELAY)  # Delay for processing
    except Exception as e:
        log_error(logger, "⚠️ Error during keyboard input: %s", e)
        raise


def send_text_to_prompt(text):
    """Sends text directly to the prompt"""
    try:
        # Copy text to clipboard
        set_clipboard_text(text)

        # Ctrl+V to paste
        win32api.keybd_event(win32con.VK_CONTROL, 0, 0, 0)  # Press Ctrl
        win32api.keybd_event(ord("V"), 0, 0, 0)  # Press V
        time.sleep(config.KEY_PRESS_DELAY)  # Delay between key presses
        win32api.keybd_event(ord("V"), 0, win32con.KEYEVENTF_KEYUP, 0)  # Release V
        win32api.keybd_event(win32con.VK_CONTROL, 0, win32con.KEYEVENTF_KEYUP, 0)  # Release Ctrl

        # Press Enter
        time.sleep(0.05)  # Short pause
        win32api.keybd_event(win32con.VK_RETURN, 0, 0, 0)
        win32api.keybd_event(win32con.VK_RETURN, 0, win32con.KEYEVENTF_KEYUP, 0)
        time.sleep(config.PROMPT_SUBMIT_DELAY)

    except Exception as e:
        log_error(logger, "⚠️ Error during prompt input: %s", e)
        raise


def insert_text(manager, text):
    """Output text based on configured mode"""
    try:
        # Save text for tests
        manager.test_output.append(text)

        # In test mode, only capture the output without actually inserting it
        if handle_test_mode_output(manager, text):
            return

        # Copy text to clipboard for all modes (as fallback)
        set_clipboard_text(text)
        log_info(logger, "\n📋 Processed: %s", text)
        log_info(logger, "Output mode: %s", config.OUTPUT_MODE)

        # Write to test log file
        with open("tests/speech_test_output.log", "a", encoding="utf-8") as f:
            f.write(f"{time.strftime('%Y-%m-%d %H:%M:%S')} - {text}\n")

        # Identify active window
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            log_warning(logger, "⚠️ No active window found")
            return

        # Check if it's VS Code
        window_title = win32gui.GetWindowText(hwnd)
        is_vscode = "Visual Studio Code" in window_title
        if is_vscode:
            log_debug(logger, "Detected VS Code window: %s", window_title)

        # Find edit control for VS Code
        edit_hwnd = None
        if is_vscode:
            edit_hwnd = find_vscode_edit_control(hwnd)
            if edit_hwnd:
                log_debug(logger, "Found VS Code edit control: %d", edit_hwnd)

        # Insert text into active window
        if config.OUTPUT_MODE == config.OutputMode.PROMPT:
            send_text_to_prompt(text)
            log_info(logger, "✓ Text sent to active window using prompt mode")
        elif config.OUTPUT_MODE == config.OutputMode.SENDMESSAGE:
            # Try SendMessage with the appropriate window handle
            target_hwnd = edit_hwnd if edit_hwnd else hwnd
            success = send_message(target_hwnd, text)

            # Fallback to clipboard if SendMessage fails
            if not success:
                log_warning(logger, "⚠️ SendMessage failed, falling back to clipboard")
                send_paste_command()
                log_info(logger, "✓ Inserted using clipboard fallback")
            else:
                log_info(logger, "✓ Text sent using SendMessage API")
        elif config.OUTPUT_MODE == config.OutputMode.CLIPBOARD:
            send_paste_command()
            log_info(logger, "✓ Inserted using clipboard")
        elif config.OUTPUT_MODE == config.OutputMode.BOTH:
            # Try SendMessage first
            target_hwnd = edit_hwnd if edit_hwnd else hwnd
            success = send_message(target_hwnd, text)

            # Always do prompt mode
            send_text_to_prompt(text)

            log_info(logger, "✓ Text sent using both methods")

    except Exception as e:
        log_error(logger, "⚠️ Error during text input: %s", e)
        log_info(logger, "⌨️  Alternative: Press Ctrl+V to paste manually")
