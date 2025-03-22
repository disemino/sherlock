# Sherlock Telegram Monitor Bot

Sherlock is a Telegram-based bot to monitor public and private channels/groups for keywords – ideal for humanitarian use cases such as tracking missing persons in conflict zones.

---

## 🔧 Features

- Monitor any Telegram channel or group (even private)
- Works with @usernames or -100... channel IDs
- Supports protected channels via `sources_secure.json`
- Detects and highlights keywords (static or via `/scan <word>`)
- Duplicate message detection
- Dynamic commands from a private group
- Fully async and systemd-compatible

---

## 📁 Structure

```
sherlock/
├── bot/
│   └── scan_bot_secure.py        # Main bot logic (insert your version)
├── data/
│   ├── keywords.txt              # One keyword per line (UTF-8, lowercase)
│   ├── sources.txt               # List of sources: @channel or -100...
│   ├── sources_secure.json       # Private channels with access_hash
│   └── seen_messages.txt         # Auto-managed
├── scripts/
│   ├── export_sources.py         # Export private channel info
│   ├── start.sh / stop.sh        # Manual bot control
├── systemd/
│   └── sherlock.service          # Autostart with system
├── .env.example                  # Put your API credentials here
├── requirements.txt              # Python dependencies
└── README.md
```

---

## 🚀 Setup on VPS (Debian-based)

```bash
apt update && apt install -y python3 python3-venv git
git clone https://github.com/yourusername/sherlock.git
cd sherlock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # insert API_ID and API_HASH
```
---

## 🖥️ Install on Local Computer (macOS / Linux / Windows)

You can install and run Sherlock on your personal computer for testing or full use.

### 📦 Step-by-step installation

```bash
# Clone the repository
git clone https://github.com/disemino/sherlock.git
cd sherlock

# Create a virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create your environment file
cp .env.example .env
nano .env  # Fill in your own API_ID and API_HASH

---

## 🔐 Private Channel Setup

1. Join private channels with the same account
2. Run: `python3 scripts/export_sources.py`
3. Copy desired entries into `data/sources_secure.json`
4. Add corresponding `-100<id>` in `sources.txt`

---

## 💬 Commands

From your private Telegram group:

- `/scan` → scan last 200 messages with keywords
- `/fullscan` → scan entire history since 24 Feb 2022
- `/scan jackson` → scan last 200 for just "jackson"
- `/fullscan johnson` → full history for just "johnson"
- `/addsource @channel` → append new source
- `/status`, `/reset` → status & message cleanup

---

## 🛡️ Important Notes

- `keywords.txt` must be lowercase
- Messages already scanned are skipped
- Protected messages will fallback to text snippet if forward fails
- `.env` and `.session` must NOT be pushed to GitHub

---

> 🔐 You must provide your own API credentials.  
> 📄 Do **not** publish `.env` or `.session` files.
