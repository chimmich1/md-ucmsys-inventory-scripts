"""Evaluate permanent-master completion and create a targeted refresh queue."""
import hashlib
import json
from pathlib import Path

from permanent_master_snapshot import validate_active

VALID = {"UNVERIFIED", "INCOMPLETE", "DISCOVERY_STALLED", "COMPLETE"}


def load(path):
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))


def completion(status, rule, **details):
    if status not in VALID:
        raise ValueError(f"invalid completion status: {status}")
    return {"status": status, "proof": {"rule": rule, **details} if status == "COMPLETE" else None,
            "details": {"reason": rule, **details} if status != "COMPLETE" else {}}


def _default_index(group):
    return {(x["cabinNumber"], x["field"]): x for x in group["classDefaults"]}


def _ship_index(group):
    result = {}
    for ship in group["shipFields"]:
        for cabin in ship["cabins"]:
            for field, value in cabin["fields"].items():
                result[(ship["shipCode"], cabin["cabinNumber"], field)] = value
    return result


def _has_value(provider, ship, cabin, field, defaults, exceptions):
    exception = exceptions.get((ship, cabin, field))
    if exception is not None:
        return "value" in exception
    default = defaults.get((cabin, field))
    if default is None:
        return False
    return any(source.split("/")[1] == ship for source in default.get("sourceIds", []))


