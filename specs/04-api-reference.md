# API Reference Specification

## Overview

This document describes all external APIs used by claudecode-telegram.

---

## Telegram Bot API

**Base URL:** `https://api.telegram.org/bot<TOKEN>`

**Authentication:** Bot token in URL path

---

### sendMessage

Send text message to chat.

#### Request

**Method:** POST  
**Endpoint:** `/sendMessage`  
**Content-Type:** `application/json`

**Body:**
```json
{
  "chat_id": integer,
  "text": string,
  "parse_mode": "HTML" | "Markdown" | "MarkdownV2",  // optional
  "disable_web_page_preview": boolean,  // optional
  "message_thread_id": integer  // optional (for topics)
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `chat_id` | integer | Yes | Unique chat identifier |
| `text` | string | Yes | Text message (1-4096 characters) |
| `parse_mode` | string | No | Format: "HTML", "Markdown", or "MarkdownV2" |
| `disable_web_page_preview` | boolean | No | Disable link previews |

#### Response

```json
{
  "ok": true,
  "result": {
    "message_id": 12345,
    "from": {...},
    "chat": {...},
    "date": 1234567890,
    "text": "Hello!"
  }
}
```

**Usage in code:**

```python
# bridge.py
result = telegram_api("sendMessage", {
    "chat_id": chat_id,
    "text": "Hello!"
})

# send-to-telegram.sh (embedded Python)
def send(txt, mode=None):
    data = {"chat_id": chat_id, "text": txt}
    if mode:
        data["parse_mode"] = mode
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{token}/sendMessage",
        json.dumps(data).encode(),
        {"Content-Type": "application/json"}
    )
    return json.loads(urllib.request.urlopen(req).read()).get("ok")
