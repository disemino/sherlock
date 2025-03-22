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

# === Placeholder for your private Telegram group ID ===
chat_id_gruppo = YOUR_GROUP_ID_HERE  # Inserisci l'ID del tuo gruppo privato Telegram

# === File paths ===
keywords_file = 'data/keywords.txt'
sources_txt = 'data/sources.txt'
sources_json = 'data/sources_secure.json'
seen_file = 'data/seen_messages.txt'

client = TelegramClient("sessione_monitor", api_id, api_hash)

# === Load keywords from file ===
def carica_keywords():
    with open(keywords_file, 'r', encoding='utf-8') as f:
        return [line.strip().lower() for line in f if line.strip()]

# === Load/save seen messages ===
def carica_seen():
    if not os.path.exists(seen_file):
        return set()
    with open(seen_file, 'r', encoding='utf-8') as f:
        return set(line.strip() for line in f)

def salva_seen(seen):
    with open(seen_file, 'w', encoding='utf-8') as f:
        for mid in seen:
            f.write(mid + '\n')

# === Load monitored sources ===
def carica_sources_txt():
    with open(sources_txt, 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip()]

def carica_sources_secure():
    if not os.path.exists(sources_json):
        return {}
    with open(sources_json, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return {str(item['id']): item['access_hash'] for item in data}

# === Scan messages for keywords ===
async def esegui_scan(client, full_scan=False, override_keywords=None):
    keywords = override_keywords or carica_keywords()
    seen_messages = carica_seen()
    sources_raw = carica_sources_txt()
    sources_secure = carica_sources_secure()

    messaggi_trovati = 0
    errore_scan = []

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

            if full_scan:
                offset_date = datetime(2022, 2, 24)
            else:
                offset_date = datetime.now() - timedelta(days=7)

            async for message in client.iter_messages(entity, limit=200 if not full_scan else None, offset_date=offset_date):
                if not message.text:
                    continue
                if str(message.id) in seen_messages:
                    continue

                testo = message.text.lower()
                if any(kw in testo for kw in keywords):
                    try:
                        await client.forward_messages(chat_id_gruppo, message)
                    except:
                        snippet = message.text[:1000] + ('...' if len(message.text) > 1000 else '')
                        await client.send_message(chat_id_gruppo, f"🔍 Match in {source}:

{snippet}")
                    messaggi_trovati += 1
                seen_messages.add(str(message.id))

        except Exception as e:
            errore_scan.append(f"⚠️ {source}: {e}")

    salva_seen(seen_messages)

    report = f"✅ Scan completato. Trovati: {messaggi_trovati} messaggi."
    if errore_scan:
        report += "\n\n⚠️ Errori durante la scansione:\n" + "\n".join(errore_scan)
    await client.send_message(chat_id_gruppo, report)

# === Telegram bot commands ===
@client.on(events.NewMessage(pattern='/scan'))
async def comando_scan(event):
    parts = event.message.message.strip().split(maxsplit=1)
    keyword = parts[1].strip().lower() if len(parts) > 1 else None
    await esegui_scan(client, full_scan=False, override_keywords=[keyword] if keyword else None)

@client.on(events.NewMessage(pattern='/fullscan'))
async def comando_fullscan(event):
    parts = event.message.message.strip().split(maxsplit=1)
    keyword = parts[1].strip().lower() if len(parts) > 1 else None
    await esegui_scan(client, full_scan=True, override_keywords=[keyword] if keyword else None)

@client.on(events.NewMessage(pattern='/reset'))
async def comando_reset(event):
    if os.path.exists(seen_file):
        os.remove(seen_file)
    await client.send_message(chat_id_gruppo, "🧹 Cache dei messaggi visti resettata.")

@client.on(events.NewMessage(pattern='/status'))
async def comando_status(event):
    keywords = carica_keywords()
    sources = carica_sources_txt()
    await client.send_message(chat_id_gruppo, f"📊 Sherlock attivo. Parole chiave: {len(keywords)}, Fonti: {len(sources)}")

@client.on(events.NewMessage(pattern='/addsource'))
async def comando_addsource(event):
    parts = event.message.message.strip().split()
    if len(parts) < 2:
        return await client.send_message(chat_id_gruppo, "❌ Usa il comando così: /addsource @canale")
    nuovo = parts[1].strip()
    with open(sources_txt, 'a', encoding='utf-8') as f:
        f.write(nuovo + '\n')
    await client.send_message(chat_id_gruppo, f"✅ Sorgente aggiunta: {nuovo}")

# === Start the bot ===
with client:
    print("🤖 Sherlock è attivo.")
    client.run_until_disconnected()
