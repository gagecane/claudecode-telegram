# Configuration Reference Specification

## Overview

This document describes all configuration options for claudecode-telegram.

---

## Environment Variables

### TELEGRAM_BOT_TOKEN (Required)

**Description:** Telegram bot token obtained from BotFather  
**Type:** String  
**Default:** None (must be set)  
**Example:** `123456789:ABCdefGHIjklMNOpqrsTUVwxyz`

**How to obtain:**
1. Message @BotFather on Telegram
2. Send `/newbot` command
3. Follow prompts to name your bot
4. Receive token

**Usage:**
```bash
export TELEGRAM_BOT_TOKEN="your_token_here"
python bridge.py
```

---

### TMUX_SESSION

**Description:** Name of tmux session running Claude Code  
**Type:** String  
**Default:** `"claude"`  
**Example:** `"my-claude-session"`

**Usage:**
```bash
# Start tmux with custom name
tmux new -s my-claude-session
claude --dangerously-skip-permissions

# Set env var for bridge
export TMUX_SESSION="my-claude-session"
python bridge.py
```

---

### PORT

**Description:** Port for bridge HTTP server  
**Type:** Integer  
**Default:** `8080`  
**Example:** `3000`

**Usage:**
```bash
export PORT=3000
python bridge.py
```

**Note:** Port must not be in use. Cloudflare tunnel will forward to this port.

---

## State Files

### ~/.claude/telegram_chat_id

**Description:** Stores the chat ID of the last active Telegram conversation  
**Type:** Plain text file  
**Content:** Integer chat ID  
**Created by:** Bridge server  
**Read by:** Stop hook

**Example content:**
```
123456789
```

**Lifecycle:**
- Written by bridge on each incoming message
- Read by hook to determine response target
- Overwritten on each new conversation

---

### ~/.claude/telegram_pending

**Description:** Flag file indicating a pending response to Telegram  
**Type:** Plain text file  
**Content:** Unix timestamp  
**Created by:** Bridge server  
**Read/Deleted by:** Stop hook

**Example content:**
```
1711642800
```

**Lifecycle:**
- Created by bridge when Telegram message received
- Read by hook to validate Telegram-initiated message
- Deleted by hook after response sent or on timeout

**Timeout:** 600 seconds (10 minutes)

---

### ~/.claude/history.jsonl

**Description:** Session history for resumption feature  
**Type:** JSON Lines file  
**Created by:** Claude Code  
**Read by:** Bridge server

**Format:** One JSON object per line

**Example:**
```jsonl
{"timestamp":1711642800,"project":"/Users/user/project1","display":"Project One","session_id":"sess-abc123"}
{"timestamp":1711643000,"project":"/Users/user/project2","display":"Project Two","session_id":"sess-def456"}
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `timestamp` | integer | Unix timestamp |
| `project` | string | Project path |
| `display` | string | Display name |
| `session_id` | string | Session identifier |

---

## Claude Code Settings

### ~/.claude/settings.json

**Description:** Claude Code configuration file  
**Type:** JSON  
**Purpose:** Configure Stop hook

**Required configuration:**

```json
{
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/send-to-telegram.sh"
          }
        ]
      }
    ]
  }
}
```

**Full example:**

```json
{
  "model": "claude-3-5-sonnet",
  "hooks": {
    "Stop": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "~/.claude/hooks/send-to-telegram.sh"
          }
        ]
      }
    ]
  },
  "context": {
    "enableProjectContext": true
  }
}
```

---

## Bot Commands Configuration

### BOT_COMMANDS (bridge.py)

**Description:** List of commands registered with Telegram  
**Type:** List of dicts  
**Location:** `bridge.py` module level

**Default:**

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

**To add a command:**

1. Add to `BOT_COMMANDS` list
2. Implement handler in `handle_message()`

**Example:**

```python
BOT_COMMANDS = [
    # ... existing commands ...
    {"command": "help", "description": "Show help message"},
]

# In handle_message():
if cmd == "/help":
    self.reply(chat_id, "Available commands:\n/status, /clear, /resume, /loop, /stop")
    return
