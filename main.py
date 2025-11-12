import os
import json
import asyncio
from maigret.maigret import MaigretDatabase, maigret
from maigret.result import Result
from maigret.utils import save_json

# Chemins Apify
INPUT_PATH = os.getenv("APIFY_INPUT", "/apify_storage/key_value_stores/default/INPUT.json")
OUTPUT_PATH = "/apify_storage/key_value_stores/default/OUTPUT.json"

async def main():
    # Lire l'input Apify
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    usernames = data.get("usernames", [])
    site_subset = data.get("siteSubset")
    timeout = int(data.get("timeoutSec", 60))

    if not usernames:
        print("⚠️ Aucun username fourni dans l'input.")
        return

    # Charger la base des sites Maigret
    db = MaigretDatabase()
    await db.load_from_remote()

    # Lancer la recherche
    results = {}

    for username in usernames:
        print(f"🔎 Recherche Maigret pour: {username}")
        try:
            found = await maigret(
                username=username,
                db=db,
                site_subset=site_subset,
                timeout=timeout,
