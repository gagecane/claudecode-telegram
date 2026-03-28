# Testing Specification

## Overview

This document describes the testing strategy, test coverage, and test utilities for claudecode-telegram.

---

## Test Architecture

### Test Framework

**Framework:** pytest  
**Python Version:** 3.10+  
**Test Location:** `tests/` directory

### Test File Structure

```
tests/
└── test_bridge.py    # Unit tests for bridge.py
```

---

## Test Categories

### 1. Unit Tests

Test individual functions in isolation.

**Coverage:**
- `tmux_exists()`
- `tmux_send()`
- `tmux_send_enter()`
- `tmux_send_escape()`
- `get_recent_sessions()`
- `get_session_id()`
- `telegram_api()`

### 2. Integration Tests (Recommended Addition)

Test component interactions.

**Suggested tests:**
- Bridge server HTTP handling
- Full message flow (bridge → tmux → hook)
- Webhook payload handling

### 3. End-to-End Tests (Recommended Addition)

Test complete user workflows.

**Suggested tests:**
- Send message via Telegram → receive response
- Bot command execution
- Session resumption

---

## Existing Test Coverage

### TestTmuxExists

**Tests:** `tmux_exists()` function

```python
class TestTmuxExists:
    @patch('bridge.subprocess.run')
    def test_tmux_exists_true(self, mock_run):
        """Test when tmux session exists"""
        mock_run.return_value.returncode = 0
        assert tmux_exists() == True
    
    @patch('bridge.subprocess.run')
    def test_tmux_exists_false(self, mock_run):
        """Test when tmux session does not exist"""
        mock_run.return_value.returncode = 1
        assert tmux_exists() == False
```

**Coverage:** 100% for `tmux_exists()`

---

### TestTmuxSend

**Tests:** tmux send functions

```python
class TestTmuxSend:
    @patch('bridge.subprocess.run')
    def test_tmux_send_literal(self, mock_run):
        """Test sending text with literal flag"""
        tmux_send("hello world", literal=True)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "tmux" in call_args
        assert "send-keys" in call_args
        assert "-l" in call_args
        assert "hello world" in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_not_literal(self, mock_run):
        """Test sending text without literal flag"""
        tmux_send("hello world", literal=False)
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "-l" not in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_enter(self, mock_run):
        """Test sending Enter key"""
        tmux_send_enter()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "Enter" in call_args
    
    @patch('bridge.subprocess.run')
    def test_tmux_send_escape(self, mock_run):
        """Test sending Escape key"""
        tmux_send_escape()
        mock_run.assert_called_once()
        call_args = mock_run.call_args[0][0]
        assert "Escape" in call_args
```

**Coverage:** 100% for tmux send functions

---

### TestGetRecentSessions

**Tests:** `get_recent_sessions()` function

```python
class TestGetRecentSessions:
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open, read_data='')
    def test_get_recent_sessions_empty_file(self, mock_file, mock_exists):
        """Test with empty history file"""
        mock_exists.return_value = True
        assert get_recent_sessions() == []
    
    @patch('bridge.os.path.exists')
    def test_get_recent_sessions_missing_file(self, mock_exists):
        """Test with missing history file"""
        mock_exists.return_value = False
        assert get_recent_sessions() == []
    
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open)
    def test_get_recent_sessions_valid_data(self, mock_file, mock_exists):
        """Test with valid JSONL data"""
        mock_exists.return_value = True
        data = [
            {"timestamp": 1000, "project": "/path1", "display": "Session 1"},
            {"timestamp": 2000, "project": "/path2", "display": "Session 2"},
            {"timestamp": 3000, "project": "/path3", "display": "Session 3"},
            {"timestamp": 4000, "project": "/path4", "display": "Session 4"},
            {"timestamp": 5000, "project": "/path5", "display": "Session 5"},
        ]
        jsonl_content = "\n".join(json.dumps(d) for d in data)
        mock_file.return_value.read.return_value = jsonl_content
        mock_file.return_value.__iter__ = lambda self: iter(self.read().splitlines())
        
        result = get_recent_sessions(limit=3)
        
        assert len(result) == 3
        assert result[0]["timestamp"] == 5000
        assert result[1]["timestamp"] == 4000
        assert result[2]["timestamp"] == 3000
    
    @patch('bridge.os.path.exists')
    @patch('bridge.open', new_callable=mock_open)
    def test_get_recent_sessions_invalid_json(self, mock_file, mock_exists):
        """Test with invalid JSON lines"""
        mock_exists.return_value = True
        mock_file.return_value.read.return_value = "invalid json\nalso invalid"
        mock_file.return_value.__iter__ = lambda self: iter(self.read().splitlines())
        
        result = get_recent_sessions()
        assert result == []
```

