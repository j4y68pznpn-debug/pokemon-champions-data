import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

BASE = "https://championsbattledata.com"


def fetch_json(path):
    request = Request(
        BASE + path,
        headers={
            "User-Agent": "PokemonChampionsDataBot/1.0"
        },
    )

    for attempt in range(4):
        try:
            with urlopen(request, timeout=30) as response:
                return json.load(response)
        except Exception:
            if attempt == 3:
                raise
            time.sleep(2 ** attempt)


def main():
    ranking_data = fetch_json(
        "/api/rankings?format=Singles"
    )

    rankings = ranking_data["rankings"]
    results = {}
    failures = []

    print(f"Found {len(rankings)} Pokemon")

    for index, pokemon in enumerate(rankings, 1):
        name = pokemon["showdownId"]

        try:
            data = fetch_json(
                "/api/battle/Singles/"
                + quote(name, safe="")
            )

            if not isinstance(data, dict):
                raise ValueError("Invalid response")

            if not isinstance(data.get("rows"), list):
                raise ValueError("Missing rows")

            results[name] = data
            print(
                f"OK {index}/{len(rankings)}: {name}"
            )

        except Exception as error:
            failures.append(name)
            print(f"ERROR: {name}: {error}")

        time.sleep(0.3)

    if failures:
        raise RuntimeError(
            "Data retrieval failed: "
            + ", ".join(failures)
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
        json.dumps(
            output,
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )

    print(
        f"Saved {len(results)} Pokemon "
        "to data/latest.json"
    )


if __name__ == "__main__":
    main()
