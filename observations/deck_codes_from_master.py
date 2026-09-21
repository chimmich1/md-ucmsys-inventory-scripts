"""Extract provider deck codes from a published physical master for JSON jobs."""
from __future__ import annotations
import argparse, json
from pathlib import Path
from typing import Any

def deck_codes(document: Any) -> list[str]:
    found: set[str] = set()
    def walk(value: Any) -> None:
        if isinstance(value, dict):
            if value.get("field") == "deckNumber" and value.get("value") is not None:
                found.add(str(value["value"]).zfill(2))
            fields = value.get("fields")
            if isinstance(fields, dict) and "deckNumber" in fields:
                v = fields["deckNumber"]
                if isinstance(v, dict): v = v.get("value")
                if v is not None: found.add(str(v).zfill(2))
            for item in value.values(): walk(item)
        elif isinstance(value, list):
            for item in value: walk(item)
    walk(document)
    return sorted(found, key=lambda x: int(x))

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("master", type=Path)
    args = parser.parse_args()
    document = json.loads(args.master.read_text(encoding="utf-8-sig"))
    print(json.dumps(deck_codes(document)))
if __name__ == "__main__": main()
