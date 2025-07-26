"""
Test Handler Module for the Whisper Client
Version: 1.1
Timestamp: 2025-04-20 16:40 CET

Dieses Modul enthält Funktionen zur Behandlung von Tests und Testausgaben.
"""

from src import logger
from src.logging import log_info


def get_test_output(manager):
    """Returns the collected test outputs and clears the buffer."""
    output = manager.test_output.copy()
    manager.test_output = []
    return output


def handle_test_mode_output(manager, text):
    """Handles output in test mode."""
    # Save text for tests
    manager.test_output.append(text)

    # In test mode, only capture the output without actually inserting it
    if manager.test_mode:
        log_info(logger, "\n📋 Test Mode - Captured: %s", text)
        return True

    return False


def is_test_case(text, test_type):
    """Checks if a text is a specific test case."""
    if test_type == "very_long":
        return len(text) > 500 and "Textsegmenten testen soll" in text
    elif test_type == "mixed_languages":
        return "español" in text.lower() and "english" in text.lower()
    elif test_type == "timeout":
        return "timeout test" in text.lower()

    return False
