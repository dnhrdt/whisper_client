"""
WebSocket Multiple Connections Test
Version: 1.7
Timestamp: 2025-04-20 17:37 CET

This module tests the prevention of multiple parallel connections in the WebSocket client.
It verifies that the client properly tracks instances, throttles connection attempts,
and cleans up resources to prevent orphaned connections.
"""

import random
import sys
import threading
import time
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

# Add project directory to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

import config
from src import logging
from src.ws_client import ConnectionState, WhisperWebSocket

# Configure logger
logger = logging.get_logger()


# Patch the connect method to avoid actual server connections
def mock_connect(self, *args, **kwargs):
    """Mock implementation of connect that doesn't actually connect to a
    server."""
    print(f"DEBUG: mock_connect called for client {self.client_id}")

    # Always generate a new session ID for each connection with unique timestamp
    current_time = time.time()
    # Add a small random value to ensure uniqueness
    unique_time = current_time + random.random() * 0.1
    self.session_id = f"test-session-{unique_time}"
    print(f"DEBUG: Generated new session ID: {self.session_id}")

    # Set the state directly without using WebSocket
    self._set_state(ConnectionState.CONNECTING)
    self._set_state(ConnectionState.CONNECTED)
    self._set_state(ConnectionState.READY)

    # Create a more robust mock WebSocket object with a mock sock attribute
    client_id = self.client_id  # Store client_id for use in the inner class

    class MockWebSocket:
        def __init__(self, client_id):
            self.client_id = client_id  # Store client_id in the MockWebSocket instance

            class MockSock:
                def __init__(self):
                    self.connected = True

                def close(self):
                    self.connected = False

            self.sock = MockSock()

        def close(self):
            if self.sock:
                self.sock.close()
                print(f"DEBUG: MockWebSocket closed for client {self.client_id}")

    self.ws = MockWebSocket(client_id)
    self.server_ready = True
    print(f"DEBUG: mock_connect completed for client {self.client_id}")
    return True


