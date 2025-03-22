from telethon.sync import TelegramClient
from dotenv import load_dotenv
import os
import json

load_dotenv()

api_id = int(os.getenv("API_ID"))
api_hash = os.getenv("API_HASH")

client = TelegramClient("sessione_export", api_id, api_hash)

with client:
    dialogs = client.iter_dialogs()
    results = []
    for dialog in dialogs:
        entity = dialog.entity
        if hasattr(entity, 'access_hash') and entity.username is None:
            results.append({
                "title": entity.title,
                "id": entity.id if isinstance(entity.id, int) else int(entity.id.split("_")[-1]),
                "access_hash": entity.access_hash
            })

    output_path = os.path.join("data", "sources_secure.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print(f"💾 Salvato in: {output_path}")
