from __future__ import annotations
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
import hashlib, json

PROVENANCE = {
    "STRUCTURED": "PROVIDER_STRUCTURED",
    "RELATIONSHIP": "PROVIDER_RELATIONSHIP",
    "CATEGORY": "PROVIDER_CATEGORY_DERIVED",
    "TEXT": "PROVIDER_TEXT_DERIVED",
    "ASSET": "PROVIDER_ASSET_DERIVED",
    "SYSTEM": "SYSTEM_DERIVED",
    "UNKNOWN": "UNKNOWN",
}

def evidence(provenance: str, resolution: str, source: str | None,
             raw_value: Any = None, voyage_id: str | None = None,
             observed_at: str | None = None) -> dict:
    return {
        "provenance": provenance,
        "resolution": resolution,
        "source": source,
        "sourceVoyageId": voyage_id,
        "observedAt": observed_at,
        "rawValue": raw_value,
    }

def fact(value: Any, ev: list[dict] | None = None) -> dict:
    return {"value": value, "evidence": ev or []}

def number_fact(value: Any = None, ev: list[dict] | None = None,
                minimum: Any = None, maximum: Any = None) -> dict:
    return {"value": value, "min": minimum, "max": maximum, "evidence": ev or []}

def stable_hash(obj: Any) -> str:
    raw=json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def dump_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def first(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None, ""):
            return d[k]
    return default

def iter_dicts(obj: Any) -> Iterable[dict]:
    if isinstance(obj, dict):
        yield obj
        for v in obj.values():
            yield from iter_dicts(v)
    elif isinstance(obj, list):
        for v in obj:
            yield from iter_dicts(v)
