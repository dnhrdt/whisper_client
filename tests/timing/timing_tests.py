"""
Systematic Timing Test Script
Version: 1.1
Timestamp: 2025-04-20 17:35 CET
"""

import json
import sys
import threading
import time
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import config
from src.audio import AudioManager
from src.text import TextManager
from src.ws_client import WhisperWebSocket


class TimingTest:
    def __init__(self):
        self.ws = WhisperWebSocket()
        self.audio = AudioManager()
        self.text = TextManager()
        self.received_texts = []
        self.test_log = []

    def log_event(self, event_type: str, message: str, timestamp: float = None):
        """Log event with timestamp."""
        if timestamp is None:
            timestamp = time.time()

        self.test_log.append({"timestamp": timestamp, "type": event_type, "message": message})

    def on_text_received(self, segments):
        """Callback for received text segments."""
        timestamp = time.time()
        for segment in segments:
            text = segment.get("text", "").strip()
            if text:
                self.received_texts.append({"timestamp": timestamp, "text": text})
                self.log_event("text", f"Received: {text}", timestamp)

    def save_test_results(self, test_name: str):
        """Save test results."""
        results = {
            "test_name": test_name,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "config": {
                "WS_FINAL_WAIT": config.WS_FINAL_WAIT,
                "WS_MESSAGE_WAIT": config.WS_MESSAGE_WAIT,
                "AUDIO_BUFFER_SECONDS": config.AUDIO_BUFFER_SECONDS,
            },
            "events": self.test_log,
            "received_texts": self.received_texts,
        }

        # Save in tests/results
        results_dir = Path("tests/results")
        results_dir.mkdir(exist_ok=True)

        result_file = results_dir / f"{test_name}_{int(time.time())}.json"
        with open(result_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=2, ensure_ascii=False)

    def analyze_results(self):
        """Analyze test results."""
        if not self.test_log:
            return "No test results available"

        analysis = []

        # Time intervals between events
        events = sorted(self.test_log, key=lambda x: x["timestamp"])
        for i in range(1, len(events)):
            delta = events[i]["timestamp"] - events[i - 1]["timestamp"]
            analysis.append(f"Δt {events[i-1]['type']} → {events[i]['type']}: {delta:.3f}s")

        # Text completeness
        if self.received_texts:
            total_chars = sum(len(t["text"]) for t in self.received_texts)
            analysis.append(f"Received texts: {len(self.received_texts)}")
            analysis.append(f"Total characters: {total_chars}")

            # Time distribution
            if len(self.received_texts) > 1:
                start = self.received_texts[0]["timestamp"]
                end = self.received_texts[-1]["timestamp"]
                duration = end - start
                analysis.append(f"Total duration: {duration:.3f}s")
                analysis.append(f"Average time per text: {duration/len(self.received_texts):.3f}s")

        return "\n".join(analysis)


def test_complete_text_capture():
    """Test: All texts must be received completely"""
    test = TimingTest()
    test.ws.set_text_callback(test.on_text_received)

    # F13 handler for recording control
    recording = False

    def toggle_recording():
        nonlocal recording
        if not recording:
            # First start WebSocket
            test.ws.start_processing()
            time.sleep(config.TEST_SERVER_READY_DELAY)  # Wait for server ready
            # Then start recording
            test.audio.start_recording(test.ws.send_audio)
            recording = True
            test.log_event("audio", "Recording started")
        else:
            # First stop recording
            test.audio.stop_recording()
            time.sleep(config.TEST_AUDIO_PROCESS_DELAY)  # Wait for audio processing
            # Then stop WebSocket
            test.ws.stop_processing()
            recording = False
            test.log_event("audio", "Recording stopped")

    # Establish connection
    test.log_event("connection", "Connecting to server")
    assert test.ws.connect(), "Connection setup failed"
    test.log_event("connection", "Connected to server")

    print("\nPlease read text from Speech Test 1.2.")
    print("Press F13 to start recording")
    print("Press F13 again to stop after reading")

    # Wait for user interaction
    input("Press Enter when test is complete...")

    print("\nPlease read text from Speech Test 1.2.")
    print("Press F13 to start recording")
    print("Press F13 again to stop after reading")

    # Wait for user interaction
    input("Press Enter when finished...")

    # Save and analyze results
    test.save_test_results("complete_text_capture")
    analysis = test.analyze_results()
    print("\nTest Analysis:")
    print(analysis)


def test_quick_stop_handling():
    """Test: Texts must be received even with quick stop"""
    test = TimingTest()
    test.ws.set_text_callback(test.on_text_received)

    # F13 handler for recording control
    recording = False

    def toggle_recording():
        nonlocal recording
        if not recording:
            # First start WebSocket
            test.ws.start_processing()
            time.sleep(config.TEST_SERVER_READY_DELAY)  # Wait for server ready
            # Then start recording
            test.audio.start_recording(test.ws.send_audio)
            recording = True
            test.log_event("audio", "Recording started")
        else:
            # First stop recording
            test.audio.stop_recording()
            time.sleep(config.TEST_AUDIO_PROCESS_DELAY)  # Wait for audio processing
            # Then stop WebSocket
            test.ws.stop_processing()
            recording = False
            test.log_event("audio", "Recording stopped")

    # Establish connection
    test.log_event("connection", "Connecting to server")
    assert test.ws.connect(), "Connection setup failed"
    test.log_event("connection", "Connected to server")

    print("\nPlease say a short sentence (2-3 words).")
    print("Press F13 to start recording")
    print("Press F13 IMMEDIATELY after the sentence to stop")

    # Wait for user interaction
    input("Press Enter when test is complete...")

    print("\nPlease say a short sentence (2-3 words).")
    print("Press F13 to start recording")
    print("Press F13 IMMEDIATELY after the sentence to stop")

    # Wait for user interaction
    input("Press Enter when finished...")

    # Save and analyze results
    test.save_test_results("quick_stop_handling")
    analysis = test.analyze_results()
    print("\nTest Analysis:")
    print(analysis)


if __name__ == "__main__":
    print("Starting Timing Tests...")

    print("\n1. Test: Complete Text Capture")
    test_complete_text_capture()

    print("\n2. Test: Quick Stop Handling")
    test_quick_stop_handling()
