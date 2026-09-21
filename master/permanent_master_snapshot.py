"""Build and transactionally publish permanent-master snapshots from local evidence."""
import hashlib
import importlib.util
import json
from pathlib import Path

from catalog_state import dump


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def sha(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def with_hash(document):
    result = dict(document)
    result["contentSha256"] = sha(document)
    return result


def verify_document(document):
    body = dict(document)
    expected = body.pop("contentSha256", None)
    if expected != sha(body):
        raise ValueError(f"permanent-master content hash mismatch: {document.get('kind')}")


def load_audit_module(repo_root):
    path = repo_root / "master/audit-permanent-masters.py"
    spec = importlib.util.spec_from_file_location("permanent_master_audit", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def build_documents(state, classes_path, repo_root):
    report = load_audit_module(repo_root).audit(state, classes_path)
    source_by_id = {s["sourceId"]: s for s in report["sources"]}
    documents = {}
    for provider in ("CELEBRITY", "PRINCESS"):
        groups = [g for g in report["groups"] if g["provider"] == provider]
        source_ids = sorted(sid for g in groups for m in g["sourceMembership"] for sid in [m["sourceId"]])
        def sources_for(evidence_key):
            return [{"sourceId": sid, "path": source_by_id[sid]["path"],
                     "sha256": source_by_id[sid][evidence_key], "hashScope": evidence_key,
                     "verifiedAt": None} for sid in sorted(set(source_ids))]
        coverage = {name: {"status": "UNVERIFIED", "evidence": None}
                    for name in ("membership", "attributes", "categoryDefinitions", "assignments")}

        physical_groups = []
        for group in groups:
            default_lookup = {(item["cabinNumber"], item["field"]): item["value"]
                              for item in group["proposedSharedFields"]}
            conflicts = []
            ship_fields = []
            for ship_record in group["shipFieldObservations"]:
                cabins = []
                for cabin in ship_record["cabins"]:
                    fields = {}
                    for item in cabin["fields"]:
                        known = [v for v in item["values"] if v["value"] is not None]
                        if not known:
                            continue
                        if len(known) == 1 and len(item["values"]) == 1:
                            if default_lookup.get((cabin["cabinNumber"], item["field"]), object()) == known[0]["value"]:
                                continue
                            fields[item["field"]] = {"value": known[0]["value"],
                                                      "sourceIds": known[0]["sourceIds"]}
                        else:
                            fields[item["field"]] = {"observations": item["values"]}
                        if len(known) > 1:
                            conflicts.append({"shipCode": ship_record["shipCode"],
                                "cabinNumber": cabin["cabinNumber"], "field": item["field"],
                                "values": known})
                    if fields:
                        cabins.append({"cabinNumber": cabin["cabinNumber"], "fields": fields})
                ship_fields.append({"shipCode": ship_record["shipCode"], "cabins": cabins})
            physical_groups.append({"groupId": group["groupId"], "scope": group["scope"],
                "classDefaults": group["proposedSharedFields"],
                "shipMembership": [{"shipCode": ship, "cabinNumbers": cabins,
                                    "configurationEvidence": [m["sourceId"] for m in group["sourceMembership"]
                                        if m["sourceId"].split("/")[1] == ship]}
                                   for ship, cabins in group["confirmedShipMembership"].items()],
                "sourceMembership": group["sourceMembership"], "shipFields": ship_fields,
                "conflicts": conflicts})
        physical = with_hash({"schemaVersion": "2.0", "kind": "PHYSICAL_CABIN_MASTER",
                              "provider": provider, "revisionId": "pending",
                              "sources": sources_for("physicalEvidenceSha256"),
                              "coverage": coverage, "groups": physical_groups})

        definitions = []
        for group in groups:
            for entry in group["categoryDefinitions"]:
                definitions.append({"groupId": group["groupId"], **entry})
        category = with_hash({"schemaVersion": "2.0", "kind": "CATEGORY_DEFINITION_MASTER",
                              "provider": provider, "revisionId": "pending",
                              "sources": sources_for("categoryEvidenceSha256"),
                              "coverage": coverage, "definitions": definitions})

        revisions = []
        for group in groups:
            for revision in group["assignmentRevisions"]:
                revisions.append({"groupId": group["groupId"], **revision})
        assignment = with_hash({"schemaVersion": "2.0", "kind": "CABIN_CATEGORY_ASSIGNMENT_MASTER",
                                "provider": provider, "revisionId": "pending",
                                "sources": sources_for("assignmentEvidenceSha256"),
                                "coverage": coverage, "revisions": revisions})
        for name, document in (("physical", physical), ("categories", category), ("assignments", assignment)):
            revision = document["contentSha256"][:16]
            body = dict(document); body.pop("contentSha256"); body["revisionId"] = revision
            documents[f"{provider.lower()}-{name}.json"] = with_hash(body)

    file_hashes = {name: hashlib.sha256(canonical(doc)).hexdigest() for name, doc in sorted(documents.items())}
    snapshot_id = sha(file_hashes)[:24]
    manifest = with_hash({"schemaVersion": "1.0", "kind": "PERMANENT_MASTER_SNAPSHOT",
                          "snapshotId": snapshot_id, "files": file_hashes,
                          "legacyCatalogsRemainAuthoritative": True})
    documents["manifest.json"] = manifest
    return snapshot_id, documents


def verify_snapshot(directory, documents=None):
    manifest = json.loads((directory / "manifest.json").read_text(encoding="utf-8-sig"))
    verify_document(manifest)
    required = {f"{provider}-{name}.json" for provider in ("celebrity", "princess")
                for name in ("physical", "categories", "assignments")}
    if set(manifest.get("files", {})) != required:
        raise ValueError("snapshot manifest does not contain the six required masters")
    for name, expected in manifest["files"].items():
        path = directory / name
        if path.resolve().parent != directory.resolve():
            raise ValueError(f"snapshot file path escapes snapshot: {name}")
        document = json.loads(path.read_text(encoding="utf-8-sig"))
        verify_document(document)
        provider, master_type = name.removesuffix(".json").split("-", 1)
        expected_kind = {"physical": "PHYSICAL_CABIN_MASTER",
                         "categories": "CATEGORY_DEFINITION_MASTER",
                         "assignments": "CABIN_CATEGORY_ASSIGNMENT_MASTER"}[master_type]
        if document.get("provider") != provider.upper() or document.get("kind") != expected_kind:
            raise ValueError(f"snapshot master identity mismatch: {name}")
        if hashlib.sha256(canonical(document)).hexdigest() != expected:
            raise ValueError(f"snapshot file hash mismatch: {name}")
        if documents is not None and canonical(document) != canonical(documents[name]):
            raise ValueError(f"existing snapshot differs: {name}")
    return manifest


def publish(output_root, snapshot_id, documents, before_activate=None):
    if documents["manifest.json"]["snapshotId"] != snapshot_id:
        raise ValueError("snapshot identity does not match manifest")
    output_root.mkdir(parents=True, exist_ok=True)
    snapshots = output_root / "snapshots"
    snapshots.mkdir(exist_ok=True)
    final = snapshots / snapshot_id
    staging = snapshots / f".staging-{snapshot_id}"
    if not final.exists():
        staging.mkdir(exist_ok=True)
        for name, document in sorted(documents.items()):
            dump(staging / name, document)
        verify_snapshot(staging, documents)
        staging.replace(final)
    else:
        verify_snapshot(final, documents)
    if before_activate:
        before_activate(final)
    activate(output_root, snapshot_id)
    return final


def activate(output_root, snapshot_id):
    final = output_root / "snapshots" / snapshot_id
    manifest = verify_snapshot(final)
    if manifest["snapshotId"] != snapshot_id:
        raise ValueError("snapshot directory/manifest identity mismatch")
    pointer = {"schemaVersion": "1.0", "snapshotId": snapshot_id,
               "manifestPath": f"snapshots/{snapshot_id}/manifest.json"}
    dump(output_root / "active-snapshot.json", pointer)


def validate_active(output_root):
    pointer_path = output_root / "active-snapshot.json"
    if not pointer_path.exists():
        return None
    pointer = json.loads(pointer_path.read_text(encoding="utf-8-sig"))
    manifest_path = output_root / Path(pointer["manifestPath"])
    if not manifest_path.resolve().is_relative_to(output_root.resolve()):
        raise ValueError("active permanent-master manifest escapes output root")
    expected = output_root / "snapshots" / str(pointer["snapshotId"]) / "manifest.json"
    if manifest_path.resolve() != expected.resolve():
        raise ValueError("active permanent-master manifest path/identity mismatch")
    manifest = verify_snapshot(manifest_path.parent)
    if manifest["snapshotId"] != pointer["snapshotId"]:
        raise ValueError("active permanent-master snapshot identity mismatch")
    return manifest
