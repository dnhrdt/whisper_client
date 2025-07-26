"""
Alpha Test Script for WhisperClient
Version: 1.1
Timestamp: 2025-04-20 17:34 CET

This script provides a simple test to verify the basic functionality of the WhisperClient.
It checks if the WhisperLive server is running, initializes the client, records a short
audio sample, processes it, and verifies the output.

Usage:
    python tools/alpha_test.py

Requirements:
    - WhisperLive server running on localhost:9090
    - Microphone connected and configured in config.py
"""

import json
import os
import socket
import sys
import threading
import time

# Add parent directory to path to import from main project
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src import logger
from src.audio import AudioManager, AudioProcessor
from src.text import TextManager
from src.utils import check_server_status
from src.ws_client import ConnectionState, WhisperWebSocket


class AlphaTest:
    """Simple test class for WhisperClient alpha testing."""

    def __init__(self):
        """Initialize the test."""
        self.text_manager = TextManager(test_mode=True)
        self.websocket = WhisperWebSocket()
        self.audio_manager = AudioManager()
        self.audio_processor = AudioProcessor()

        # Test results
        self.test_results = {
            "server_check": False,
            "websocket_connection": False,
            "audio_device": False,
            "recording": False,
            "processing": False,
            "text_output": False,
            "cleanup": False,
            "output_text": [],
            "errors": [],
        }

        # Set callbacks
        self.websocket.set_text_callback(self.on_text_segments)

        # Event to signal test completion
        self.test_complete = threading.Event()

    def on_text_segments(self, segments):
        """Callback for text segments."""
        for segment in segments:
            text = segment.get("text", "").strip()
            if text:
                self.test_results["output_text"].append(text)
                logger.info(f"Received text: {text}")
                self.test_results["text_output"] = True

    def on_audio_data(self, audio_data):
        """Callback for audio data."""
        self.audio_processor.process_audio(audio_data)

    def on_processed_audio(self, processed_audio):
        """Callback for processed audio."""
        self.websocket.send_audio(processed_audio)
        self.test_results["processing"] = True

    def check_server(self):
        """Check if the WhisperLive server is running."""
        logger.info("Checking server status...")
        server_status = check_server_status()
        self.test_results["server_check"] = server_status
        if not server_status:
            self.test_results["errors"].append("WhisperLive server not running")
            logger.error("❌ WhisperLive server not running")
            return False
        logger.info("✓ WhisperLive server is running")
        return True

    def connect_websocket(self):
        """Connect to the WhisperLive server."""
        logger.info("Connecting to WhisperLive server...")
        try:
            self.websocket.connect()
            start_time = time.time()
            while self.websocket.state != ConnectionState.READY:
                if time.time() - start_time > 5.0:
                    self.test_results["errors"].append("WebSocket connection timeout")
                    logger.error("❌ WebSocket connection timeout")
                    return False
                time.sleep(0.1)

            self.test_results["websocket_connection"] = True
            logger.info("✓ Connected to WhisperLive server")
            return True
        except Exception as e:
            self.test_results["errors"].append(f"WebSocket connection error: {str(e)}")
            logger.error(f"❌ WebSocket connection error: {e}")
            return False

    def check_audio_device(self):
        """Check if the audio device is available."""
        logger.info("Checking audio device...")
        if not self.audio_manager.is_device_available():
            self.test_results["errors"].append("Audio device not available")
            logger.error("❌ Audio device not available")
            return False

        self.test_results["audio_device"] = True
        logger.info("✓ Audio device is available")
        return True

    def record_audio(self, duration=5.0):
        """Record audio for the specified duration."""
        logger.info(f"Recording audio for {duration} seconds...")

        # Start audio processing
        self.audio_processor.start_processing(self.on_processed_audio)

        # Start WebSocket processing
        self.websocket.start_processing()

        # Start recording
        self.audio_manager.start_recording(self.on_audio_data)
        self.test_results["recording"] = True

        # Wait for the specified duration
        time.sleep(duration)

        # Stop recording
        logger.info("Stopping recording...")
        self.audio_manager.stop_recording()

        # Stop audio processing
        self.audio_processor.stop_processing()

        # Wait for final text
        logger.info("Waiting for final text...")
        self.websocket.stop_processing()

        # Wait for test completion or timeout
        self.test_complete.wait(timeout=10.0)

        return True

    def cleanup(self):
        """Clean up resources."""
        logger.info("Cleaning up resources...")
        try:
            self.audio_manager.cleanup()
            self.websocket.cleanup()
            self.test_results["cleanup"] = True
            logger.info("✓ Resources cleaned up")
            return True
        except Exception as e:
            self.test_results["errors"].append(f"Cleanup error: {str(e)}")
            logger.error(f"❌ Cleanup error: {e}")
            return False

    def run_test(self, duration=5.0):
        """Run the alpha test."""
        logger.info("\n=== WhisperClient Alpha Test ===\n")

        # Check server
        if not self.check_server():
            return self.test_results

        # Connect to WebSocket
        if not self.connect_websocket():
            return self.test_results

        # Check audio device
        if not self.check_audio_device():
            self.cleanup()
            return self.test_results

        # Record audio
        if not self.record_audio(duration):
            self.cleanup()
            return self.test_results

        # Clean up
        self.cleanup()

        # Print results
        self.print_results()

        return self.test_results

    def print_results(self):
        """Print test results."""
        logger.info("\n=== Test Results ===\n")

        # Check if all tests passed
        all_passed = all(
            [
                self.test_results["server_check"],
                self.test_results["websocket_connection"],
                self.test_results["audio_device"],
                self.test_results["recording"],
                self.test_results["processing"],
                self.test_results["text_output"],
                self.test_results["cleanup"],
            ]
        )

        if all_passed:
            logger.info("✅ All tests passed!")
        else:
            logger.info("❌ Some tests failed:")

            for test, result in self.test_results.items():
                if test not in ["output_text", "errors"]:
                    status = "✅" if result else "❌"
                    logger.info(f"{status} {test}: {result}")

        # Print output text
        if self.test_results["output_text"]:
            logger.info("\nRecognized text:")
            for text in self.test_results["output_text"]:
                logger.info(f"  - {text}")
        else:
            logger.info("\nNo text was recognized.")

        # Print errors
        if self.test_results["errors"]:
            logger.info("\nErrors:")
            for error in self.test_results["errors"]:
                logger.info(f"  - {error}")

        # Save results to file
        results_file = "alpha_test_results.json"
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(self.test_results, f, indent=2, ensure_ascii=False)

        logger.info(f"\nResults saved to {results_file}")


def main():
    """Main function."""
    # Parse command line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Run alpha test for WhisperClient")
    parser.add_argument("--duration", type=float, default=5.0, help="Recording duration in seconds")
    args = parser.parse_args()

    # Run test
    test = AlphaTest()
    test.run_test(duration=args.duration)


if __name__ == "__main__":
    main()