```

---

### setMyCommands

Register bot commands shown in inline help.

#### Request

**Method:** POST  
**Endpoint:** `/setMyCommands`

**Body:**
```json
{
  "commands": [
    {
      "command": string,
      "description": string
    }
  ]
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `command` | string | Yes | Command name (1-32 chars, lowercase, starts with `/`) |
| `description` | string | Yes | Command description (1-256 chars) |

#### Response

```json
{
  "ok": true
}
```

**Usage in code:**

```python
# bridge.py
BOT_COMMANDS = [
    {"command": "clear", "description": "Clear conversation"},
    {"command": "resume", "description": "Resume session"},
]

result = telegram_api("setMyCommands", {"commands": BOT_COMMANDS})
if result and result.get("ok"):
    print("Bot commands registered")
```

---

### sendChatAction

Send chat action (typing indicator, uploading file, etc.).

#### Request

**Method:** POST  
**Endpoint:** `/sendChatAction`

**Body:**
```json
{
  "chat_id": integer,
  "action": string
}
```

**Actions:**

| Action | Description |
|--------|-------------|
| `typing` | User is typing (disappears after 5s) |
| `upload_photo` | Uploading photo |
| `upload_video` | Uploading video |
| `upload_audio` | Uploading audio |
| `upload_document` | Uploading document |
| `choose_sticker` | Choosing sticker |
| `record_video` | Recording video |
| `record_audio` | Recording audio |

#### Response

```json
{
  "ok": true
}
```

**Usage in code:**

```python
# bridge.py - typing indicator loop
def send_typing_loop(chat_id):
    while os.path.exists(PENDING_FILE):
        telegram_api("sendChatAction", {
            "chat_id": chat_id,
            "action": "typing"
        })
        time.sleep(4)  # Send before 5s timeout
```

---

### answerCallbackQuery

Respond to inline keyboard callback.

#### Request

**Method:** POST  
**Endpoint:** `/answerCallbackQuery`

**Body:**
```json
{
  "callback_query_id": string,
  "text": string,  // optional, shows as popup
  "show_alert": boolean  // optional, alert vs popup
}
```

**Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `callback_query_id` | string | Yes | ID from callback_query |
| `text` | string | No | Text to show (0-64 chars) |
| `show_alert` | boolean | No | Alert dialog vs popup |

#### Response

```json
{
  "ok": true
}
```

**Usage in code:**

```python
# bridge.py - handle_callback()
def handle_callback(self, cb):
    telegram_api("answerCallbackQuery", {
        "callback_query_id": cb.get("id")
    })
    # ... process callback ...
```

---

### setMessageReaction

Set reaction on a message.

#### Request

**Method:** POST  
**Endpoint:** `/setMessageReaction`

**Body:**
```json
{
  "chat_id": integer,
  "message_id": integer,
  "reaction": [
    {
      "type": "emoji",
      "emoji": string
    }
  ],
  "is_big": boolean  // optional
}
```

**Reaction Types:**

| Type | Emoji | Description |
|------|-------|-------------|
| `👍` | `\ud83d\udc4d` | Thumbs up |
| `❤️` | `\u2764\ufe0f` | Heart |
| `🔥` | `\ud83d\udd25` | Fire |
| `✅` | `\u2705` | Check mark |

#### Response

```json
{
  "ok": true
}
```

**Usage in code:**

```python
# bridge.py - acknowledge user message
if msg_id:
    telegram_api("setMessageReaction", {
        "chat_id": chat_id,
        "message_id": msg_id,
        "reaction": [{"type": "emoji", "emoji": "\u2705"}]
    })
```

---

### Webhook Setup

Configure webhook URL for receiving updates.

#### Request

**Method:** GET (via curl)  
**Endpoint:** `/setWebhook`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `url` | string | Yes | Webhook URL (must be HTTPS) |

#### Command

```bash
curl "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/setWebhook?url=https://YOUR-URL.trycloudflare.com"
```

#### Response

```json
{
  "ok": true,
  "result": true,
  "description": "Webhook was set"
}
```

---

## Webhook Payload Structure

### Incoming Update

Telegram sends POST request with JSON body:

```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 42,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "User",
      "username": "user_handle"
    },
    "chat": {
      "id": 987654321,
      "first_name": "User",
      "type": "private"
    },
    "date": 1234567890,
    "text": "/status"
  }
}
```

### Callback Query (Inline Keyboard)

```json
{
  "update_id": 123456789,
  "callback_query": {
    "id": "callback_id",
    "from": {...},
    "message": {
      "message_id": 42,
      "chat": {
        "id": 987654321
      }
    },
    "data": "resume:session-id-123"
  }
}
```

---

## Rate Limits

### Telegram Bot API

| Limit | Value |
|-------|-------|
| Requests per second | ~30 |
| Messages per second (per chat) | ~1 |
| Message length | 4096 characters |
| Callback data | 64 bytes |

### Consequences of Exceeding

- HTTP 429 Too Many Requests
- Temporary flood wait (seconds to hours)

### Mitigation in Code

```python
# Add delay between requests
time.sleep(0.1)  # 100ms between API calls

# Retry with exponential backoff
for attempt in range(3):
    result = telegram_api("sendMessage", data)
    if result:
        break
    time.sleep(2 ** attempt)
```

---

## Error Responses

### HTTP Errors

| Code | Meaning |
|------|--------|
| 400 | Bad Request (invalid parameters) |
| 401 | Unauthorized (invalid token) |
| 403 | Forbidden (method not allowed) |
| 404 | Not Found (chat not found) |
| 409 | Conflict (webhook conflict) |
| 429 | Too Many Requests (rate limit) |

### JSON Error Response

```json
{
  "ok": false,
  "error_code": 429,
  "description": "Too Many Requests"
}
```

### Handling in Code

```python
def telegram_api(method, data):
    if not BOT_TOKEN:
        return None
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{BOT_TOKEN}/{method}",
        data=json.dumps(data).encode(),
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())
    except Exception as e:
        print(f"Telegram API error: {e}")
        return None
```

---

## HTML Parse Mode

When `parse_mode: "HTML"` is set, these tags are supported:

### Supported Tags

| Tag | Description | Attributes |
|-----|-------------|------------|
| `<b>` | Bold | - |
| `<i>` | Italic | - |
| `<u>` | Underline | - |
| `<s>` | Strikethrough | - |
| `<code>` | Inline code | - |
| `<pre>` | Preformatted block | - |
| `<a>` | Link | `href` |
| `<spoiler>` | Spoiler text | - |
| `<tg-spoiler>` | Spoiler (alias) | - |
| `<strong>` | Bold (alias) | - |
| `<em>` | Italic (alias) | - |
| `<ins>` | Underline (alias) | - |
| `<del>` | Strikethrough (alias) | - |

### Example

```python
text = """Hello <b>World</b>!

Here's some <code>inline code</code>.

<pre><code class="language-python">
def hello():
    print("Hello")
</code></pre>"""

result = telegram_api("sendMessage", {
    "chat_id": chat_id,
    "text": text,
    "parse_mode": "HTML"
})
```

---

## Best Practices

### 1. Always Check Response

```python
result = telegram_api("sendMessage", data)
if result and result.get("ok"):
    # Success
else:
    # Handle failure
```

### 2. Use Timeout

```python
with urllib.request.urlopen(req, timeout=10) as r:
    response = r.read()
```

### 3. Escape HTML Entities

```python
def esc(s):
    return (s.replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;'))
```

### 4. Truncate Long Messages

```python
if len(text) > 4000:
    text = text[:4000] + "..."
```

### 5. Handle Missing Token Gracefully

```python
if not BOT_TOKEN:
    return None  # Don't crash
```