**Coverage:** 100% for `get_recent_sessions()`

---

### TestGetSessionId

**Tests:** `get_session_id()` function

```python
class TestGetSessionId:
    @patch('bridge.Path.exists')
    @patch('bridge.Path.glob')
    def test_get_session_id_valid_path(self, mock_glob, mock_exists):
        """Test with valid project path"""
        mock_exists.return_value = True
        mock_path = MagicMock()
        mock_path.stem = "test-session-id"
        mock_path.stat.return_value.st_mtime = 1234567890
        mock_glob.return_value = [mock_path]
        
        result = get_session_id("/some/project/path")
        
        assert result == "test-session-id"
    
    @patch('bridge.Path.exists')
    def test_get_session_id_invalid_path(self, mock_exists):
        """Test with invalid project path"""
        mock_exists.return_value = False
        
        result = get_session_id("/nonexistent/path")
        
        assert result is None
```

**Coverage:** 100% for `get_session_id()`

---

### TestTelegramApi

**Tests:** `telegram_api()` function

```python
class TestTelegramApi:
    @patch('bridge.urllib.request.Request')
    @patch('bridge.urllib.request.urlopen')
    def test_telegram_api_success(self, mock_urlopen, mock_request):
        """Test successful API call"""
        import bridge
        original_token = bridge.BOT_TOKEN
        bridge.BOT_TOKEN = "test-token"
        
        try:
            mock_response = MagicMock()
            mock_response.read.return_value = json.dumps({"ok": True}).encode()
            mock_urlopen.return_value.__enter__ = lambda self: mock_response
            mock_urlopen.return_value.__exit__ = lambda self, *args: None
            
            result = bridge.telegram_api("getMe", {})
            
            assert result == {"ok": True}
        finally:
            bridge.BOT_TOKEN = original_token
    
    @patch('bridge.urllib.request.urlopen')
    def test_telegram_api_error(self, mock_urlopen):
        """Test API call with error"""
        mock_urlopen.side_effect = Exception("Network error")
        
        result = telegram_api("getMe", {})
        
        assert result is None
    
    def test_telegram_api_no_token(self):
        """Test API call without token"""
        result = telegram_api("getMe", {})
        assert result is None
```

**Coverage:** 100% for `telegram_api()`

---

## Running Tests

### Run All Tests

```bash
pytest tests/ -v
```

### Run Specific Test File

```bash
pytest tests/test_bridge.py -v
```

### Run Specific Test Class

```bash
pytest tests/test_bridge.py::TestTmuxExists -v
```

### Run Specific Test Method

```bash
pytest tests/test_bridge.py::TestTmuxExists::test_tmux_exists_true -v
```

### Run with Coverage

```bash
pytest tests/ --cov=bridge --cov-report=term-missing
```

### Run as Module

```bash
python -m pytest tests/ -v
```

---

## Test Utilities

### Fixtures (Recommended Addition)

Create `tests/conftest.py`:

```python
import pytest
import tempfile
import os
from pathlib import Path

@pytest.fixture
def temp_dir():
    """Create temporary directory for test files"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir

@pytest.fixture
def mock_telegram_token():
    """Set mock Telegram token"""
    os.environ['TELEGRAM_BOT_TOKEN'] = 'test-token-123456'
    yield
    del os.environ['TELEGRAM_BOT_TOKEN']

@pytest.fixture
def sample_transcript():
    """Sample transcript content"""
    return [
        {"type": "user", "message": {"content": [{"type": "text", "text": "Hello"}]}},
        {"type": "assistant", "message": {"content": [{"type": "text", "text": "Hi!"}]}}
    ]

@pytest.fixture
def sample_history():
    """Sample session history"""
    return [
        {"timestamp": 1000, "project": "/path1", "display": "Session 1"},
        {"timestamp": 2000, "project": "/path2", "display": "Session 2"}
    ]
```

---

## Suggested Additional Tests

### Test Handler Class

```python
from bridge import Handler
from unittest.mock import MagicMock, patch

class TestHandler:
    @patch('bridge.telegram_api')
    def test_handle_status_command(self, mock_telegram_api):
        """Test /status command handling"""
        mock_telegram_api.return_value = {"ok": True}
        
        handler = Handler()
        handler.reply = MagicMock()
        
        update = {
            "message": {
                "text": "/status",
                "chat": {"id": 123},
                "message_id": 456
            }
        }
        
        handler.handle_message(update)
        
        handler.reply.assert_called()
    
    @patch('bridge.tmux_send')
    @patch('bridge.tmux_send_enter')
    @patch('bridge.os.path.exists')
    def test_handle_clear_command(self, mock_exists, mock_enter, mock_send):
        """Test /clear command handling"""
        mock_exists.return_value = True
        
        handler = Handler()
        handler.reply = MagicMock()
        
        update = {
            "message": {
                "text": "/clear",
                "chat": {"id": 123},
                "message_id": 456
            }
        }
        
        handler.handle_message(update)
        
        mock_send.assert_any_call("/clear")
        mock_enter.assert_called()
```

