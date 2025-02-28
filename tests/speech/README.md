# Speech Recognition Tests
Version: 1.0
Timestamp: 2025-02-26 21:15 CET

## Purpose
This directory contains German speech recognition tests for the WhisperClient system. These tests are Priority 3 in our test strategy, building upon stable timing and integration foundations.

## Documentation
Detailed documentation can be found in:
- [Test Architecture](../../docs/testing/test_architecture.md)
- [Speech Tests Documentation](../../docs/testing/speech_tests.md)

## Directory Structure
```
speech/
├── test_basic.py         # Simple German sentences
├── test_complex.py       # Advanced German cases
└── test_edge_cases.py    # Special scenarios
```

## Test Categories

### Basic Tests (test_basic.py)
1. **Short, Clear Sentences**
   - Single short sentences
   - Multiple sentences in succession
   - Basic punctuation
   Example: "Dies ist ein Test.", "Das ist der zweite Satz."

2. **Sentences with Abbreviations**
   - Common German abbreviations
   - Title abbreviations (Dr., Prof.)
   - General abbreviations (z.B., usw.)
   Example: "Dr. Müller und Prof. Schmidt arbeiten zusammen."

### Complex Tests (test_complex.py)
1. **German Language Features**
   - Compound words
   - Umlauts and ß
   - Article variations
   - Case sensitivity
   Example: "Donaudampfschifffahrtsgesellschaftskapitän"

2. **Sentence Structures**
   - Complex sentences
   - Nested clauses
   - Variable word order
   - Grammatical cases
   Example: "Der Mann, der das Buch gelesen hat, arbeitet hier."

### Edge Cases (test_edge_cases.py)
1. **Timing Variations**
   - Pauses between words
   - Rapid speech
   - Variable speech rates
   Example: "Dies ist... ein Test... mit Pausen."

2. **Special Cases**
   - Numbers and dates
   - Foreign words
   - Technical terms
   - Mixed language elements
   Example: "Am 21.03.2025 startet das Software-Update."

## Test Resources
All test cases are documented in [speech_test_cases.md](../../docs/testing/speech_tests.md)

## Running Tests
```bash
# Run all speech tests
python -m pytest tests/speech/

# Run specific test category
python -m pytest tests/speech/test_basic.py
python -m pytest tests/speech/test_complex.py
python -m pytest tests/speech/test_edge_cases.py
```

## Success Criteria
1. Accurate German speech recognition
2. Proper handling of German language features
3. Correct punctuation and capitalization
4. Accurate compound word recognition
5. Proper special character handling

## Current Status
- [ ] test_basic.py - To be implemented
- [ ] test_complex.py - To be implemented
- [ ] test_edge_cases.py - To be implemented

## Next Steps
1. Implement basic sentence tests
2. Implement complex language tests
3. Implement edge case handling
4. Document recognition accuracy
5. Optimize German language model

## Test Environment Requirements
1. **Speaker Requirements**
   - Native German speaker preferred
   - Clear standard German pronunciation
   - Consistent speaking pace
   - Natural intonation

2. **Environment Setup**
   - Quiet testing environment
   - Consistent microphone setup
   - Proper room acoustics
   - Temperature control

3. **System Requirements**
   - German language model loaded
   - Proper audio device configuration
   - UTF-8 encoding support
   - German keyboard layout

## Quality Metrics
1. **Recognition Accuracy**
   - Word Error Rate (WER)
   - Character Error Rate (CER)
   - Compound word accuracy
   - Special character accuracy

2. **Performance Metrics**
   - Recognition speed
   - Processing latency
   - Memory usage
   - CPU utilization

## Dependencies
- Stable timing test results
- Working integration tests
- German language model
- Test audio samples
- Reference transcriptions
