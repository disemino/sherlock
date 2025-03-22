import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from telethon import TelegramClient, events
from telethon.tl.types import PeerChannel
import json

# === Load environment variables ===
load_dotenv()
api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

# === Placeholder for your private group/chat ID ===
chat_id_gruppo = YOUR_GROUP_ID_HERE  # Replace with your Telegram group or chat ID

# === File paths ===
keywords_file = 'data/keywords.txt'
sources_txt = 'data/sources.txt'
sources_json = 'data/sources_secure.json'
seen_file = 'data/seen_messages.txt'

client = TelegramClient("sessione_monitor", api_id, api_hash)

# === Load keywords from file ===
def load_keywords():
    with open(keywords_file, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

# === Load and save seen message IDs ===
def load_seen():
    if not os.path.exists(seen_file):
        return set()
    with open(seen_file, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def save_seen(seen):
    with open(seen_file, 'w', encoding='utf-8') as f:
        for mid in seen:
            f.write(mid + '\n')

# === Load sources ===
def load_sources_txt():
    with open(sources_txt, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def load_sources_secure():
    if not os.path.exists(sources_json):
        return {}
    with open(sources_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {str(item['id']): item['access_hash'] for item in data}

# === Generate keyword-centered snippet ===
def get_snippet(text, keyword, width=400):
    index = text.lower().find(keyword)
    if index == -1:
        return text[:width] + ('...' if len(text) > width else '')
    start = max(index - width // 2, 0)
    end = min(start + width, len(text))
    snippet = text[start:end]
    if start > 0:
        snippet = '...' + snippet
    if end < len(text):
        snippet += '...'
    return snippet

# === Main scan function ===
async def execute_scan(client, full_scan=False, override_keywords=None):
    keywords = override_keywords or load_keywords()
    seen_messages = load_seen()
    sources_raw = load_sources_txt()
    sources_secure = load_sources_secure()

    matches_found = 0
    scan_errors = []

    for source in sources_raw:
        try:
            entity = None
            if source.startswith('@'):
                entity = await client.get_entity(source)
            elif source.startswith('-100'):
                channel_id = int(source)
                access_hash = sources_secure.get(str(channel_id))
                if access_hash:
                    entity = PeerChannel(channel_id)
                else:
                    entity = await client.get_entity(channel_id)
            else:
                continue

            offset_date = datetime(2022, 2, 24) if full_scan else (datetime.now() - timedelta(days=7))

            async for message in client.iter_messages(entity, limit=200 if not full_scan else None, offset_date=offset_date):
                if not message.text:
                    continue
                if str(message.id) in seen_messages:
                    continue

                text = message.text.lower()
                matched_kw = next((kw for kw in keywords if kw in text), None)
                if matched_kw:
                    try:
                        await client.forward_messages(chat_id_gruppo, message)
                    except:
                        snippet = get_snippet(message.text, matched_kw)
                        await client.send_message(chat_id_gruppo, f"🔍 Match in {source}:

{snippet}")
                    matches_found += 1
                seen_messages.add(str(message.id))

        except Exception as e:
            scan_errors.append(f"⚠️ {source}: {e}")

    save_seen(seen_messages)

    report = f"✅ Scan completed. Matches found: {matches_found}."
    if scan_errors:
        report += "\n\n⚠️ Errors during scan:\n" + "\n".join(scan_errors)
    await client.send_message(chat_id_gruppo, report)

# === Telegram bot commands ===
@client.on(events.NewMessage(pattern='/scan'))
async def command_scan(event):
    parts = event.message.message.strip().split(maxsplit=1)
    keyword = parts[1].strip().lower() if len(parts) > 1 else None
    await execute_scan(client, full_scan=False, override_keywords=[keyword] if keyword else None)

@client.on(events.NewMessage(pattern='/fullscan'))
async def command_fullscan(event):
    parts = event.message.message.strip().split(maxsplit=1)
    keyword = parts[1].strip().lower() if len(parts) > 1 else None
    await execute_scan(client, full_scan=True, override_keywords=[keyword] if keyword else None)

@client.on(events.NewMessage(pattern='/reset'))
async def command_reset(event):
    if os.path.exists(seen_file):
        os.remove(seen_file)
    await client.send_message(chat_id_gruppo, "🧹 Seen messages cache has been reset.")

@client.on(events.NewMessage(pattern='/status'))
async def command_status(event):
    keywords = load_keywords()
    sources = load_sources_txt()
    await client.send_message(chat_id_gruppo, f"📊 Sherlock is running. Keywords: {len(keywords)}, Sources: {len(sources)}")

@client.on(events.NewMessage(pattern='/addsource'))
async def command_addsource(event):
    parts = event.message.message.strip().split()
    if len(parts) < 2:
        return await client.send_message(chat_id_gruppo, "❌ Usage: /addsource @channel")
    new_source = parts[1].strip()
    with open(sources_txt, 'a', encoding='utf-8') as f:
        f.write(new_source + '\n')
    await client.send_message(chat_id_gruppo, f"✅ Source added: {new_source}")

# === Start the bot ===
with client:
    print("🤖 Sherlock is now running.")
    client.run_until_disconnected()
