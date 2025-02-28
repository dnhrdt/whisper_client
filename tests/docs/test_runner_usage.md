# Test Runner Usage Guide
Version: 1.1
Timestamp: 2025-02-28 19:58 CET

## Overview
The WhisperClient test runner provides a simplified way to execute tests by category while maintaining essential timing test functionality. It follows the project's core testing philosophy: "The test framework is a tool, not a deliverable".

## Basic Usage

### Running Tests by Category
```bash
# Run timing tests
python run_tests.py timing

# Run integration tests
python run_tests.py integration

# Run speech tests
python run_tests.py speech

# Run all tests
python run_tests.py all
```

### Enabling Verbose Output
Add the `-v` or `--verbose` flag for detailed logging:
```bash
python run_tests.py timing -v
```

### Skipping UI Tests
For automated testing environments (CI/CD pipelines), use the `--no-ui` flag to skip tests that require user interaction:
```bash
python run_tests.py integration --no-ui
```
This will skip tests that require an active window, such as SendMessage API tests.

## Test Categories

### 1. Timing Tests (Priority 1)
Tests focused on timing and server communication:
- Server Flow
- WebSocket Connection
- Complete Text Capture
- Quick Stop Handling

### 2. Integration Tests (Priority 2)
Tests for text processing and output:
- Text Processing - Basic Tests
- Text Processing - Edge Cases
- Text Processing - Integration
- SendMessage API
- Prompt Output

For detailed information about the text processing tests, see [text_processing_tests.md](text_processing_tests.md).

### 3. Speech Tests (Priority 3)
Speech recognition tests (to be implemented)

## Prerequisites

### For Timing Tests
- WhisperLive Server must be running
- Server configuration in config.py must be correct
- Network connectivity required

### For Integration Tests
- Basic tests and edge cases: No external dependencies, can run offline
- Integration tests: Require an active window for SendMessage API testing
- Use `--no-ui` flag to skip tests requiring UI interaction

### For Speech Tests
- To be determined during implementation

## Test Results

### Output Format
```
=== Test Suite Results ===
========================================
Category: [category]
Duration: [time]s
Status: [✅ Passed or ❌ Failed]

Detailed Results:
✅ Test Name
❌ Failed Test
   Error: Error message if any
========================================
```

### Exit Codes
- 0: All tests passed
- 1: Tests failed or interrupted

## Common Issues

### Connection Errors
If you see connection errors like:
```
❌ Connection error: [WinError 10061] Es konnte keine Verbindung hergestellt werden...
```
Verify that:
1. WhisperLive Server is running
2. Server port (default: 9090) is correct
3. No firewall blocking the connection

### Test Interruption
To safely interrupt running tests:
1. Press Ctrl+C
2. The runner will perform cleanup
3. Exit with status code 1

## Batch File Usage
For Windows users, a batch file is provided:
```bash
# Run from tests directory
run_tests.bat timing
run_tests.bat integration -v
```

## Development Notes

### Adding New Tests
1. Create test file in appropriate category directory
2. Follow existing test patterns
3. Update test runner if needed
4. Document in test_inventory.md

### Test Philosophy
Remember: "The test framework is a tool, not a deliverable"
- Keep tests simple and maintainable
- Focus on essential functionality
- Prefer manual verification for straightforward features
- Add complexity only when needed

## References
- test_inventory.md: Complete test catalog
- migration_roadmap.md: Test migration status
- test_architecture.md: Overall test architecture