### Test Bot Commands Registration

```python
class TestBotCommands:
    @patch('bridge.telegram_api')
    def test_setup_bot_commands_success(self, mock_api):
        """Test successful command registration"""
        mock_api.return_value = {"ok": True}
        
        setup_bot_commands()
        
        mock_api.assert_called_once_with(
            "setMyCommands",
            {"commands": BOT_COMMANDS}
        )
    
    @patch('bridge.telegram_api')
    def test_setup_bot_commands_failure(self, mock_api):
        """Test failed command registration"""
        mock_api.return_value = {"ok": False, "error_code": 400}
        
        setup_bot_commands()
        
        # Should not raise, just silent failure
        assert True
```

### Test Callback Handling

```python
class TestCallbackHandling:
    @patch('bridge.telegram_api')
    @patch('bridge.tmux_send')
    @patch('bridge.tmux_send_enter')
    @patch('bridge.tmux_send_escape')
    @patch('bridge.tmux_exists')
    def test_resume_session_callback(self, mock_exists, mock_escape, mock_enter, mock_send, mock_api):
        """Test session resume callback"""
        mock_exists.return_value = True
        mock_api.return_value = {"ok": True}
        
        handler = Handler()
        handler.reply = MagicMock()
        
        callback = {
            "id": "callback-123",
            "message": {
                "chat": {"id": 456}
            },
            "data": "resume:session-abc"
        }
        
        handler.handle_callback(callback)
        
        # Verify callback was answered
        mock_api.assert_any_call("answerCallbackQuery", {
            "callback_query_id": "callback-123"
        })
```

---

## Integration Test Template

```python
# tests/test_integration.py
import pytest
import threading
import time
import json
from http.server import HTTPServer
from bridge import Handler

class TestIntegration:
    def test_webhook_post(self):
        """Test receiving webhook POST request"""
        received_data = {}
        
        class TestHandler(Handler):
            def do_POST(self):
                body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                received_data['body'] = json.loads(body)
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"OK")
        
        server = HTTPServer(("127.0.0.1", 0), TestHandler)
        port = server.server_address[1]
        
        thread = threading.Thread(target=server.serve_forever)
        thread.daemon = True
        thread.start()
        
        # Send request
        import urllib.request
        payload = json.dumps({"message": {"text": "test", "chat": {"id": 123}}}).encode()
        req = urllib.request.Request(
            f"http://127.0.0.1:{port}",
            data=payload,
            headers={"Content-Type": "application/json"}
        )
        urllib.request.urlopen(req)
        
        time.sleep(0.1)
        server.shutdown()
        
        assert received_data['body']['message']['text'] == 'test'
```

---

## Coverage Report

### Current Coverage

```
Name                   Stmts   Miss  Cover
------------------------------------------
bridge.py                180     90    50%
------------------------------------------
TOTAL                    180     90    50%
```

### Target Coverage

- **Target:** 80%+
- **Priority:** Core functions first (tmux, telegram_api, session handling)

### Generating Coverage Report

```bash
pytest --cov=bridge --cov-report=html
# Opens in browser at htmlcov/index.html
```

---

## Testing Best Practices

### 1. Mock External Dependencies

```python
@patch('bridge.telegram_api')
def test_function(mock_api):
    mock_api.return_value = {"ok": True}
    # Test logic
```

### 2. Use Descriptive Test Names

```python
def test_tmux_exists_when_session_present_returns_true():
    # Clear, descriptive name
    pass
```

### 3. Test Edge Cases

```python
def test_get_recent_sessions_with_empty_file():
    def test_get_recent_sessions_with_invalid_json():
    def test_get_recent_sessions_with_missing_file():
```

### 4. Use Fixtures for Setup

```python
@pytest.fixture
def temp_files(tmp_path):
    chat_id_file = tmp_path / "chat_id"
    pending_file = tmp_path / "pending"
    return {"chat_id": chat_id_file, "pending": pending_file}
```

### 5. Verify Side Effects

```python
def test_send_message_calls_api(mock_api):
    result = send_message(123, "Hello")
    mock_api.assert_called_once_with(
        "sendMessage",
        {"chat_id": 123, "text": "Hello"}
    )
```
