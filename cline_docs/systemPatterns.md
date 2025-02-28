# System Architecture & Patterns
Version: 1.8
Timestamp: 2025-02-28 19:19 CET

## Document Purpose
This document outlines how the system is built, key technical decisions, architectural patterns, and development philosophies used throughout the WhisperClient project.

## Testing Philosophy

### Core Testing Axiom
> "The test framework is a tool, not a deliverable"

This axiom guides our testing approach:
1. Focus on core functionality over test infrastructure
2. Implement comprehensive tests only for complex issues
3. Prefer manual verification for straightforward features
4. Keep test framework minimal and maintainable
5. Add complexity only when truly needed

### Testing Strategy
1. **Essential Testing**
   - Core functionality must be tested
   - Focus on timing and integration
   - Verify critical paths
   - Document test purposes clearly
   - Tests evolve with development needs

2. **Test Runner Implementation**
   - Category-based execution (timing, integration, speech)
   - Minimal configuration (--verbose only)
   - Clear result reporting with emojis
   - Proper error handling
   - See test_runner_usage.md for details

2. **Manual Verification**
   - Preferred for straightforward features
   - Used for basic functionality checks
   - Appropriate for UI/UX testing
   - Efficient for quick validations

3. **Comprehensive Testing**
   - Reserved for complex issues
   - Used when debugging difficult problems
   - Implemented for critical components
   - Added when manual testing is insufficient

4. **Test Framework Guidelines**
   - Keep it simple and maintainable
   - Add features only when needed
   - Focus on utility over complexity
   - Support core development goals
   - Let tests evolve organically
   - Avoid premature test infrastructure
   - Create tests for specific problems
   - Validate approach through usage

## Memory Bank Workflow

### Critical Memory Bank Rules
1. **ALWAYS Check Memory Bank First**
   - Before ANY task or tool use
   - Before exploring other documentation
   - Before making ANY changes
   - No exceptions to this rule

2. **Memory Bank Verification**
   - Read ALL Memory Bank files
   - Verify versions and timestamps
   - Understand complete context
   - Document any missing information

3. **Memory Bank Warning**
   - Memory resets are complete
   - Previous context is ONLY in Memory Bank
   - Skipping Memory Bank leads to errors
   - Example: Task exploration before Memory Bank check can lead to misaligned solutions

4. **Memory Bank First Pattern**
   ```mermaid
   flowchart TD
       A[New Task] --> B[Check Memory Bank]
       B --> C{Complete Context?}
       C -->|No| D[Update Memory Bank]
       D --> B
       C -->|Yes| E[Proceed with Task]
   ```

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

### Logging Checklist
1. **When to Update Logs**
   - After implementing a new feature
   - After fixing a bug
   - After significant refactoring
   - After updating documentation
   - After changing configuration
   - Before committing changes to the repository

2. **Which Log Files to Update**
   - For all changes: Create a new incremental log in `logs/increments/`
   - For critical changes: Also add an entry to `logs/main.json`
   - For changes affecting tests: Update test documentation

3. **Log Format Guidelines**
   - Follow the format specified in the "Log Levels & Details" section
   - Use the correct log type (critical, normal, minor) based on the change
   - Include all relevant details (files changed, components affected, etc.)
   - Use ISO-8601 format for timestamps (YYYY-MM-DDThh:mm:ss+01:00)

4. **Memory Bank Integration**
   - Coordinate log updates with Memory Bank updates (not as separate steps)
   - As part of the same workflow, ensure:
     * `activeContext.md` reflects the latest changes
     * `progress.md` is updated with completed tasks and next steps
     * Version and timestamp are updated in all modified Memory Bank files
   - This is not a separate process but part of the existing Memory Bank protocol

5. **Verification Steps**
   - Verify log entries are correctly formatted
   - Ensure all affected files are listed
   - Check that timestamps are accurate
   - Confirm task IDs are consistent across logs and Memory Bank

This checklist ensures consistent and comprehensive logging throughout the development process, maintaining a clear history of changes and facilitating knowledge transfer across memory resets.

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

### Commit Message Guidelines
1. **Prefer Direct Commit Messages**
   - Use `git commit -m "message"` for simple commits
   - For multi-line messages, use `git commit` (without -m) to open editor
   - Avoid creating temporary files for commit messages

2. **When Files Are Necessary**
   - Only use files for complex commit messages when absolutely necessary
   - ALWAYS clean up temporary message files immediately after use
   - Add temporary message files to .gitignore (e.g., *commit_msg.txt)

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
