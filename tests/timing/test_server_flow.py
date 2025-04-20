"""
Server Data Flow Test Script
Version: 1.1
Timestamp: 2025-04-20 17:36 CET
"""

import json
import sys
import time
from pathlib import Path

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import logging

import config
from src.text import TextManager
from src.ws_client import WhisperWebSocket

# Configure logger for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


def simulate_server_message():
    """Simulates a typical server message"""
    return {
        "segments": [
            {"text": "This is a test."},
            {"text": "Another test."},
            {"text": "And another one?"},
            {"text": "Yes!"},
            {"text": "Okay."},
        ]
    }


def test_server_flow():
    """Tests data flow from server to text processing"""
    print("\n🔍 Testing Server Data Flow...")
    print("=" * 50)

    # Initialize TextManager
    manager = TextManager()

    # Simulate server message
    server_message = simulate_server_message()

    print("\n1️⃣ Server sends JSON message:")
    print("-" * 30)
    print(json.dumps(server_message, indent=2))

    print("\n2️⃣ WebSocket receives and logs segments:")
    print("-" * 30)
    for segment in server_message["segments"]:
        print(f"  → {segment['text']}")

    print("\n3️⃣ Text processing processes segments:")
    print("-" * 30)

    # Store original insert_text method
    original_insert = manager.insert_text
    output_history = []

    def mock_insert_text(self, text):
        """Mock for insert_text that logs outputs"""
        output_history.append({"timestamp": time.time(), "text": text})
        print(f"Output: {text}")

    # Set mock function
    TextManager.insert_text = mock_insert_text

    try:
        # Process segments
        manager.process_segments(server_message["segments"])

        print("\n4️⃣ Analysis:")
        print("-" * 30)
        print(f"• Input segments: {len(server_message['segments'])}")
        print(f"• Output sentences: {len(output_history)}")
        print("\nTiming sequence:")
        for i, output in enumerate(output_history, 1):
            if i > 1:
                time_diff = output["timestamp"] - output_history[i - 2]["timestamp"]
                print(f"\nTime since last output: {time_diff:.2f}s")
            print(f"Sentence {i}: {output['text']}")

    finally:
        # Restore original method
        TextManager.insert_text = original_insert

    print("\n✅ Test completed!")


def test_websocket_connection():
    """Tests WebSocket connection with server-ready-check and END_OF_AUDIO signal"""
    print("\n🔌 Testing WebSocket Connection...")
    print("=" * 50)

    # Initialize WebSocket
    ws = WhisperWebSocket()

    print("\n1️⃣ Connection setup:")
    print("-" * 30)

    # Establish connection
    try:
        connected = ws.connect()
        print(f"Connection successful: {connected}")
        print(f"Server ready: {ws.is_ready()}")

        print("\n2️⃣ Audio transmission:")
        print("-" * 30)

        # Test audio transmission without server-ready
        ws.server_ready = False
        audio_sent = ws.send_audio(b"test_audio")
        print(f"Audio sent without server-ready: {audio_sent} (should be False)")

        # Test audio transmission with server-ready
        ws.server_ready = True
        audio_sent = ws.send_audio(b"test_audio")
        print(f"Audio sent with server-ready: {audio_sent}")

        print("\n3️⃣ END_OF_AUDIO signal:")
        print("-" * 30)

        # Test END_OF_AUDIO signal
        signal_sent = ws.send_end_of_audio()
        print(f"END_OF_AUDIO signal sent: {signal_sent}")

        print("\n4️⃣ Cleanup:")
        print("-" * 30)

        # Test cleanup
        ws.cleanup()
        print(f"Connection after cleanup: {ws.connected}")
        print(f"Server-ready after cleanup: {ws.server_ready}")

    except Exception as e:
        print(f"⚠️ Test failed: {e}")
        raise
    finally:
        if ws.connected:
            ws.cleanup()

    print("\n✅ Test completed!")


if __name__ == "__main__":
    test_server_flow()
    test_websocket_connection()