def assess(snapshot_root, policy_path, manual_targets=(), factory_refresh_targets=()):
    snapshot_root, policy_path = Path(snapshot_root), Path(policy_path)
    manifest = validate_active(snapshot_root)
    if not manifest:
        raise ValueError("no active permanent-master snapshot")
    policy = load(policy_path)
    if policy.get("schemaVersion") != "1.0":
        raise ValueError("unsupported refresh policy")
    files = snapshot_root / "snapshots" / manifest["snapshotId"]
    queue, providers, known_ships = [], [], set()

    for provider in ("CELEBRITY", "PRINCESS"):
        physical = load(files / f"{provider.lower()}-physical.json")
        categories = load(files / f"{provider.lower()}-categories.json")
        assignments = load(files / f"{provider.lower()}-assignments.json")
        assignment_by_source = {}
        for revision in assignments["revisions"]:
            cabin_numbers = {a["cabinNumber"] for a in revision["assignments"]}
            for source in revision["sourceIds"]:
                assignment_by_source[source] = cabin_numbers

        group_results = []
        for group in physical["groups"]:
            defaults, exceptions = _default_index(group), _ship_index(group)
            required = policy["requiredPhysicalFields"][provider]
            conflict_keys = {(x["shipCode"], x["cabinNumber"], x["field"])
                             for x in group["conflicts"]}
            missing = {}
            confirmed_count = 0
            for membership in group["shipMembership"]:
                ship = membership["shipCode"]
                known_ships.add((provider, ship))
                confirmed_count += len(membership["cabinNumbers"])
                for field in required:
                    cabins = [c for c in membership["cabinNumbers"]
                              if (ship, c, field) not in conflict_keys and
                              not _has_value(provider, ship, c, field, defaults, exceptions)]
                    if cabins:
                        missing[(ship, field)] = cabins
                        queue.append({"provider": provider, "groupId": group["groupId"],
                            "shipCode": ship, "dimension": "attributes", "action": "DISCOVER_MISSING_FIELD",
                            "field": field, "cabinCount": len(cabins), "cabinExamples": cabins[:10],
                            "reason": "required field is unknown for confirmed membership"})
            for conflict in group["conflicts"]:
                queue.append({"provider": provider, "groupId": group["groupId"],
                    "shipCode": conflict["shipCode"], "dimension": "attributes",
                    "action": "RESOLVE_CONTRADICTORY_EVIDENCE", "field": conflict["field"],
                    "cabinCount": 1, "cabinExamples": [conflict["cabinNumber"]],
                    "reason": "multiple known values remain unresolved"})

            assignment_gaps = []
            for source in group["sourceMembership"]:
                missing_assignments = sorted(set(source["cabinNumbers"]) - assignment_by_source.get(source["sourceId"], set()))
                if missing_assignments:
                    assignment_gaps.append({"sourceId": source["sourceId"], "cabinCount": len(missing_assignments),
                                            "cabinExamples": missing_assignments[:10]})
                    queue.append({"provider": provider, "groupId": group["groupId"],
                        "shipCode": source["sourceId"].split("/")[1], "dimension": "assignments",
                        "action": "DISCOVER_MISSING_ASSIGNMENT", "sourceId": source["sourceId"],
                        "cabinCount": len(missing_assignments), "cabinExamples": missing_assignments[:10],
                        "reason": "confirmed cabin has no assignment in this source configuration"})

            conflict_count = len(group["conflicts"])
            attribute_status = "COMPLETE" if not missing and not conflict_count else "INCOMPLETE"
            assignment_status = "COMPLETE" if not assignment_gaps else "INCOMPLETE"
            stalled = {field: completion("DISCOVERY_STALLED", reason, retry="manual-or-policy-change")
                       for field, reason in policy["stalledPhysicalFields"][provider].items()}
            group_results.append({"groupId": group["groupId"], "scope": group["scope"],
                "membership": completion("UNVERIFIED", "observed membership lacks an independent completeness proof",
                                         confirmedCabins=confirmed_count),
                "attributes": completion(attribute_status, "all required fields have one selected value for confirmed membership",
                                         confirmedCabins=confirmed_count, missingFieldGroups=len(missing), conflicts=conflict_count),
                "attributeFields": stalled,
                "categoryDefinitions": completion("UNVERIFIED", "observed definitions lack an independent completeness proof",
                                                  observedDefinitions=sum(d["groupId"] == group["groupId"]
                                                                          for d in categories["definitions"])),
                "assignments": completion(assignment_status, "every confirmed source cabin has an observed assignment",
                                          sourceConfigurations=len(group["sourceMembership"]), gaps=assignment_gaps)})
        providers.append({"provider": provider, "groups": group_results})

    for action, targets in (("MANUAL_VERIFY_PHYSICAL", manual_targets),
                            ("VERIFY_FACTORY_REFRESH", factory_refresh_targets)):
        for target in targets:
            parts = target.upper().split("/", 1)
            if len(parts) != 2 or tuple(parts) not in known_ships:
                raise ValueError(f"unknown permanent-master target: {target}")
            provider, ship = parts
            queue.append({"provider": provider, "groupId": None, "shipCode": ship,
                          "dimension": "attributes", "action": action, "cabinCount": 0,
                          "cabinExamples": [], "reason": "explicit operator trigger"})

    queue.sort(key=lambda x: (x["provider"], x["groupId"] or "", x["shipCode"], x["dimension"],
                              x["action"], x.get("field", ""), x.get("sourceId", "")))
    policy_hash = hashlib.sha256(policy_path.read_bytes()).hexdigest()
    return {"schemaVersion": "1.0", "kind": "PERMANENT_MASTER_COMPLETION_ASSESSMENT",
            "snapshotId": manifest["snapshotId"], "policySha256": policy_hash,
            "providers": providers, "refreshQueue": queue,
            "queueSummary": {"workItems": len(queue),
                "byAction": {action: sum(x["action"] == action for x in queue)
                             for action in sorted({x["action"] for x in queue})}},
            "periodicVerificationDays": policy["periodicVerificationDays"],
            "periodicSchedule": {name: {"intervalDays": days, "status": "UNSCHEDULED",
                "reason": "migrated evidence has no supported verifiedAt date"}
                for name, days in policy["periodicVerificationDays"].items()},
            "automaticTriggers": policy["automaticTriggers"], "manualTriggers": policy["manualTriggers"]}
