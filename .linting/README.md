# WhisperClient Linting
Version: 1.0
Timestamp: 2025-03-09 01:51 CET

## Quick Commands

```powershell
# Run all linters
./.linting/lint.ps1

# Run specific linters
./.linting/lint.ps1 -isort -black

# Run on specific files
./.linting/lint.ps1 -files "src/audio.py src/websocket.py"

# Apply automatic fixes
./.linting/lint.ps1 -fix
```