```

---

## Blocked Commands Configuration

### BLOCKED_COMMANDS (bridge.py)

**Description:** Commands that require interactive access  
**Type:** List of strings  
**Location:** `bridge.py` module level

**Default:**

```python
BLOCKED_COMMANDS = [
    "/mcp", "/help", "/settings", "/config", "/model", "/compact", "/cost",
    "/doctor", "/init", "/login", "/logout", "/memory", "/permissions",
    "/pr", "/review", "/terminal", "/vim", "/approved-tools", "/listen"
]
```

**Purpose:** These commands require interactive CLI and don't work via message injection.

---

## Hook Configuration

### send-to-telegram.sh Variables

**Description:** Variables in hook script  
**Location:** `hooks/send-to-telegram.sh`

**TELEGRAM_BOT_TOKEN:**
```bash
TELEGRAM_BOT_TOKEN="${TELEGRAM_BOT_TOKEN:-YOUR_BOT_TOKEN_HERE}"
```

**Usage:** Set via environment variable or edit script directly.

**Recommended:** Use environment variable:
```bash
export TELEGRAM_BOT_TOKEN="your_token"
```

---

## Cloudflare Tunnel Configuration

### Command-line Options

**Basic usage:**
```bash
cloudflared tunnel --url http://localhost:8080
```

**With custom port:**
```bash
cloudflared tunnel --url http://localhost:$PORT
```

**Persistent tunnel (recommended for production):**

1. Login to Cloudflare:
```bash
cloudflared login
```

2. Create tunnel:
```bash
cloudflared tunnel create claudecode-telegram
```

3. Configure DNS (in Cloudflare dashboard)

4. Run tunnel:
```bash
cloudflared tunnel run claudecode-telegram
```

---

## Webhook URL Configuration

### Setting the Webhook

**Command:**
```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=https://YOUR-TUNNEL-URL.trycloudflare.com"
```

**Response:**
```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

### Verifying Webhook

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

**Response:**
```json
{
  "ok": true,
  "result": {
    "url": "https://abc123.trycloudflare.com",
    "has_custom_certificate": false,
    "pending_update_count": 0,
    "last_error_date": null
  }
}
```

---

## Configuration Checklist

### Bridge Server

- [ ] `TELEGRAM_BOT_TOKEN` set
- [ ] Optional: `TMUX_SESSION` set (if not using default "claude")
- [ ] Optional: `PORT` set (if not using default 8080)
- [ ] tmux installed
- [ ] cloudflared installed

### Claude Code

- [ ] Stop hook configured in `~/.claude/settings.json`
- [ ] Hook script copied to `~/.claude/hooks/`
- [ ] Hook script made executable
- [ ] Bot token set in hook (or via env var)

### Telegram

- [ ] Bot created via @BotFather
- [ ] Bot token obtained
- [ ] Webhook URL set

### Infrastructure

- [ ] tmux session created (`tmux new -s claude`)
- [ ] Claude Code running in session
- [ ] Bridge server running (`python bridge.py`)
- [ ] Cloudflare tunnel running

---

## Environment-Specific Configurations

### Development

```bash
# .env.dev
TELEGRAM_BOT_TOKEN="dev_token"
TMUX_SESSION="claude-dev"
PORT=8080
```

### Production

```bash
# .env.prod
TELEGRAM_BOT_TOKEN="prod_token"
TMUX_SESSION="claude-prod"
PORT=8080
```

### Docker (if containerized)

```dockerfile
ENV TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}
ENV TMUX_SESSION=claude
ENV PORT=8080
```

---

## Troubleshooting Configuration

### Bot Not Responding

1. Check token in bridge:
```bash
echo $TELEGRAM_BOT_TOKEN
```

2. Check token in hook:
```bash
grep TELEGRAM_BOT_TOKEN ~/.claude/hooks/send-to-telegram.sh
```

3. Verify token format (should be `123456789:ABCdef...`)

### Hook Not Firing

1. Check settings.json:
```bash
cat ~/.claude/settings.json | jq '.hooks.Stop'
```

2. Verify hook exists:
```bash
ls -la ~/.claude/hooks/send-to-telegram.sh
```

3. Check hook permissions:
```bash
file ~/.claude/hooks/send-to-telegram.sh
# Should show: executable
```

### Webhook Not Receiving Updates

1. Check webhook status:
```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/getWebhookInfo"
```

2. Verify tunnel is running:
```bash
ps aux | grep cloudflared
```

3. Check bridge is listening:
```bash
lsof -i :$PORT
```

### tmux Session Not Found

1. Check session exists:
```bash
tmux list-sessions
```

2. Verify session name matches:
```bash
echo $TMUX_SESSION  # Should match tmux session name
```

3. Create session if missing:
```bash
tmux new -s $TMUX_SESSION
```
