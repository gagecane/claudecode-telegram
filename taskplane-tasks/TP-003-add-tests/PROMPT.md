# TP-003: Add Basic Tests for bridge.py

## Summary
Add a basic unit test suite for `bridge.py` using pytest.

## Context to Read First
- `bridge.py` — understand the code structure and functions
- `pyproject.toml` — current project configuration

## Task Description

Create a test file `test_bridge.py` with unit tests for the core functions in `bridge.py`:

### Functions to Test

1. **`tmux_exists()`** — check if tmux session exists
   - Mock subprocess to return success/failure

2. **`get_recent_sessions()`** — parse history file
   - Test with valid JSONL data
   - Test with empty file
   - Test with missing file
   - Test limit parameter

3. **`get_session_id()`** — extract session ID from project path
   - Test with valid project path
   - Test with invalid path

4. **Helper functions** (if applicable):
   - Any text parsing/formatting functions

### Test Structure

```python
import pytest
from unittest.mock import patch, MagicMock
import sys
sys.path.insert(0, '.')
from bridge import tmux_exists, get_recent_sessions, get_session_id

@patch('bridge.subprocess.run')
def test_tmux_exists_true(mock_run):
    mock_run.return_value.returncode = 0
    assert tmux_exists() == True
```

## Acceptance Criteria

1. Create `test_bridge.py` in project root
2. Include tests for at least:
   - `tmux_exists()` (2 test cases: true/false)
   - `get_recent_sessions()` (3 test cases: valid data, empty, missing file)
   - `get_session_id()` (2 test cases: valid path, invalid path)
3. All tests pass: `pytest test_bridge.py` shows all passing
4. Tests use mocking for external dependencies (subprocess, file I/O)
5. Update `pyproject.toml` to include pytest as dev dependency (optional)

## Notes
- Use `unittest.mock` for mocking subprocess and file operations
- Create temporary files for file-based tests
- Keep tests simple and focused on logic, not integration
- Tests should be deterministic (no network calls, no real tmux)
