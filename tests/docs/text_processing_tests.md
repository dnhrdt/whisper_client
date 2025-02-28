# Text Processing Validation Framework
Version: 1.0
Timestamp: 2025-02-28 19:57 CET

## Overview

This document describes the text processing validation framework for the WhisperClient application. The framework provides a comprehensive set of tests to validate the text processing functionality, including sentence detection, duplicate handling, and text formatting.

## Framework Structure

The text processing validation framework consists of three main components:

1. **Basic Tests**: Core functionality tests for normal text processing scenarios
2. **Edge Case Tests**: Tests for unusual or extreme scenarios
3. **Integration Tests**: Tests for integration with the SendMessage API and other output modes

## Running the Tests

### Running All Tests

To run all tests, execute the following command:

```bash
python tests/integration/test_text_processing.py
```

This will run all test categories and provide a comprehensive summary of the results.

### Running Automated Tests

For automated testing environments (e.g., CI/CD pipelines), you can use the `--no-ui` flag to skip tests that require user interaction:

```bash
python tests/integration/test_text_processing.py --no-ui
```

This will skip the integration tests that require an active window for SendMessage API testing.

## Test Categories

### Basic Tests

Basic tests cover the core functionality of the text processing system:

1. **Normal Sentence Processing**: Tests the basic sentence processing functionality
2. **Deduplication**: Tests the system's ability to detect and handle duplicate text segments
3. **Abbreviations**: Tests the handling of common abbreviations (e.g., "Dr.", "Prof.")
4. **Incomplete Sentences**: Tests the timeout mechanism for incomplete sentences
5. **Punctuation and Formatting**: Tests the handling of different punctuation marks
6. **German Text Processing**: Tests the processing of German text with umlauts and special characters
7. **Mixed Punctuation**: Tests the handling of sentences with different punctuation marks
8. **Sentence Continuation**: Tests the continuation of sentences across multiple segments
9. **Overlapping Segments**: Tests the handling of overlapping text segments
10. **Special Characters**: Tests the processing of text with special characters and numbers

### Edge Case Tests

Edge case tests cover unusual or extreme scenarios:

1. **Empty Segments**: Tests the handling of empty or whitespace-only segments
2. **Very Long Segments**: Tests the processing of very long text segments
3. **Special Abbreviations**: Tests the handling of complex abbreviation patterns
4. **Multiple Sentence End Markers**: Tests the handling of sentences with multiple end markers
5. **Rapid Segment Processing**: Tests the system's ability to handle rapidly arriving segments
6. **Unicode Characters**: Tests the processing of text with Unicode characters and emojis
7. **Mixed Languages**: Tests the handling of text with multiple languages

### Integration Tests

Integration tests verify the interaction with different output modes:

1. **Clipboard Mode Integration**: Tests the clipboard-based text insertion
2. **SendMessage Mode Integration**: Tests the SendMessage API-based text insertion
3. **Both Modes Integration**: Tests the combined clipboard and SendMessage modes

## Test Results

The test results are saved in JSON format in the following files:

- `tests/results/text_processing_results.json`: Basic test results
- `tests/results/text_processing_edge_cases.json`: Edge case test results
- `tests/results/text_processing_integration.json`: Integration test results

Each result file contains detailed information about each test, including:

- Test name
- Input segments
- Expected outputs
- Actual outputs
- Pass/fail status
- Detailed error messages (if any)

## Performance Measurement

The framework includes performance measurement for text processing operations. The performance test:

1. Processes a set of text segments multiple times
2. Measures the processing time for each iteration
3. Calculates statistics (average, median, min, max)
4. Reports the results

## Extending the Framework

To add new tests to the framework:

1. Identify the appropriate test category (basic, edge case, integration)
2. Add a new test case to the corresponding function in `test_text_processing.py`
3. Define the test name, input segments, and expected outputs
4. Run the tests to verify the new test case

Example:

```python
validator.run_test(
    name="New Test Case",
    segments=[
        "Input segment 1",
        "Input segment 2"
    ],
    expected_outputs=["Expected output"]
)
```

## Troubleshooting

### Common Issues

1. **Test Failures**: If a test fails, check the detailed error messages in the test output. The most common issues are:
   - Mismatch between expected and actual outputs
   - Incorrect handling of special cases (abbreviations, punctuation)
   - Timing issues with the timeout mechanism

2. **Integration Test Failures**: If integration tests fail, check:
   - The active window during the test
   - The output mode configuration
   - The SendMessage API implementation

### Debugging

For detailed debugging:

1. Set the log level to DEBUG in `config.py`:
   ```python
   config.LOG_LEVEL_CONSOLE = "DEBUG"
   ```

2. Run the tests with verbose output:
   ```bash
   python tests/integration/test_text_processing.py
   ```

3. Check the detailed log output for each test case

## Conclusion

The text processing validation framework provides a comprehensive set of tests to ensure the reliability and correctness of the WhisperClient's text processing functionality. By regularly running these tests, you can detect and fix issues early in the development process.
