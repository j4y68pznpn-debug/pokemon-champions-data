
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen

BASE = "https://championsbattledata.com"
POKEMON = [
    "garchomp",
    "primarina",
    "hippowdon",
    "archaludon",
    "mimikyu",
    "lucario",
    "raichu",
    "indeedee",
    "ceruledge",
    "arboliva",
]

def fetch_json(path):
    request = Request(
        BASE + path,
        headers={"User-Agent": "PokemonChampionsData/1.0"}
    )
    with urlopen(request, timeout=30) as response:
        return json.load(response)

def main():
    results = {}
    failures = []

    for name in POKEMON:
        try:
            data = fetch_json(
                f"/api/battle/Singles/{name}"
            )
            if not isinstance(data, dict):
                raise ValueError("Invalid response")
            if not isinstance(data.get("rows"), list):
                raise ValueError("Missing battle rows")
            results[name] = data
            print(f"OK: {name}")
        except Exception as error:
            failures.append(name)
            print(f"ERROR: {name}: {error}")

    if failures:
        raise RuntimeError(
            "Data retrieval failed: " + ", ".join(failures)
        )

    output = {
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "source": BASE,
        "format": "Singles",
        "pokemon": results,
    }

    Path("data").mkdir(exist_ok=True)
    Path("data/latest.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("Saved: data/latest.json")

if __name__ == "__main__":
    main()
