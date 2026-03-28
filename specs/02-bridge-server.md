# Bridge Server Specification

## Overview

The bridge server (`bridge.py`) is a lightweight HTTP server that receives Telegram webhook updates and forwards messages to a running Claude Code session via tmux.

---

## Module Interface

### Imports

```python
from http.server import HTTPServer, BaseHTTPRequestHandler
import os, json, subprocess, threading, time, urllib.request
from pathlib import Path
```

### Configuration Constants

| Constant | Type | Default | Description |
|----------|------|---------|-------------|
| `TMUX_SESSION` | str | `"claude"` | tmux session name |
| `CHAT_ID_FILE` | Path | `~/.claude/telegram_chat_id` | Chat ID storage |
| `PENDING_FILE` | Path | `~/.claude/telegram_pending` | Pending response flag |
| `HISTORY_FILE` | Path | `~/.claude/history.jsonl` | Session history |
| `BOT_TOKEN` | str | *env var* | Telegram bot token |
| `PORT` | int | `8080` | Server port |

---

## API Reference

### Bot Commands

```python
BOT_COMMANDS = [
    {"command": "clear", "description": "Clear conversation"},
    {"command": "resume", "description": "Resume session (shows picker)"},
    {"command": "continue_", "description": "Continue most recent session"},
    {"command": "loop", "description": "Ralph Loop: /loop <prompt>"},
    {"command": "stop", "description": "Interrupt Claude (Escape)"},
    {"command": "status", "description": "Check tmux status"},
]
```

### Blocked Commands

```python
BLOCKED_COMMANDS = [
    "/mcp", "/help", "/settings", "/config", "/model", "/compact", "/cost",
    "/doctor", "/init", "/login", "/logout", "/memory", "/permissions",
    "/pr", "/review", "/terminal", "/vim", "/approved-tools", "/listen"
]
```

These commands are blocked because they require interactive CLI access.

---

## Functions

### `telegram_api(method, data) -> dict | None`

Makes HTTP POST request to Telegram Bot API.

**Parameters:**
- `method`: API endpoint (e.g., "sendMessage", "getMe")
- `data`: Request body as dict

**Returns:** Parsed JSON response or `None` on error

**Example:**
```python
result = telegram_api("sendMessage", {
    "chat_id": 123456789,
    "text": "Hello!"
})
```

---

### `setup_bot_commands() -> None`

Registers bot commands with Telegram via `setMyCommands` API.

**Side Effects:** Prints confirmation on success

---

### `send_typing_loop(chat_id) -> None`

Background thread that sends typing indicator to Telegram every 4 seconds while pending file exists.

**Parameters:**
- `chat_id`: Target chat ID

**Lifecycle:** Runs until `PENDING_FILE` is deleted

---

### `tmux_exists() -> bool`

Checks if tmux session exists.

**Returns:** `True` if session exists, `False` otherwise

**Implementation:**
```bash
tmux has-session -t <session_name>
```

---

### `tmux_send(text, literal=True) -> None`

Sends text to tmux session.

**Parameters:**
- `text`: Text to send
- `literal`: If True, use `-l` flag (literal mode, no key bindings)

**Implementation:**
```bash
tmux send-keys -t <session> [-l] <text>
```

---

### `tmux_send_enter() -> None`

Sends Enter key to tmux session.

---

### `tmux_send_escape() -> None`

Sends Escape key to tmux session.

---

### `get_recent_sessions(limit=5) -> list[dict]`

Reads and returns most recent sessions from history file.

**Parameters:**
- `limit`: Maximum sessions to return (default: 5)

**Returns:** List of session dicts sorted by timestamp descending

**File Format:** JSONL with fields:
- `timestamp`: Unix timestamp
- `project`: Project path
- `display`: Display name

---

### `get_session_id(project_path) -> str | None`

Extracts session ID from project path.

**Parameters:**
- `project_path`: Path to project directory

**Returns:** Session ID (filename stem of most recent .jsonl) or `None`

**Search Pattern:**
```
~/.claude/projects/<encoded_path>/<session_id>.jsonl
```

---

## Handler Class

### `Handler(BaseHTTPRequestHandler)`

HTTP request handler for Telegram webhooks.

#### Methods

##### `do_POST() -> None`

Handles incoming webhook POST requests.

