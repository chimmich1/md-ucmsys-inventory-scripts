"""Portable catalog metadata and recovery from published runtime artifacts."""
import hashlib
import json
import os
import tempfile
from pathlib import Path, PurePosixPath, PureWindowsPath


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dump(path, document):
    """Replace one JSON document atomically; never truncate its published copy."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         prefix=path.name + ".", suffix=".partial",
                                         delete=False) as stream:
            temporary = Path(stream.name)
            json.dump(document, stream, indent=2, ensure_ascii=False)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        temporary.replace(path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


def master_path(root, provider, ship, configuration, filename):
    for value in (ship, configuration):
        if value is None or str(value) in ("", ".", "..") or any(c in str(value) for c in "/\\:"):
            raise ValueError(f"invalid catalog identity: {ship!r}/{configuration!r}")
    return Path(root) / provider / str(ship) / str(configuration) / filename


def resolve_catalog_path(root, value, provider, ship, configuration, filename):
    """Resolve legacy absolute paths against this state, never the old host."""
    root = Path(root)
    normalized = str(value).replace("\\", "/")
    if PurePosixPath(normalized).is_absolute() or PureWindowsPath(value).is_absolute():
        return master_path(root, provider, ship, configuration, filename)
    path = root / normalized
    if not path.resolve().is_relative_to(root.resolve()):
        raise ValueError(f"catalog path escapes static-masters: {value}")
    return path


def celebrity_entry(root, item):
    ship, configuration = item["shipCode"], str(item["configurationId"])
    final = master_path(root, "celebrity", ship, configuration,
                        f"celebrity-ship-master-{ship}-v2.2.json")
    validation_path = final.with_name(f"celebrity-ship-master-validation-{ship}-v2.2.json")
    master, validation = load(final), load(validation_path)
    for document in (master, validation):
        if (document.get("provider") != "CELEBRITY" or document.get("shipCode") != ship
                or str(document.get("targetConfiguration")) != configuration):
            raise ValueError(f"Celebrity master/validation identity mismatch: {final}")
    if validation.get("cabinDeckConflictCount", 0) or validation.get("cabinDeckConflicts"):
        raise ValueError(f"cabin/deck conflict: {final}")
    saturation = (validation.get("saturation") or {}).get("saturated")
    if not isinstance(saturation, bool) or (master.get("saturation") or {}).get("saturated") != saturation:
        raise ValueError(f"Celebrity master/validation saturation mismatch: {final}")
    return {**item, "path": final.relative_to(root).as_posix(),
            "sha256": sha(final), "saturated": saturation}


def reconcile_celebrity(root, catalog):
    return {**catalog, "schemaVersion": "1.1", "provider": "CELEBRITY",
            "configurations": [celebrity_entry(root, item)
                               for item in catalog.get("configurations", [])]}


def relocate_princess(root, catalog):
    entries = []
    for item in catalog.get("configurations", []):
        final = master_path(root, "princess", item["shipCode"], item["configurationId"],
                            "published-deck-plan.json")
        if sha(final) != item["sha256"]:
            raise ValueError(f"Princess hash mismatch: {final}")
        entries.append({**item, "path": final.relative_to(root).as_posix()})
    return {**catalog, "configurations": entries}
