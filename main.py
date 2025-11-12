import os
import json
import asyncio
from maigret import Maigret

# Chemins standards Apify
INPUT_PATH = os.getenv("APIFY_INPUT", "/apify_storage/key_value_stores/default/INPUT.json")
OUTPUT_PATH = "/apify_storage/key_value_stores/default/OUTPUT.json"

async def run_maigret():
    # Lire l'input Apify
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    usernames = data.get("usernames", [])
    site_subset = data.get("siteSubset")
    timeout = data.get("timeoutSec", 60)
    output_format = data.get("outputFormat", "json")

    if not usernames:
        raise ValueError("No usernames provided in input.")

    results = {}

    # Créer l'instance Maigret
    maigret = Maigret()

    for username in usernames:
        print(f"Scanning username: {username}")
        try:
            res = await maigret.search(username, site_subset=site_subset, timeout=timeout)
            results[username] = res
        except Exception as e:
            print(f"Error scanning {username}: {e}")
            results[username] = {"error": str(e)}

    # Sauvegarder les résultats
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    print("✅ Scan finished. Results saved to OUTPUT.json")

if __name__ == "__main__":
    asyncio.run(run_maigret())