**Flow:**
1. Read request body
2. Parse JSON
3. Route to `handle_callback()` or `handle_message()`
4. Respond with 200 OK

##### `do_GET() -> None`

Simple health check endpoint.

**Response:** `200 OK` with body "Claude-Telegram Bridge"

##### `handle_callback(callback_query) -> None`

Handles inline keyboard callbacks (session resumption).

**Supported Actions:**
- `resume:<session_id>`: Resume specific session
- `continue_recent`: Continue most recent session

**Flow:**
1. Extract chat_id and callback data
2. Answer callback query (clears loading state)
3. Exit current conversation (`/exit`)
4. Launch new/resumed session
5. Reply with confirmation

##### `handle_message(update) -> None`

Handles incoming messages and commands.

**Command Handlers:**

| Command | Action |
|---------|--------|
| `/status` | Check tmux session status |
| `/stop` | Send Escape, remove pending flag |
| `/clear` | Clear current conversation |
| `/continue_` | Continue most recent session |
| `/loop <prompt>` | Start Ralph Loop (5 iterations) |
| `/resume` | Show session picker keyboard |

**Blocked Commands:** Returns error message for commands in `BLOCKED_COMMANDS`

**Regular Messages:**
1. Save chat ID to file
2. Write pending flag with timestamp
3. Send typing indicator thread
4. Inject message into tmux
5. Set checkmark reaction on user message

##### `reply(chat_id, text) -> None`

Sends message to chat.

**Parameters:**
- `chat_id`: Target chat ID
- `text`: Message text

---

## Main Function

### `main() -> None`

Entry point. Initializes server and starts listening.

**Flow:**
1. Validate `BOT_TOKEN` environment variable
2. Register bot commands via API
3. Print status message
4. Start HTTP server (blocks on `serve_forever()`)
5. Handle graceful shutdown on Ctrl+C

---

## Error Handling

### Telegram API Errors

```python
try:
    with urllib.request.urlopen(req, timeout=10) as r:
        return json.loads(r.read())
except Exception as e:
    print(f"Telegram API error: {e}")
    return None
```

All Telegram API calls return `None` on error, allowing graceful degradation.

### Missing Files

- `CHAT_ID_FILE`: Hook exits silently
- `PENDING_FILE`: Hook exits (no response sent)
- `HISTORY_FILE`: Returns empty session list

---

## Threading Model

### Typing Indicator Thread

```python
threading.Thread(
    target=send_typing_loop,
    args=(chat_id,),
    daemon=True  # Does not block shutdown
).start()
```

**Characteristics:**
- Daemon thread (exits with main process)
- One thread per message
- Automatically terminates when pending file deleted

---

## Performance Considerations

1. **Single-threaded HTTP:** `http.server` handles one request at a time
2. **Blocking tmux calls:** `subprocess.run()` blocks until complete
3. **No connection pooling:** Each Telegram API call creates new connection
4. **Sufficient for:** Single user, moderate message frequency

---

## Testing Hooks

### Mockable Functions

```python
from unittest.mock import patch

with patch('bridge.telegram_api') as mock_api:
    mock_api.return_value = {"ok": True}
    result = setup_bot_commands()
```

### Test Fixtures

```python
import tempfile
import os

def test_with_temp_files():
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ['TELEGRAM_BOT_TOKEN'] = 'test'
        # Set custom paths for testing
        bridge.CHAT_ID_FILE = os.path.join(tmpdir, 'chat_id')
        bridge.PENDING_FILE = os.path.join(tmpdir, 'pending')
        # Run test
```

---

## Extension Points

### Adding New Commands

1. Add to `BOT_COMMANDS` list
2. Add handler in `handle_message()`:
```python
if cmd == "/newcommand":
    # Implementation
    self.reply(chat_id, "Result")
    return
```

### Custom Response Formatting

Override `reply()` method or create new method:
```python
def reply_html(self, chat_id, text):
    telegram_api("sendMessage", {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML"
    })
```

### Rate Limiting

Add before Telegram API calls:
```python
import time
from datetime import datetime, timedelta

_last_call = {}

def rate_limited_telegram_api(method, data, chat_id=None):
    if chat_id and chat_id in _last_call:
        if datetime.now() - _last_call[chat_id] < timedelta(seconds=1):
            time.sleep(0.1)  # Respect Telegram rate limits
    _last_call[chat_id] = datetime.now()
    return telegram_api(method, data)
```
