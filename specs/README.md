# Specifications

## Overview

This directory contains specification documents for the **claudecode-telegram** project — a Telegram bot bridge for Claude Code.

---

## Document Index

### Architecture & Design

| Document | Description |
|----------|-------------|
| [01-system-architecture.md](./01-system-architecture.md) | High-level system design, component diagram, data flow |
| [02-bridge-server.md](./02-bridge-server.md) | Bridge server (bridge.py) API reference and implementation details |
| [03-stop-hook.md](./03-stop-hook.md) | Stop hook (send-to-telegram.sh) execution flow and formatting |

### Reference Documentation

| Document | Description |
|----------|-------------|
| [04-api-reference.md](./04-api-reference.md) | Telegram Bot API endpoints used by the project |
| [05-configuration-reference.md](./05-configuration-reference.md) | Environment variables, config files, settings |

### Testing

| Document | Description |
|----------|-------------|
| [06-testing-specification.md](./06-testing-specification.md) | Test coverage, test utilities, suggested additions |

---

## Quick Navigation

### For Developers

1. **Understanding the system:** Start with [01-system-architecture.md](./01-system-architecture.md)
2. **Modifying bridge.py:** See [02-bridge-server.md](./02-bridge-server.md)
3. **Modifying the hook:** See [03-stop-hook.md](./03-stop-hook.md)
4. **Adding tests:** See [06-testing-specification.md](./06-testing-specification.md)

### For Users

1. **Installation:** See [README.md](../README.md)
2. **Configuration:** See [05-configuration-reference.md](./05-configuration-reference.md)
3. **API details:** See [04-api-reference.md](./04-api-reference.md)

---

## System Diagram

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Telegram  │────▶│ Cloudflare   │────▶│  Bridge     │
│     API     │     │   Tunnel     │     │  Server     │
└─────────────┘     └──────────────┘     └──────┬──────┘
                                                │
                                                ▼
                                       ┌─────────────┐
                                       │    tmux     │
                                       │   Session   │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │ Claude Code │
                                       │    CLI      │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │   Stop Hook │
                                       │ (send back) │
                                       └──────┬──────┘
                                              │
                                              ▼
                                       ┌─────────────┐
                                       │  Telegram   │
                                       │    API      │
                                       └─────────────┘
```

---

## Component Summary

### Bridge Server (bridge.py)

- **Type:** HTTP Server
- **Purpose:** Receives Telegram webhooks, forwards to Claude via tmux
- **Port:** Configurable (default: 8080)
- **Commands:** `/status`, `/clear`, `/resume`, `/loop`, `/stop`

### Stop Hook (hooks/send-to-telegram.sh)

- **Type:** Bash script with embedded Python
- **Purpose:** Reads transcript, formats response, sends to Telegram
- **Trigger:** Claude Code Stop hook event
- **Features:** HTML formatting, code blocks, inline code

---

## Key Design Patterns

### 1. Pending Flag Pattern

Bridge writes `~/.claude/telegram_pending` when receiving Telegram message. Hook only responds if file exists.

**Purpose:** Ensures hook only responds to Telegram-initiated messages.

### 2. tmux as Message Transport

Uses `tmux send-keys` to inject messages into Claude Code session.

**Purpose:** No modification to Claude Code required.

### 3. Inline Python in Bash

Hook embeds Python for complex text processing.

**Purpose:** Single file deployment, powerful string manipulation.

---

## File Structure

```
claudecode-telegram/
├── bridge.py                    # Main bridge server
├── hooks/
│   └── send-to-telegram.sh     # Stop hook script
├── tests/
│   └── test_bridge.py          # Unit tests
├── pyproject.toml              # Python package config
├── README.md                   # User documentation
└── specs/                      # This directory
    ├── README.md               # This file
    ├── 01-system-architecture.md
    ├── 02-bridge-server.md
    ├── 03-stop-hook.md
    ├── 04-api-reference.md
    ├── 05-configuration-reference.md
    └── 06-testing-specification.md
```

---

## State Files

| File | Purpose | Created By |
|------|---------|------------|
| `~/.claude/telegram_chat_id` | Last active chat ID | Bridge |
| `~/.claude/telegram_pending` | Pending response flag | Bridge |
| `~/.claude/history.jsonl` | Session history | Claude Code |

---

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `TELEGRAM_BOT_TOKEN` | Yes | — | Bot token from BotFather |
| `TMUX_SESSION` | No | `claude` | tmux session name |
| `PORT` | No | `8080` | Bridge server port |

---

## Dependencies

### Runtime

- Python 3.10+
- tmux
- cloudflared
- jq (in hook)

### Development

- pytest

---

## Related Documentation

- [README.md](../README.md) — User guide and installation
- [pyproject.toml](../pyproject.toml) — Package configuration
- [test_bridge.py](../tests/test_bridge.py) — Test suite

---

## License

MIT — See [LICENSE](../LICENSE) if present, otherwise inherited from parent repository.
