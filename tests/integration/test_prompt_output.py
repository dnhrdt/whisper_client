"""
Prompt Window Output Test Script
Version: 1.0
Timestamp: 2025-02-26 22:34 CET
"""

import sys
import time
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import config
from src import logging
from src.text import TextManager

# Configure logger for tests
logger = logging.get_logger()
config.LOG_LEVEL_CONSOLE = "DEBUG"


def test_prompt_output():
    """Tests text output to the prompt window."""
    print("\n🧪 Testing Prompt Output...")
    print("=" * 50)

    # Initialize TextManager
    manager = TextManager()

    # Store original insert_text method
    original_insert = manager.insert_text
    output_history = []

    def mock_insert_text(self, text):
        """Mock for insert_text that logs outputs."""
        output_history.append({"timestamp": time.time(), "text": text})
        print(f"\n[{len(output_history)}] Output:")
        print("-" * 20)
        print(text)
        print("-" * 20)

    # Set mock function
    TextManager.insert_text = mock_insert_text

    try:
        print("\nTest 1: Multiple Short Sentences")
        print("-" * 30)
        segments = [
            {"text": "This is the first sentence."},
            {"text": "This is the second sentence."},
            {"text": "And the third sentence."},
        ]

        for segment in segments:
            print(f"\nInput: {segment['text']}")
            manager.process_segments([segment])
            time.sleep(0.5)  # Pause between segments

        print("\nTest 2: Sentence with Pauses")
        print("-" * 30)
        segments = [
            {"text": "This is a sentence"},
            {"text": " with a pause"},
            {"text": " between parts."},
        ]

        for segment in segments:
            print(f"\nInput: {segment['text']}")
            manager.process_segments([segment])
            time.sleep(1.0)  # Longer pause

        # Output analysis
        print("\n📊 Analysis:")
        print("-" * 30)
        for i, output in enumerate(output_history, 1):
            if i > 1:
                time_diff = output["timestamp"] - output_history[i - 2]["timestamp"]
                print(f"\nTime since last output: {time_diff:.2f}s")
            print(f"Output {i}: {output['text']}")

    finally:
        # Restore original method
        TextManager.insert_text = original_insert

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_prompt_output()
