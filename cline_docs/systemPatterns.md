# System Architecture & Patterns
Version: 1.2
Timestamp: 2025-02-26 20:42 CET

## Document Purpose
This document outlines how the system is built, key technical decisions, and architectural patterns used throughout the WhisperClient project.

## How The System Is Built

### Development Standards
1. **Code Style**
   - PEP 8 conventions
   - Typed functions (Python 3.12+)
   - Comprehensive docstrings
   - Clear error handling

2. **Documentation Requirements**
   - ALL changes MUST be documented
   - Commit after each functional change
   - Documentation parallel to code
   - Changes tracked in logs
   - Development history in incremental logs

3. **Line Ending Standards**
   - .gitattributes controls line endings
   - Python files use LF (*.py)
   - Documentation files use LF (*.md, *.txt, *.json)
   - Windows scripts use CRLF (*.bat, *.cmd, *.ps1)
   - Auto-detection for other files

3. **Error Handling Patterns**
   - Connection errors: 5s timeout, 3s reconnect
   - Audio errors: overflow ignoring, stream reset
   - Thread-safe recording control
   - Structured error logging

### Development Logging Strategy
Note: This describes the development change tracking system.

## Log Levels & Details

### Critical Changes (Full Detail)
- Regressions and their fixes
- Core feature implementations
- Breaking changes
- Major refactoring

Log Format:
```json
{
  "type": "critical",
  "task_id": "T123",
  "component": "core",
  "description": "Detailed description",
  "details": ["Change 1", "Change 2"],
  "files_changed": ["file1.py", "file2.py"],
  "test_impact": {
    "tests_affected": [],
    "tests_added": []
  },
  "regression_potential": "high"
}
```

### Normal Changes (Basic Detail)
- Minor refactoring
- Significant adjustments
- Test implementations
- Important documentation

Log Format:
```json
{
  "type": "normal",
  "task_id": "T123",
  "component": "tests",
  "description": "Basic description",
  "files_changed": ["test1.py"]
}
```

### Minor Changes (Minimal Detail)
- Small fixes
- Documentation updates
- Cleanup tasks
- Style adjustments

Log Format:
```json
{
  "type": "minor",
  "task_id": "T123",
  "component": "docs",
  "description": "Short description"
}
```

## File Structure
```
logs/
├── main.json         # Critical changes only (max 1MB)
├── increments/       # All changes, auto-generated Task-IDs
│   ├── log_001.json 
│   └── log_002.json
└── archive/          # Quarterly consolidated logs
    ├── 2025_Q1.json
    └── 2024_Q4.json
```

### Technical System Logging
- Log Levels and Usage:
  * DEBUG: Development information (WebSocket messages, Audio data details)
  * INFO: Standard events (Connection status, Recording state)
  * WARNING: Non-critical issues (Connection loss, Buffer overflows)
  * ERROR: Critical errors (Device errors, System failures)

- Log Structure:
  ```python
  LOG_FORMAT = {
      'default': "%(asctime)s - %(levelname)s - %(message)s",
      'connection': "%(asctime)s - CONNECTION: %(message)s",
      'audio': "%(asctime)s - AUDIO: %(message)s",
      'text': "%(asctime)s - TEXT: %(message)s",
      'error': "%(asctime)s - ERROR: %(message)s"
  }
  ```

- Log File Management:
  * Daily rotation
  * Separate console and file handlers
  * Structured error logging
  * Debug information preservation

## Development Workflow

### Change Tracking Format
```json
{
  "timestamp": "ISO-8601",
  "description": "Change description",
  "changes": [
    {
      "type": "refactor|feat|fix|etc",
      "description": "Detailed change info"
    }
  ],
  "status": "in_development|completed|etc",
  "files": ["affected/files.py"]
}
```

### VSCode Snippets
1. **Standard Format** (Trigger: `commit⏎`)
```
feat(audio): overflow-handling implemented

- Buffer size optimized
- Overflow detection added
- Logging improved
```

2. **Complex Changes** (Trigger: `commitc⏎`)
```
refactor(timing): timing parameters centralized

- Parameters moved to config.py
- Documentation extended
- Modules adjusted:
  - WebSocket: Connection timing
  - Audio: Buffer timing
  - Text: Output timing
```

## Version Control Strategy
1. Regular commits on working states
2. Clear change documentation
3. Defined test protocol
4. Focus on relevant issues
5. Better use of version control

## Audio Processing Patterns

### Proof-of-Concept Results
1. **Tumbling Window**
   - 130ms average latency
   - Stable processing (27 windows/3.5s)
   - Overlapping windows for transitions
   - Status: Ready for implementation

2. **Queue-based Chunk Management**
   - Thread and async implementations
   - AudioChunk data model with metadata
   - Enhanced WebSocket integration
   - Status: Conceptually validated

3. **Audio Segmentation**
   - Speech segment detection
   - Energy-based classification
   - Parameter optimization required
   - Status: Partially validated

## Test Framework Architecture

### Speech Test Documentation
- Test cases in `tests/speech_test_cases.md` (maintained in German)
- Progress tracking in `tests/speech_test_progress.json`
- Automatic status updates
- Standardized test cases
- Focus on German speech recognition

### Test Execution Framework
1. **Pre-Test Setup**
   - Clear terminal
   - Fresh program start
   - Single instance check
   - Server logs check

2. **Test Execution**
   - Run single test
   - Analyze server logs
   - Check internal logs
   - Verify sentence processing

3. **Result Documentation**
   - Update speech_test_progress.json
   - Document results
   - Analyze errors
   - Plan next steps

### Server Log Analysis
- WhisperLive Server in WSL
- WSL Path: /home/michael/appdata/whisperlive/logs/
- Windows Access: W:\ (Network share from WSL)
- Portainer timestamps for event analysis
- Post-test log analysis for timing investigation

## Architecture Patterns

### 1. Communication
- WebSocket connection with auto-reconnect
- JSON message format
- Structured error recovery
- Connection state tracking

### 2. Data Processing
- Threaded audio recording
- Float32 normalization
- Buffer management
- Stream synchronization

### 3. Text Handling
- Window detection
- Input simulation
- Clipboard operations
- Sentence boundary detection

### 4. Error Recovery
- Automatic reconnection
- Buffer reset mechanisms
- State restoration
- Thread safety measures

## Collaboration Guidelines

### Environment Awareness
- Check running instances before starting new ones
- Verify system state before changes
- Consider side effects on running processes

### Error Handling Protocol
1. Understand full context before fixing
2. Verify problem understanding with team
3. Consider that "issues" might be intended
4. Document fix attempts and results

### Status Change Rules
- Explicit approval needed for:
  * Test completion marking
  * Next step transitions
  * Task completion
  * Project flow changes

## References
- Development logs: logs/increments/
- Investigation docs: docs/investigations/
- Test documentation: tests/docs/
- Technical setup: tech_context.md
