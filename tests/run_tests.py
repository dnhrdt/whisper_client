#!/usr/bin/env python3
"""
Simplified Test Runner
Version: 1.1
Timestamp: 2025-02-28 19:58 CET

This script provides a minimal test runner that supports running tests by category
while maintaining essential timing test functionality. It follows the project's
core testing philosophy: "The test framework is a tool, not a deliverable".
"""
import sys
import time
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Callable

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

import config
from src import logging

# Configure logger
logger = logging.get_logger()
config.LOG_LEVEL_CONSOLE = "INFO"

class TestRunner:
    """Simplified test runner with basic category support."""
    
    def __init__(self):
        self.results: Dict[str, Dict] = {}
        self.start_time: float = 0
        self.category: str = ""
    
    def start_test_suite(self, category: str) -> None:
        """Initialize a test suite for a category."""
        self.category = category
        self.start_time = time.time()
        print(f"\n=== Running {category.title()} Tests ===")
        print("=" * 40)
    
    def end_test_suite(self) -> None:
        """Finalize a test suite and print results."""
        duration = time.time() - self.start_time
        success = all(result.get("success", False) for result in self.results.values())
        
        print("\n=== Test Suite Results ===")
        print("=" * 40)
        print(f"Category: {self.category}")
        print(f"Duration: {duration:.2f}s")
        print(f"Status: {'✅ Passed' if success else '❌ Failed'}")
        print("\nDetailed Results:")
        
        for test_name, result in self.results.items():
            status = "✅" if result.get("success", False) else "❌"
            print(f"{status} {test_name}")
            if "error" in result:
                print(f"   Error: {result['error']}")
        print("=" * 40)
    
    def run_test(self, name: str, test_func: Callable) -> None:
        """Run a single test and record its result."""
        print(f"\n▶️ Running: {name}")
        try:
            test_func()
            self.results[name] = {"success": True}
            print(f"✅ Passed: {name}")
        except Exception as e:
            self.results[name] = {"success": False, "error": str(e)}
            print(f"❌ Failed: {name}")
            print(f"Error: {e}")
    
    def run_timing_tests(self) -> None:
        """Run timing-specific tests."""
        from tests.timing.test_server_flow import test_server_flow, test_websocket_connection
        from tests.timing.timing_tests import test_complete_text_capture, test_quick_stop_handling
        
        self.start_test_suite("timing")
        
        # Run timing tests
        self.run_test("Server Flow", test_server_flow)
        self.run_test("WebSocket Connection", test_websocket_connection)
        self.run_test("Complete Text Capture", test_complete_text_capture)
        self.run_test("Quick Stop Handling", test_quick_stop_handling)
        
        self.end_test_suite()
    
    def run_integration_tests(self) -> None:
        """Run integration tests."""
        from tests.integration.test_text_processing import run_basic_tests, run_edge_case_tests, run_integration_tests
        from tests.integration.test_prompt_output import test_prompt_output
        from tests.integration.test_sendmessage_api import test_sendmessage_api
        
        self.start_test_suite("integration")
        
        # Run integration tests
        self.run_test("Text Processing - Basic Tests", run_basic_tests)
        self.run_test("Text Processing - Edge Cases", run_edge_case_tests)
        
        # Skip UI tests if running in CI/CD environment
        if "--no-ui" not in sys.argv:
            self.run_test("Text Processing - Integration", run_integration_tests)
            self.run_test("SendMessage API", test_sendmessage_api)
            self.run_test("Prompt Output", test_prompt_output)
        else:
            print("Skipping UI tests (--no-ui flag detected)")
        
        self.end_test_suite()
    
    def run_speech_tests(self) -> None:
        """Run speech recognition tests."""
        self.start_test_suite("speech")
        print("Speech tests not yet implemented")
        self.end_test_suite()

def main() -> None:
    """Main entry point for the test runner."""
    parser = argparse.ArgumentParser(description="Simplified WhisperClient Test Runner")
    parser.add_argument(
        "category",
        choices=["timing", "integration", "speech", "all"],
        help="Test category to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--no-ui",
        action="store_true",
        help="Skip tests that require UI interaction (for CI/CD environments)"
    )
    
    args = parser.parse_args()
    
    # Set log level based on verbosity
    if args.verbose:
        config.LOG_LEVEL_CONSOLE = "DEBUG"
    
    runner = TestRunner()
    
    try:
        if args.category in ["timing", "all"]:
            runner.run_timing_tests()
        
        if args.category in ["integration", "all"]:
            runner.run_integration_tests()
        
        if args.category in ["speech", "all"]:
            runner.run_speech_tests()
            
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nError running tests: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
