# Sherlock Telegram Monitor Bot

**Sherlock** is a Telegram-based scanner bot designed to help monitor public and private channels and groups for keywords, primarily used to track missing persons during conflict zones.

---

## 🛠️ Features

- Monitor Telegram channels/groups using `@username`, `-100...` ID, or `access_hash`
- Works with protected/private channels via access_hash
- Highlight matched keywords in extracted message text
- Ignore duplicates automatically
- Accepts `/scan` and `/fullscan` commands from a private group
- Supports one-time keyword search like `/scan ivanov`
- Commands `/status`, `/reset`, `/addsource`

---

## 📦 Files

- `bot/scan_bot_secure.py`: main bot script
- `data/keywords.txt`: (empty) list of keywords to monitor (one per line)
- `data/sources.txt`: (empty) list of sources: @channel or -100id
- `data/sources_secure.json`: (empty) list of secure sources (private channels with access_hash)
- `scripts/export_sources.py`: export joined private channels with access_hash
- `scripts/start.sh`: run the bot in background with `nohup`
- `.env.example`: copy to `.env` and insert your API credentials
- `requirements.txt`: install with `pip install -r requirements.txt`

---

## 🚀 Setup

```bash
git clone <this-repo>
cd sherlock
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # fill your credentials
```

Then edit `data/keywords.txt` and `data/sources.txt`.

---

## 🔐 Private Channels

1. Join the private channel manually from the same Telegram account
2. Run `scripts/export_sources.py`
3. Copy only the relevant blocks into `data/sources_secure.json`
4. In `sources.txt`, add `-100<id>` of that channel
   - e.g. `-1001251934223`

Sherlock will match this `id` to the secure list and use `access_hash` internally.

---

## 🧪 Usage

From your private Telegram group, send commands:

- `/scan` — scan last 200 messages from all sources
- `/fullscan` — full historical scan since 24 Feb 2022
- `/scan petrova` — scan last 200 for "petrova" only
- `/fullscan ivanov` — full scan for "ivanov" only
- `/addsource @newchannel` — adds to `sources.txt`
- `/status` — shows stats
- `/reset` — resets message history

---

## 📬 Output

Matched messages will be:

- Forwarded to your private group (if possible)
- OR summarized with extracted text and keyword highlight

---

## ℹ️ Notes

- Keywords are **case-insensitive**
- `sources.txt` accepts `@username` or `-100...` format
- `sources_secure.json` is optional, but needed for private/username-less channels
- Forwarding from protected content will fail; fallback text will be sent

---

Sherlock is meant for humanitarian, non-commercial use only.