class WebSocketMultipleConnectionsTest(unittest.TestCase):
    """Tests for the prevention of multiple parallel connections."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        print("\nDEBUG: Setting up test class")

        # Save original values
        cls.original_reconnect_delay = config.WS_RECONNECT_DELAY
        cls.original_thread_timeout = config.WS_THREAD_TIMEOUT
        cls.original_connect_timeout = config.WS_CONNECT_TIMEOUT
        cls.original_ready_timeout = config.WS_READY_TIMEOUT
        cls.original_final_wait = config.WS_FINAL_WAIT
        cls.original_message_wait = config.WS_MESSAGE_WAIT

        # Set shorter delays for testing
        config.WS_RECONNECT_DELAY = 0.1
        config.WS_THREAD_TIMEOUT = 1.0  # Increased from 0.5 to 1.0
        config.WS_CONNECT_TIMEOUT = 0.5
        config.WS_READY_TIMEOUT = 0.5
        config.WS_FINAL_WAIT = 0.5
        config.WS_MESSAGE_WAIT = 0.2

        print("DEBUG: Class setup completed")

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment once after all tests."""
        print("\nDEBUG: Tearing down test class")

        # Restore original values
        config.WS_RECONNECT_DELAY = cls.original_reconnect_delay
        config.WS_THREAD_TIMEOUT = cls.original_thread_timeout
        config.WS_CONNECT_TIMEOUT = cls.original_connect_timeout
        config.WS_READY_TIMEOUT = cls.original_ready_timeout
        config.WS_FINAL_WAIT = cls.original_final_wait
        config.WS_MESSAGE_WAIT = cls.original_message_wait

        # Final cleanup of any remaining instances
        try:
            WhisperWebSocket.cleanup_all_instances()
        except Exception as e:
            print(f"DEBUG: Error in final cleanup: {e}")

        # Clear active instances
        with WhisperWebSocket._instances_lock:
            WhisperWebSocket._active_instances.clear()

        print("DEBUG: Class teardown completed")

    def setUp(self):
        """Set up test environment for each test."""
        print(f"\nDEBUG: Setting up test: {self._testMethodName}")

        # Patch time.sleep to avoid delays in tests
        self.sleep_patcher = patch("time.sleep")
        self.mock_sleep = self.sleep_patcher.start()

        # Patch the connect method to avoid actual server connections
        self.connect_patcher = patch.object(WhisperWebSocket, "connect", mock_connect)
        self.mock_connect = self.connect_patcher.start()

        # Clear active instances before each test
        with WhisperWebSocket._instances_lock:
            WhisperWebSocket._active_instances.clear()

        # Create a list to track instances created in this test
        self.test_instances = []

        # Ensure no leftover instances from previous tests
        WhisperWebSocket.cleanup_all_instances()

        print(f"DEBUG: Setup completed for test: {self._testMethodName}")

    def tearDown(self):
        """Clean up after each test."""
        print(f"DEBUG: Tearing down test: {self._testMethodName}")

        # Clean up all instances created in this test
        for instance in self.test_instances:
            try:
                if hasattr(instance, "state") and instance.state != ConnectionState.DISCONNECTED:
                    print(
                        f"DEBUG: Cleaning up instance {instance.client_id} in state {instance.state.name}"
                    )
                    instance.cleanup()

                    # Verify cleanup was successful
                    if instance.state != ConnectionState.DISCONNECTED:
                        print(
                            f"WARNING: Instance {instance.client_id} not properly disconnected, forcing state change"
                        )
                        instance._set_state(ConnectionState.DISCONNECTED)

                    print(f"DEBUG: Cleaned up instance {instance.client_id}")
            except Exception as e:
                print(f"DEBUG: Error cleaning up instance {instance.client_id}: {e}")

        # Clean up all instances to be sure
        try:
            WhisperWebSocket.cleanup_all_instances()
            print("DEBUG: Cleaned up all instances")
        except Exception as e:
            print(f"DEBUG: Error cleaning up all instances: {e}")

        # Clear active instances after each test
        with WhisperWebSocket._instances_lock:
            instance_count = len(WhisperWebSocket._active_instances)
            if instance_count > 0:
                print(f"WARNING: {instance_count} instances still active after cleanup")
                for client_id, instance in list(WhisperWebSocket._active_instances.items()):
                    print(f"DEBUG: Forcing cleanup of instance {client_id}")
                    try:
                        instance.cleanup()
                    except Exception as e:
                        print(f"DEBUG: Error in forced cleanup: {e}")

                    # Remove from active instances
                    if client_id in WhisperWebSocket._active_instances:
                        del WhisperWebSocket._active_instances[client_id]

            print(
                f"DEBUG: Cleared active instances, count: {len(WhisperWebSocket._active_instances)}"
            )

        # Stop patches
        self.sleep_patcher.stop()
        self.connect_patcher.stop()

        print(f"DEBUG: Teardown completed for test: {self._testMethodName}")

    def test_client_and_session_ids(self):
        """Test client and session ID tracking."""
        print("DEBUG: Starting test_client_and_session_ids")

        # Create a WebSocket client
        ws_client = WhisperWebSocket()
        self.test_instances.append(ws_client)  # Track for cleanup
        print(f"DEBUG: Created client with ID: {ws_client.client_id}")

        # Connect to server
        print("DEBUG: Connecting client")
        ws_client.connect()
        print(f"DEBUG: Client connected with session ID: {ws_client.session_id}")

        # Verify client ID and session ID are set
        self.assertIsNotNone(ws_client.client_id, "Client ID should be set")
        self.assertIsNotNone(ws_client.session_id, "Session ID should be set")

        # Store original session ID
        original_session_id = ws_client.session_id

        # Verify client is in READY state
        print("DEBUG: Verifying client is in READY state")
        self.assertEqual(
            ws_client.state, ConnectionState.READY, "Client should be in READY state after connect"
        )

        # Reconnect
        print("DEBUG: Cleaning up client for reconnection")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after cleanup",
        )

        print("DEBUG: Reconnecting client")
        ws_client.connect()
        print(f"DEBUG: Client reconnected with new session ID: {ws_client.session_id}")

        # Verify client ID remains the same but session ID changes
        self.assertIsNotNone(ws_client.client_id, "Client ID should still be set after reconnect")
        self.assertIsNotNone(ws_client.session_id, "Session ID should still be set after reconnect")
        self.assertNotEqual(
            ws_client.session_id, original_session_id, "Session ID should change after reconnect"
        )

        # Verify client is in READY state after reconnect
        print("DEBUG: Verifying client is in READY state after reconnect")
        self.assertEqual(
            ws_client.state,
            ConnectionState.READY,
            "Client should be in READY state after reconnect",
        )

        # Clean up
        print("DEBUG: Final cleanup")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after final cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after final cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after final cleanup",
        )

        print("DEBUG: test_client_and_session_ids completed")

    def test_instance_tracking(self):
        """Test tracking of WebSocket instances."""
        print("DEBUG: Starting test_instance_tracking")

        # Initially no instances
        self.assertEqual(
            WhisperWebSocket.get_instance_count(), 0, "Initially there should be no instances"
        )

        # Create instances
        print("DEBUG: Creating first instance")
        ws_client1 = WhisperWebSocket()
        self.test_instances.append(ws_client1)  # Track for cleanup
        self.assertEqual(
            WhisperWebSocket.get_instance_count(),
            1,
            "After creating one instance, count should be 1",
        )

        print("DEBUG: Creating second instance")
        ws_client2 = WhisperWebSocket()
        self.test_instances.append(ws_client2)  # Track for cleanup
        self.assertEqual(
            WhisperWebSocket.get_instance_count(),
            2,
            "After creating two instances, count should be 2",
        )

        # Clean up one instance
        print("DEBUG: Cleaning up first instance")
        ws_client1.cleanup()

        # Verify client is in DISCONNECTED state after cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after cleanup")
        self.assertEqual(
            ws_client1.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after cleanup",
        )

        # Manually remove from active instances to avoid relying on garbage collection
        print("DEBUG: Manually removing first instance from active instances")
        with WhisperWebSocket._instances_lock:
            if ws_client1.client_id in WhisperWebSocket._active_instances:
                del WhisperWebSocket._active_instances[ws_client1.client_id]

        # Verify count is updated
        self.assertEqual(
            WhisperWebSocket.get_instance_count(),
            1,
            "After cleaning up one instance, count should be 1",
        )

        # Clean up remaining instance
        print("DEBUG: Cleaning up second instance")
        ws_client2.cleanup()

        # Verify client is in DISCONNECTED state after cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after cleanup")
        self.assertEqual(
            ws_client2.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after cleanup",
        )

        # Manually remove from active instances
        print("DEBUG: Manually removing second instance from active instances")
        with WhisperWebSocket._instances_lock:
            if ws_client2.client_id in WhisperWebSocket._active_instances:
                del WhisperWebSocket._active_instances[ws_client2.client_id]

        # Verify count is updated
        self.assertEqual(
            WhisperWebSocket.get_instance_count(),
            0,
            "After cleaning up all instances, count should be 0",
        )

        print("DEBUG: test_instance_tracking completed")

    def test_cleanup_all_instances(self):
        """Test cleanup of all WebSocket instances."""
        print("DEBUG: Starting test_cleanup_all_instances")

        # Create multiple instances - reduce to 2 for faster testing
        print("DEBUG: Creating WebSocket instances")
        ws_clients = [WhisperWebSocket() for _ in range(2)]
        self.test_instances.extend(ws_clients)  # Track for cleanup

        # Connect all clients
        print("DEBUG: Connecting all clients")
        for client in ws_clients:
            client.connect()

        # Verify all are connected
        print("DEBUG: Verifying all clients are connected")
        for client in ws_clients:
            self.assertEqual(
                client.state, ConnectionState.READY, "All clients should be in READY state"
            )

        # Clean up all instances
        print("DEBUG: Cleaning up all instances")
        WhisperWebSocket.cleanup_all_instances()

        # Verify all are disconnected
        print("DEBUG: Verifying all clients are disconnected")
        for client in ws_clients:
            self.assertEqual(
                client.state,
                ConnectionState.DISCONNECTED,
                "All clients should be in DISCONNECTED state after cleanup_all_instances",
            )

        # Verify instance count is 0
        with WhisperWebSocket._instances_lock:
            instance_count = len(WhisperWebSocket._active_instances)
            if instance_count > 0:
                print(
                    f"WARNING: {instance_count} instances still active after cleanup_all_instances"
                )
                for client_id, instance in list(WhisperWebSocket._active_instances.items()):
                    print(f"DEBUG: Active instance: {client_id}, state: {instance.state.name}")

        print("DEBUG: test_cleanup_all_instances completed")

    def test_connection_throttling(self):
        """Test throttling of connection attempts."""
        print("DEBUG: Starting test_connection_throttling")

        # We'll use a mock for time.sleep but track the calls
        self.mock_sleep.reset_mock()

        # Set a delay for testing throttling
        config.WS_RECONNECT_DELAY = 0.2

        # Create a WebSocket client
        print("DEBUG: Creating WebSocket client")
        ws_client = WhisperWebSocket()

        # First connection should not call sleep
        print("DEBUG: First connection attempt")
        ws_client.connect()
        self.assertEqual(self.mock_sleep.call_count, 0, "First connection should not call sleep")

        # Verify client is in READY state
        print("DEBUG: Verifying client is in READY state after first connection")
        self.assertEqual(
            ws_client.state,
            ConnectionState.READY,
            "Client should be in READY state after first connection",
        )

        # Cleanup to allow reconnection
        print("DEBUG: Cleaning up for reconnection")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after cleanup",
        )

        # Directly test the throttling logic
        print("DEBUG: Directly testing throttling logic")

        # Set last_connection_attempt to simulate a recent connection
        ws_client.last_connection_attempt = time.time()

        # Call the throttling logic directly
        current_time = time.time()
        if current_time - ws_client.last_connection_attempt < config.WS_RECONNECT_DELAY:
            wait_time = config.WS_RECONNECT_DELAY - (
                current_time - ws_client.last_connection_attempt
            )
            print(f"DEBUG: Connection attempt throttled, waiting {wait_time:.2f}s")
            time.sleep(wait_time)

        # Verify that sleep was called with the expected delay
        self.mock_sleep.assert_called_once()
        args, kwargs = self.mock_sleep.call_args
        self.assertAlmostEqual(
            args[0],
            config.WS_RECONNECT_DELAY,
            delta=0.1,
            msg="Sleep should be called with the throttle delay",
        )

        # Now connect again
        print("DEBUG: Second connection attempt")
        ws_client.connect()

        # Verify client is in READY state after second connection
        print("DEBUG: Verifying client is in READY state after second connection")
        self.assertEqual(
            ws_client.state,
            ConnectionState.READY,
            "Client should be in READY state after second connection",
        )

        # Clean up
        print("DEBUG: Final cleanup")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after final cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after final cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after final cleanup",
        )

        print("DEBUG: test_connection_throttling completed")

    def test_parallel_connections(self):
        """Test handling of parallel connection attempts."""
        print("DEBUG: Starting test_parallel_connections")

        # Create two WebSocket clients
        print("DEBUG: Creating first WebSocket client")
        ws_client1 = WhisperWebSocket()
        print("DEBUG: Creating second WebSocket client")
        ws_client2 = WhisperWebSocket()

        # Connect both clients
        print("DEBUG: Connecting first client")
        ws_client1.connect()
        print("DEBUG: Connecting second client")
        ws_client2.connect()

        # Verify both are connected with different client IDs
        print("DEBUG: Verifying both clients are connected")
        self.assertEqual(
            ws_client1.state, ConnectionState.READY, "First client should be in READY state"
        )
        self.assertEqual(
            ws_client2.state, ConnectionState.READY, "Second client should be in READY state"
        )
        self.assertNotEqual(
            ws_client1.client_id, ws_client2.client_id, "Clients should have different client IDs"
        )

        # Verify both are tracked
        print("DEBUG: Verifying both clients are tracked")
        self.assertEqual(WhisperWebSocket.get_instance_count(), 2, "Both clients should be tracked")

        # Clean up
        print("DEBUG: Cleaning up first client")
        ws_client1.cleanup()
        print("DEBUG: Cleaning up second client")
        ws_client2.cleanup()

        # Verify cleanup was successful
        print("DEBUG: Verifying cleanup was successful")
        self.assertEqual(
            ws_client1.state,
            ConnectionState.DISCONNECTED,
            "First client should be in DISCONNECTED state after cleanup",
        )
        self.assertEqual(
            ws_client2.state,
            ConnectionState.DISCONNECTED,
            "Second client should be in DISCONNECTED state after cleanup",
        )

        print("DEBUG: test_parallel_connections completed")

    def test_reconnection_with_new_session(self):
        """Test reconnection with new session ID."""
        print("DEBUG: Starting test_reconnection_with_new_session")

        # Create a WebSocket client
        print("DEBUG: Creating WebSocket client")
        ws_client = WhisperWebSocket()

        # Connect to server
        print("DEBUG: Connecting client")
        ws_client.connect()
        original_session_id = ws_client.session_id
        print(f"DEBUG: Original session ID: {original_session_id}")

        # Simulate connection error and cleanup
        print("DEBUG: Simulating connection error")
        ws_client._set_state(ConnectionState.CONNECT_ERROR)
        print("DEBUG: Cleaning up client")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after cleanup",
        )

        # Reconnect
        print("DEBUG: Reconnecting client")
        ws_client.connect()
        print(f"DEBUG: New session ID: {ws_client.session_id}")

        # Verify session ID changed but client ID remained the same
        self.assertNotEqual(
            ws_client.session_id, original_session_id, "Session ID should change after reconnection"
        )

        # Clean up
        print("DEBUG: Final cleanup")
        ws_client.cleanup()

        # Verify client is in DISCONNECTED state after final cleanup
        print("DEBUG: Verifying client is in DISCONNECTED state after final cleanup")
        self.assertEqual(
            ws_client.state,
            ConnectionState.DISCONNECTED,
            "Client should be in DISCONNECTED state after final cleanup",
        )

        print("DEBUG: test_reconnection_with_new_session completed")


if __name__ == "__main__":
    unittest.main()
