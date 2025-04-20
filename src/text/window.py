"""
Window Management Module for the Whisper Client
Version: 1.4
Timestamp: 2025-04-20 18:12 CET

Dieses Modul stellt Funktionen zur Fenstererkennung und -manipulation bereit,
einschließlich VS Code-spezifischer Funktionen.
"""

from typing import List, Tuple

import win32gui

import config
from src import logger
from src.logging import log_debug, log_error


def find_prompt_window():
    """Finds the prompt window by title"""
    try:
        prompt_window_title = config.PROMPT_WINDOW_TITLE

        def callback(hwnd, windows):
            if win32gui.IsWindowVisible(hwnd):
                title = win32gui.GetWindowText(hwnd)
                if prompt_window_title.lower() in title.lower():
                    windows.append(hwnd)
                return True

        windows: List[int] = []
        win32gui.EnumWindows(callback, windows)
        return windows[0] if windows else None

    except Exception as e:
        log_error(logger, "⚠️ Error during window search: %s", e)
        return None


def find_vscode_edit_control(parent_hwnd):
    """Find the edit control within VS Code"""
    result: List[Tuple[int, str, str]] = []

    # VS Code uses a complex structure with Electron/Chromium
    # We need to search more deeply for potential edit areas
    def callback(hwnd, controls):
        class_name = win32gui.GetClassName(hwnd)
        # Log all controls for debugging
        text = win32gui.GetWindowText(hwnd)
        if text or class_name not in ["", "Static"]:
            log_debug(
                logger,
                "Control: %d, Class: %s, Text: %s",
                hwnd,
                class_name,
                text[:20] + "..." if len(text) > 20 else text,
            )

        # Look for potential edit controls
        # Ensure class_name is not None before using 'in'
        edit_classes = ["Edit", "RichEdit", "RichEdit20W", "RICHEDIT50W"]
        if class_name is not None:
            if any(edit_class == class_name for edit_class in edit_classes):
                controls.append((hwnd, class_name, "standard_edit"))
            # VS Code's main editor might be in Chromium's structure
            elif class_name == "Chrome_RenderWidgetHostHWND":
                controls.append((hwnd, class_name, "chrome_render"))
            # Electron apps often use Atom as a base
            elif "Atom" in class_name:
                controls.append((hwnd, class_name, "atom"))
            # Look for the Monaco editor component
            elif text is not None and ("Monaco" in text or "monaco" in text.lower()):
                controls.append((hwnd, class_name, "monaco"))
        return 1  # Continue enumeration

    try:
        # First try direct children
        win32gui.EnumChildWindows(parent_hwnd, callback, result)

        if not result:
            # If no results, try a recursive approach to find deeper controls
            def recursive_find(hwnd, depth=0, max_depth=5):
                if depth > max_depth:
                    return

                try:
                    # Korrigierte Version der Lambda-Funktion
                    def recursive_callback(child_hwnd, _):
                        callback(child_hwnd, result)
                        recursive_find(child_hwnd, depth + 1, max_depth)
                        return 1  # Ensure we return an integer

                    win32gui.EnumChildWindows(hwnd, recursive_callback, None)
                except Exception:
                    pass  # Some windows might not allow enumeration

            recursive_find(parent_hwnd)

        if result:
            log_debug(logger, "Found %d potential edit controls in VS Code", len(result))
            for i, (hwnd, class_name, control_type) in enumerate(result):
                log_debug(
                    logger,
                    "  %d. Handle: %d, Class: %s, Type: %s",
                    i + 1,
                    hwnd,
                    class_name,
                    control_type,
                )

            # Prioritize standard edit controls if found
            for hwnd, _, control_type in result:
                if control_type == "standard_edit":
                    return hwnd

            # Otherwise return the first control found
            return result[0][0]
        else:
            log_debug(logger, "No potential edit controls found in VS Code")
            # If no edit control found, return the parent window as fallback
            return parent_hwnd
    except Exception as e:
        log_error(logger, "⚠️ Error finding VS Code edit control: %s", e)
        # Return parent window as fallback
        return parent_hwnd
