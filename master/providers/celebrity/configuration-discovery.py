import argparse
import hashlib
import json
import re
import time
from collections import defaultdict
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from curl_cffi import requests


BASE = "https://www.celebritycruises.com"
ROOMS_API = BASE + "/room-selection/api/v1/rooms"


def load_json(path):
    with open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def dump_json(path, obj):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_text(
        json.dumps(obj, indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def safe_name(value):
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", str(value or "UNKNOWN"))


def normalize_location(code):
    s = (code or "").strip().upper()
    return {
        "FW": "FORWARD",
        "FWD": "FORWARD",
        "FORWARD": "FORWARD",
        "MS": "MIDSHIP",
        "MID": "MIDSHIP",
        "MIDSHIP": "MIDSHIP",
        "AF": "AFT",
        "AFT": "AFT",
    }.get(s, s or None)


def normalize_deck_number(value):
    if value is None:
        return None
    try:
        return int(str(value).strip())
    except Exception:
        return None


def get_json(session, url, params=None, attempts=4):
    last = None
    for attempt in range(1, attempts + 1):
        try:
            r = session.get(
                url,
                params=params,
                headers={
                    "accept": "application/json, text/plain, */*",
                    "referer": BASE + "/",
                    "origin": BASE,
                },
                timeout=45,
            )
            if r.status_code == 200:
                return r.json(), r.url
            last = RuntimeError(f"HTTP {r.status_code}: {r.text[:600]}")
        except Exception as exc:
            last = exc
        if attempt < attempts:
            time.sleep(1.5 * attempt)
    raise last


def source_obj(v):
    src = v.get("source")
    return src if isinstance(src, dict) else {}


def itinerary_code(v):
    src = source_obj(v)
    itin = v.get("itinerary")
    itin_code = itin.get("code") if isinstance(itin, dict) else None
    return (
        v.get("itineraryCode")
        or v.get("packageCode")
        or src.get("providerItineraryCode")
        or src.get("masterItineraryCode")
        or itin_code
    )


def ship_code(v):
    ship = v.get("ship")
    ship = ship if isinstance(ship, dict) else {}
    return v.get("shipCode") or ship.get("providerId") or ship.get("code")


def sail_date(v):
    return v.get("sailDate") or v.get("startDate") or v.get("departureDate")


def voyage_id(v):
    return v.get("voyageId") or v.get("id")


def booking_link(v):
    src = source_obj(v)
    return v.get("bookingLink") or src.get("bookingLink")


def flatten_voyages(data):
    found = []

    def walk(x):
        if isinstance(x, dict):
            has_date = x.get("sailDate") or x.get("startDate") or x.get("departureDate")
            src = x.get("source") if isinstance(x.get("source"), dict) else {}
            ship = x.get("ship") if isinstance(x.get("ship"), dict) else {}
            has_identity = (
                x.get("voyageId") or x.get("id")
                or x.get("shipCode") or ship.get("providerId")
                or x.get("bookingLink") or src.get("bookingLink")
            )
            if has_date and has_identity:
                found.append(x)
            for value in x.values():
                walk(value)
        elif isinstance(x, list):
            for value in x:
                walk(value)

    walk(data)

    dedup = {}
    for v in found:
        key = (voyage_id(v), sail_date(v), ship_code(v), itinerary_code(v))
        dedup[key] = v
    return list(dedup.values())


def select_candidates(voyages, ship, max_candidates):
    rows = [v for v in voyages if ship_code(v) == ship and sail_date(v)]
    rows.sort(key=lambda v: sail_date(v))

    by_itinerary = defaultdict(list)
    for v in rows:
        by_itinerary[itinerary_code(v) or "UNKNOWN"].append(v)

    selected = []
    latest_per_itin = sorted(
        [values[-1] for values in by_itinerary.values() if values],
        key=lambda v: sail_date(v),
        reverse=True
    )
    for v in latest_per_itin:
        selected.append(v)
        if len(selected) >= max_candidates:
            return selected

    seen = {(voyage_id(v), sail_date(v), itinerary_code(v)) for v in selected}
    for v in reversed(rows):
        key = (voyage_id(v), sail_date(v), itinerary_code(v))
        if key in seen:
            continue
        selected.append(v)
        seen.add(key)
        if len(selected) >= max_candidates:
            break
    return selected


def voyage_context(v, country, currency, adults, children):
    src = source_obj(v)
    link = booking_link(v) or ""
    qs = parse_qs(urlparse(link).query)

    package_code = (
        src.get("providerItineraryCode")
        or src.get("masterItineraryCode")
        or itinerary_code(v)
        or (qs.get("pID") or [None])[0]
    )
    group_id = src.get("providerGroupId") or (qs.get("groupId") or [None])[0]
    sc = ship_code(v) or (qs.get("sCD") or [None])[0]
    sd = sail_date(v) or (qs.get("sDT") or [None])[0]

    if not package_code or not group_id or not sc or not sd:
        raise RuntimeError(
            f"Incomplete voyage context for {voyage_id(v)}: "
            f"package={package_code!r}, group={group_id!r}, ship={sc!r}, sailDate={sd!r}"
        )

    return {
        "voyageId": voyage_id(v),
        "packageCode": package_code,
        "groupId": group_id,
        "shipCode": sc,
        "sailDate": sd,
        "country": country,
        "currency": currency,
        "adults": adults,
        "children": children,
        "itineraryCode": itinerary_code(v),
    }


def hierarchy_from_rooms_json(data):
    rooms = data.get("rooms") or []
    root = rooms[0] if rooms else {}
    options = root.get("options") if isinstance(root, dict) else {}
    stateroom_types = (options or {}).get("stateroomTypes") or []

    hierarchy = []
    for t in stateroom_types:
        type_code = t.get("code") or t.get("typeCode") or t.get("name")
        type_name = t.get("name") or t.get("displayName") or type_code
        for sub in t.get("stateroomSubtypes") or []:
            sub_code = sub.get("code") or sub.get("subtypeCode")
            sub_name = sub.get("name") or sub.get("displayName")
            lead = sub.get("categoryCode") or sub.get("category")
            cats = []
            if lead:
                cats.append(str(lead))
            for prop in ("categories", "stateroomCategories", "categoryOptions"):
                values = sub.get(prop)
                if not isinstance(values, list):
                    continue
                for cat in values:
                    if isinstance(cat, dict):
                        cc = cat.get("code") or cat.get("categoryCode") or cat.get("id")
                    else:
                        cc = cat
                    if cc and str(cc) not in cats:
                        cats.append(str(cc))
            hierarchy.append({
                "typeCode": type_code,
                "typeName": type_name,
                "subtypeCode": sub_code,
                "subtypeName": sub_name,
                "leadCategoryCode": str(lead) if lead else None,
                "candidateCategories": cats,
                "roomsLeft": sub.get("roomsLeft"),
                "pricing": sub.get("pricing"),
            })
    return hierarchy


def advertised_decks_from_room_numbers(rn):
    if not isinstance(rn, dict):
        return []
    out = []
    for d in rn.get("decks") or []:
        code = str(d.get("code") or d.get("number") or "").zfill(2)
        if not code.strip("0"):
            continue
        out.append({
            "code": code,
            "number": normalize_deck_number(d.get("number") or d.get("code")),
            "name": d.get("name"),
            "deckPlanUrl": d.get("deckPlanUrl"),
            "selected": d.get("selected") is True,
        })
    dedup = {}
    for d in out:
        dedup[d["code"]] = d
    return list(dedup.values())


def returned_selector(data):
    rooms = data.get("rooms") or []
    result = rooms[0] if rooms else {}
    room = result.get("room") if isinstance(result, dict) else {}
    room = room if isinstance(room, dict) else {}
    type_obj = room.get("stateroomType") or {}
    subtype_obj = room.get("stateroomSubtype") or {}
    return type_obj.get("code"), subtype_obj.get("code")


BOOTSTRAP_SELECTORS = [
    ("INTERIOR", "IS"), ("INTERIOR", "IN"),
    ("BALCONY", "VR"), ("BALCONY", "SV"),
    ("OUTSIDE", "OP"), ("CONCIERGE", "CC"),
    ("AQUA", "AQ"), ("DELUXE", "SS"),
]

PROBE_DECKS = [
    "02", "03", "05", "06", "07", "08", "09", "10", "11", "12",
    "14", "15", "16", "PL", "CN", "PH", "PN", "SK", "SR", "VS",
]


def discover_json_hierarchy(session, ctx):
    """Discover the full type/subtype hierarchy from rooms[].options."""
    attempts = []
    for class_code, subtype_code in BOOTSTRAP_SELECTORS:
        for deck_code in PROBE_DECKS:
            filt, data, final_url, rn = fetch_rooms_api(
                session, ctx, class_code, subtype_code, deck_code
            )
            attempts.append({
                "selector": {"typeCode": class_code, "subtypeCode": subtype_code},
                "requestedDeckCode": deck_code,
                "responseUrl": final_url,
            })
            hierarchy = hierarchy_from_rooms_json(data)
            if hierarchy:
                return hierarchy, filt, data, attempts
    raise RuntimeError("JSON rooms API did not expose options.stateroomTypes.")


def discover_subtype_decks(session, ctx, class_code, subtype_code):
    """Use only the JSON rooms API to obtain a subtype's advertised decks."""
    attempts = []
    for deck_code in PROBE_DECKS:
        filt, data, final_url, rn = fetch_rooms_api(
            session, ctx, class_code, subtype_code, deck_code
        )
        attempts.append({
            "requestedDeckCode": deck_code,
            "filter": filt,
            "response": data,
            "responseUrl": final_url,
        })
        returned_type, returned_subtype = returned_selector(data)
        if returned_type != class_code or returned_subtype != subtype_code:
            continue
        decks = advertised_decks_from_room_numbers(rn)
        if decks:
            return decks, attempts
    return [], attempts


def build_rooms_filter(ctx, class_code, subtype_code, deck_code):
    return {
        "countryCode": ctx["country"],
        "packageId": ctx["packageCode"],
        "sailDate": ctx["sailDate"],
        "currencyCode": ctx["currency"],
        "language": "en",
        "options": True,
        "roomNumbers": True,
        "rooms": [{
            "adultCount": ctx["adults"],
            "childCount": ctx["children"],
            "stateroomTypeCode": class_code,
            "stateroomSubtypeCode": subtype_code,
            "accessible": False,
            "selectionFallbackStrategy": "RECOMMENDATION",
            "editMode": True,
            "reset": False,
            "taxesAndFeesBundled": True,
            "room": {"deckCode": str(deck_code).zfill(2)},
        }],
        "platform": "web",
    }


def fetch_rooms_api(session, ctx, class_code, subtype_code, deck_code):
    filt = build_rooms_filter(ctx, class_code, subtype_code, deck_code)
    data, final_url = get_json(
        session,
        ROOMS_API,
        params={"filter": json.dumps(filt, separators=(",", ":"))},
    )

    room_numbers = None
    rooms = data.get("rooms") or []
    if rooms:
        result = rooms[0]
        room = result.get("room") or {}
        room_numbers = room.get("roomNumbers") or result.get("roomNumbers")

    if room_numbers is None:
        stack = [data]
        while stack:
            x = stack.pop()
            if isinstance(x, dict):
                if isinstance(x.get("roomNumbers"), dict):
                    room_numbers = x["roomNumbers"]
                    break
                stack.extend(x.values())
            elif isinstance(x, list):
                stack.extend(x)

    return filt, data, final_url, room_numbers


def selected_deck(room_numbers):
    if not isinstance(room_numbers, dict):
        return None
    matches = [d for d in room_numbers.get("decks") or [] if d.get("selected") is True]
    return matches[0] if len(matches) == 1 else None


def assignments_from_room_numbers(ctx, class_code, subtype_code, room_numbers, response_url):
    d = selected_deck(room_numbers)
    if d is None:
        raise RuntimeError("Provider response did not contain exactly one selected deck.")

    deck_code = str(d.get("code") or d.get("number") or "").zfill(2)
    deck = {
        "code": deck_code,
        "number": normalize_deck_number(d.get("number") or d.get("code")),
        "name": d.get("name"),
        "deckPlanUrl": d.get("deckPlanUrl"),
    }

    out = []
    for category in room_numbers.get("categories") or []:
        cat_code = category.get("categoryCode")
        for c in category.get("cabins") or []:
            n = c.get("cabinNumber")
            if n is None:
                continue
            pos = c.get("positionCode")
            out.append({
                "classCode": class_code,
                "subtypeCode": subtype_code,
                "categoryCode": cat_code,
                "cabinNumber": str(n),
                "deck": deck,
                "providerPositionCode": pos,
                "location": normalize_location(pos),
                "sources": {
                    "deck": "roomNumbers.decks[selected=true]",
                    "cabin": "roomNumbers.categories[].cabins[]",
                    "positionCode": "roomNumbers.categories[].cabins[].positionCode",
                    "responseUrl": response_url,
                    "sourceVoyageId": ctx["voyageId"],
                },
            })
    return out



def layout_version_from_url(url):
    if not url:
        return None
    m = re.search(r"/svg_c_[A-Za-z0-9]+_([0-9]+)/", str(url))
    return m.group(1) if m else None


def assignment_layout(a):
    explicit = a.get("configurationId") or a.get("layoutVersion")
    if explicit:
        return str(explicit)
    deck = a.get("deck") or {}
    return layout_version_from_url(deck.get("deckPlanUrl")) or "UNKNOWN"


def assignment_key(a):
    return (
        assignment_layout(a),
        a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"),
        a.get("cabinNumber"), (a.get("deck") or {}).get("code")
    )


def hierarchy_key(h):
    return (h.get("typeCode"), h.get("subtypeCode"), h.get("leadCategoryCode"))


def category_master_from_hierarchy(hierarchy, ship_code, configuration_id=None):
    out = []
    for h in hierarchy:
        out.append({
            "provider": "CELEBRITY",
            "shipCode": ship_code,
            "configurationId": configuration_id,
            "classCode": h.get("typeCode"),
            "className": h.get("typeName"),
            "subtypeCode": h.get("subtypeCode"),
            "subtypeName": h.get("subtypeName"),
            "leadCategoryCode": h.get("leadCategoryCode"),
            "candidateCategories": h.get("candidateCategories") or [],
        })
    return out


def with_configuration(a):
    a = dict(a)
    config = assignment_layout(a)
    a["configurationId"] = config
    a["layoutVersion"] = config
    return a


def build_physical(ship_code, assignments):
    # Physical cabin identity is configuration-scoped.
    physical = {}
    conflicts = []

    for raw in assignments:
        a = with_configuration(raw)
        config = a["configurationId"]
        n = a["cabinNumber"]
        deck = a["deck"]
        key = (config, n)
        x = physical.get(key)
        if x is None:
            x = {
                "provider": "CELEBRITY",
                "shipCode": ship_code,
                "configurationId": config,
                "layoutVersion": config,
                "cabinNumber": n,
                "deck": deck,
                "providerPositionCodes": set(),
                "locations": set(),
                "sourceVoyageIds": set(),
            }
            physical[key] = x
        elif x["deck"]["code"] != deck["code"]:
            conflicts.append({
                "configurationId": config,
                "cabinNumber": n,
                "deckA": x["deck"],
                "deckB": deck,
                "sourceVoyageId": (a.get("sources") or {}).get("sourceVoyageId"),
            })

        if a.get("providerPositionCode"):
            x["providerPositionCodes"].add(a["providerPositionCode"])
        if a.get("location"):
            x["locations"].add(a["location"])
        source_voyage = (a.get("sources") or {}).get("sourceVoyageId")
        if source_voyage:
            x["sourceVoyageIds"].add(source_voyage)

    cabins = []
    for x in physical.values():
        cabins.append({
            "provider": x["provider"],
            "shipCode": x["shipCode"],
            "configurationId": x["configurationId"],
            "layoutVersion": x["layoutVersion"],
            "cabinNumber": x["cabinNumber"],
            "deck": x["deck"],
            "providerPositionCodes": sorted(x["providerPositionCodes"]),
            "locations": sorted(x["locations"]),
            "sourceVoyageIds": sorted(x["sourceVoyageIds"]),
            "discoveryVoyageCount": len(x["sourceVoyageIds"]),
        })

    cabins.sort(key=lambda c: (
        c["configurationId"],
        c["deck"]["number"] if c["deck"]["number"] is not None else 999,
        c["cabinNumber"]
    ))
    return cabins, conflicts


def configuration_fingerprint(ship_code, config_id, cabins, assignments, category_rows):
    cabins_for = [c for c in cabins if c.get("configurationId") == config_id]
    assignments_for = [a for a in assignments if assignment_layout(a) == config_id]
    categories_for = [
        c for c in category_rows
        if c.get("configurationId") in (None, config_id)
    ]

    canonical = {
        "shipCode": ship_code,
        "configurationId": config_id,
        "cabins": sorted([
            (c["cabinNumber"], c["deck"]["code"], tuple(c.get("providerPositionCodes") or []))
            for c in cabins_for
        ]),
        "assignments": sorted([
            (
                a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"),
                a.get("cabinNumber"), (a.get("deck") or {}).get("code"),
                a.get("providerPositionCode")
            )
            for a in assignments_for
        ]),
        "categories": sorted([
            (
                c.get("classCode"), c.get("subtypeCode"), c.get("leadCategoryCode"),
                json.dumps(c.get("candidateCategories") or [], sort_keys=True)
            )
            for c in categories_for
        ]),
    }
    payload = json.dumps(canonical, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def load_excluded_voyages(previous_validation_path):
    if not previous_validation_path:
        return set()
    data = load_json(previous_validation_path)
    return {
        str(v.get("voyageId"))
        for v in (data.get("voyages") or [])
        if v.get("voyageId")
    }


def itinerary_signature(v):
    # Prefer explicit stable itinerary/master code when present, otherwise use provider itinerary code.
    src = source_obj(v)
    return (
        src.get("masterItineraryCode")
        or itinerary_code(v)
        or "UNKNOWN"
    )


def duration_nights(v):
    try:
        return int(v.get("durationNights"))
    except Exception:
        return None


def select_candidates_excluding(voyages, ship, max_candidates, excluded):
    """
    Diversity-oriented continuation selection:
      1. exclude previously tested voyages;
      2. bucket by itinerary signature;
      3. spread picks across the full available date range;
      4. prefer underrepresented durations and itinerary signatures;
      5. do not merely choose the latest sailings.
    """
    rows = [
        v for v in voyages
        if ship_code(v) == ship and sail_date(v)
        and str(voyage_id(v)) not in excluded
    ]
    rows.sort(key=lambda v: sail_date(v))
    if not rows:
        return []

    # First pass: one representative from as many itinerary signatures as possible.
    by_sig = defaultdict(list)
    for v in rows:
        by_sig[itinerary_signature(v)].append(v)

    # For each signature, choose a voyage closest to that signature's median date.
    reps = []
    for sig, vals in by_sig.items():
        vals = sorted(vals, key=lambda v: sail_date(v))
        reps.append(vals[len(vals)//2])

    # Spread representatives across global date range.
    reps.sort(key=lambda v: sail_date(v))
    selected = []
    if len(reps) <= max_candidates:
        selected.extend(reps)
    else:
        # Evenly spaced indices across the representative set.
        if max_candidates == 1:
            selected.append(reps[len(reps)//2])
        else:
            for i in range(max_candidates):
                idx = round(i * (len(reps)-1) / (max_candidates-1))
                selected.append(reps[idx])

    # De-duplicate in case rounded indices collide.
    dedup = {}
    for v in selected:
        dedup[str(voyage_id(v))] = v
    selected = list(dedup.values())

    # Fill remaining slots by maximizing novelty of duration/signature/date spacing.
    chosen_ids = {str(voyage_id(v)) for v in selected}
    chosen_sigs = {itinerary_signature(v) for v in selected}
    chosen_durations = {duration_nights(v) for v in selected}

    while len(selected) < max_candidates:
        best = None
        best_score = None
        for v in rows:
            vid = str(voyage_id(v))
            if vid in chosen_ids:
                continue
            sig = itinerary_signature(v)
            dur = duration_nights(v)

            # Date spacing score in days from nearest selected voyage.
            from datetime import date
            vd = date.fromisoformat(sail_date(v))
            if selected:
                nearest = min(
                    abs((vd - date.fromisoformat(sail_date(s))).days)
                    for s in selected
                )
            else:
                nearest = 9999

            score = (
                10000 if sig not in chosen_sigs else 0,
                1000 if dur not in chosen_durations else 0,
                nearest,
                sail_date(v),
            )
            if best_score is None or score > best_score:
                best = v
                best_score = score

        if best is None:
            break
        selected.append(best)
        chosen_ids.add(str(voyage_id(best)))
        chosen_sigs.add(itinerary_signature(best))
        chosen_durations.add(duration_nights(best))

    return sorted(selected, key=lambda v: sail_date(v), reverse=True)

    seen = {(voyage_id(v), sail_date(v), itinerary_code(v)) for v in selected}
    for v in reversed(rows):
        key = (voyage_id(v), sail_date(v), itinerary_code(v))
        if key in seen:
            continue
        selected.append(v)
        seen.add(key)
        if len(selected) >= max_candidates:
            break
    return selected



def enrich_assignment_provenance(assignments):
    # Each assignment record currently preserves one sourceVoyageId: the voyage that first discovered it.
    # Keep that explicit and add a count field for schema consistency.
    out = []
    for a in assignments:
        b = dict(a)
        source = (b.get("sources") or {}).get("sourceVoyageId")
        b["discoveryVoyageCount"] = 1 if source else 0
        out.append(b)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--voyages", required=True)
    ap.add_argument("--baseline-master", required=True,
                    help="Use the v2.0 combined master so existing 2331/2434 evidence is partitioned.")
    ap.add_argument("--previous-validation",
                    help="Optional v2.0 validation; previously tested voyages are excluded.")
    ap.add_argument("--ship", default="XC")
    ap.add_argument("--target-configuration", default="2434")
    ap.add_argument("--country", default="CAN")
    ap.add_argument("--currency", default="CAD")
    ap.add_argument("--adults", type=int, default=2)
    ap.add_argument("--children", type=int, default=0)
    ap.add_argument("--max-candidates", type=int, default=5)
    ap.add_argument("--saturation-tail", type=int, default=2)
    ap.add_argument("--min-distinct-itineraries", type=int, default=1)
    ap.add_argument("--include-voyage-ids", default="")
    ap.add_argument("--delay-ms", type=int, default=100)
    ap.add_argument("--output", default="celebrity-configuration-saturation-v2.2")
    args = ap.parse_args()

    voyages = flatten_voyages(load_json(args.voyages))
    baseline = load_json(args.baseline_master)
    excluded = load_excluded_voyages(args.previous_validation)
    previous_validation = load_json(args.previous_validation) if args.previous_validation else {}
    previous_voyage_reports = list(previous_validation.get("voyages") or [])
    included = {x for x in args.include_voyage_ids.split(",") if x}
    if included:
        voyages = [v for v in voyages if str(voyage_id(v)) in included]
    candidates = select_candidates_excluding(voyages, args.ship, args.max_candidates, excluded)

    if not candidates:
        raise RuntimeError(f"No untested candidate voyages found for ship {args.ship}.")

    output = Path(args.output)
    raw_root = output / "raw"
    raw_root.mkdir(parents=True, exist_ok=True)

    # Partition all prior assignments by provider layout token.
    baseline_assignments = [with_configuration(a) for a in (baseline.get("categoryAssignments") or [])]
    assignment_map = {assignment_key(a): a for a in baseline_assignments}

    hierarchy_by_config = defaultdict(dict)
    # Preserve existing category rows if the v2.0 master contains them.
    for c in baseline.get("categoryMaster") or []:
        cfg = c.get("configurationId") or "UNSCOPED"
        key = (c.get("classCode"), c.get("subtypeCode"), c.get("leadCategoryCode"))
        hierarchy_by_config[cfg][key] = {
            "typeCode": c.get("classCode"),
            "typeName": c.get("className"),
            "subtypeCode": c.get("subtypeCode"),
            "subtypeName": c.get("subtypeName"),
            "leadCategoryCode": c.get("leadCategoryCode"),
            "candidateCategories": c.get("candidateCategories") or [],
        }

    baseline_target_assignments = {
        assignment_key(a) for a in baseline_assignments
        if assignment_layout(a) == args.target_configuration
    }
    baseline_target_cabins = {
        a.get("cabinNumber") for a in baseline_assignments
        if assignment_layout(a) == args.target_configuration
    }
    baseline_target_categories = {
        (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"))
        for a in baseline_assignments
        if assignment_layout(a) == args.target_configuration
    }
    baseline_target_category_decks = {
        (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"),
         (a.get("deck") or {}).get("code"))
        for a in baseline_assignments
        if assignment_layout(a) == args.target_configuration
    }

    session = requests.Session(impersonate="chrome")
    try:
        session.get(BASE + "/", timeout=30)
    except Exception:
        pass

    # Preserve the complete tested-voyage history across Daily increments. This
    # prevents a later Daily run from retesting Full-run voyages and allows the
    # no-change saturation tail to span consecutive runs.
    voyage_reports = list(previous_voyage_reports)
    current_voyage_reports = []

    print("Celebrity JSON-only configuration crawler v2.3")
    print(f"  Ship:                    {args.ship}")
    print(f"  Target configuration:    {args.target_configuration}")
    print(f"  Previously tested:       {len(excluded)}")
    print(f"  Target baseline cabins:  {len(baseline_target_cabins)}")
    print(f"  Target baseline assigns: {len(baseline_target_assignments)}")
    print(f"  New candidate voyages:   {len(candidates)}")
    print()

    for index, v in enumerate(candidates, 1):
        ctx = voyage_context(v, args.country, args.currency, args.adults, args.children)
        history_index = len(previous_voyage_reports) + index
        vdir = raw_root / f"{history_index:02d}-{ctx['sailDate']}-{safe_name(ctx['voyageId'])}"
        vdir.mkdir(parents=True, exist_ok=True)

        before_target_assignments = {
            k for k in assignment_map if k[0] == args.target_configuration
        }
        before_target_cabins = {k[4] for k in before_target_assignments}
        before_target_categories = {(k[1], k[2], k[3]) for k in before_target_assignments}
        before_target_category_decks = {(k[1], k[2], k[3], k[5]) for k in before_target_assignments}

        print(f"[{index:02d}/{len(candidates):02d}] {ctx['sailDate']} {ctx['itineraryCode']} {ctx['voyageId']}")

        voyage_failures = []
        queried_decks = []
        hierarchy = []
        observed_layouts = set()

        try:
            hierarchy, bootstrap_filter, bootstrap_response, bootstrap_attempts = discover_json_hierarchy(session, ctx)
            dump_json(vdir / "bootstrap-filter.json", bootstrap_filter)
            dump_json(vdir / "bootstrap-response.json", bootstrap_response)
            dump_json(vdir / "bootstrap-attempts.json", bootstrap_attempts)
            dump_json(vdir / "hierarchy.json", hierarchy)
        except Exception as exc:
            voyage_failures.append({"stage": "json-hierarchy", "error": repr(exc)})
            print(f"  JSON HIERARCHY FAILED: {exc}")
            voyage_reports.append({
                "voyageId": ctx["voyageId"],
                "sailDate": ctx["sailDate"],
                "itineraryCode": ctx["itineraryCode"],
                "observedConfigurations": [],
                "targetConfigurationSeen": False,
                "newTargetCabins": 0,
                "newTargetAssignments": 0,
                "newTargetCategories": 0,
                "newTargetCategoryDecks": 0,
                "failureCount": len(voyage_failures),
                "failures": voyage_failures,
            })
            continue

        for h in hierarchy:
            class_code = h.get("typeCode")
            subtype_code = h.get("subtypeCode")
            seed_cat = h.get("leadCategoryCode")
            if not class_code or not subtype_code:
                continue

            label = f"{class_code}/{subtype_code}/{seed_cat or '-'}"
            print(f"  {label}", end="", flush=True)

            try:
                decks, probe_attempts = discover_subtype_decks(
                    session, ctx, class_code, subtype_code
                )
                for probe_index, probe in enumerate(probe_attempts, 1):
                    stem = (
                        f"probe-{safe_name(class_code)}-{safe_name(subtype_code)}"
                        f"-{probe_index:02d}-deck-{safe_name(probe['requestedDeckCode'])}"
                    )
                    dump_json(vdir / f"{stem}-filter.json", probe["filter"])
                    dump_json(vdir / f"{stem}-response.json", probe["response"])
            except Exception as exc:
                voyage_failures.append({
                    "stage": "json-deck-discovery",
                    "classCode": class_code,
                    "subtypeCode": subtype_code,
                    "seedCategoryCode": seed_cat,
                    "error": repr(exc),
                })
                print(" -> JSON deck discovery FAILED")
                continue

            if not decks:
                print(" -> no physical decks")
                continue

            for d in decks:
                cfg = layout_version_from_url(d.get("deckPlanUrl"))
                if cfg:
                    observed_layouts.add(cfg)

            print(f" -> decks {','.join(d['code'] for d in decks)}")

            for deck in decks:
                    deck_code = deck["code"]
                    try:
                        filt, data, final_url, rn = fetch_rooms_api(
                            session, ctx, class_code, subtype_code, deck_code
                        )
                        dump_json(
                            vdir / f"rooms-{safe_name(class_code)}-{safe_name(subtype_code)}-{safe_name(seed_cat)}-deck-{deck_code}-filter.json",
                            filt
                        )
                        dump_json(
                            vdir / f"rooms-{safe_name(class_code)}-{safe_name(subtype_code)}-{safe_name(seed_cat)}-deck-{deck_code}-response.json",
                            data
                        )

                        if not isinstance(rn, dict):
                            voyage_failures.append({
                                "stage": "rooms-api",
                                "classCode": class_code,
                                "subtypeCode": subtype_code,
                                "seedCategoryCode": seed_cat,
                                "deckCode": deck_code,
                                "error": "No roomNumbers in response",
                            })
                            continue

                        returned_type, returned_subtype = returned_selector(data)
                        if returned_type != class_code or returned_subtype != subtype_code:
                            voyage_failures.append({
                                "stage": "rooms-api",
                                "classCode": class_code,
                                "subtypeCode": subtype_code,
                                "seedCategoryCode": seed_cat,
                                "deckCode": deck_code,
                                "error": (
                                    f"Provider fallback returned {returned_type}/{returned_subtype}"
                                ),
                            })
                            continue

                        provider_selected = selected_deck(rn)
                        returned_deck = str(
                            (provider_selected or {}).get("code")
                            or (provider_selected or {}).get("number") or ""
                        ).zfill(2)
                        if provider_selected is None or returned_deck != str(deck_code).zfill(2):
                            voyage_failures.append({
                                "stage": "rooms-api",
                                "classCode": class_code,
                                "subtypeCode": subtype_code,
                                "seedCategoryCode": seed_cat,
                                "deckCode": deck_code,
                                "error": f"Provider selected deck {returned_deck or None}",
                            })
                            continue

                        rows = assignments_from_room_numbers(
                            ctx, class_code, subtype_code, rn, final_url
                        )

                        configured_rows = []
                        returned_cfgs = set()
                        for raw in rows:
                            a = with_configuration(raw)
                            returned_cfgs.add(a["configurationId"])
                            observed_layouts.add(a["configurationId"])
                            configured_rows.append(a)
                            assignment_map.setdefault(assignment_key(a), a)

                        queried_decks.append({
                            "classCode": class_code,
                            "subtypeCode": subtype_code,
                            "seedCategoryCode": seed_cat,
                            "deckCode": deck_code,
                            "configurationIds": sorted(returned_cfgs),
                            "returnedCategoryCodes": sorted(set(
                                r["categoryCode"] for r in configured_rows if r.get("categoryCode")
                            )),
                            "cabinCount": len(configured_rows),
                        })

                    except Exception as exc:
                        voyage_failures.append({
                            "stage": "rooms-api",
                            "classCode": class_code,
                            "subtypeCode": subtype_code,
                            "seedCategoryCode": seed_cat,
                            "deckCode": deck_code,
                            "error": repr(exc),
                        })

                    if args.delay_ms > 0:
                        time.sleep(args.delay_ms / 1000.0)

        # Scope hierarchy to each layout actually observed on this voyage.
        for cfg in observed_layouts:
            if cfg == "UNKNOWN":
                continue
            for h in hierarchy:
                hierarchy_by_config[cfg][hierarchy_key(h)] = h

        after_target_assignments = {
            k for k in assignment_map if k[0] == args.target_configuration
        }
        after_target_cabins = {k[4] for k in after_target_assignments}
        after_target_categories = {(k[1], k[2], k[3]) for k in after_target_assignments}
        after_target_category_decks = {(k[1], k[2], k[3], k[5]) for k in after_target_assignments}

        target_seen = args.target_configuration in observed_layouts
        report = {
            "voyageId": ctx["voyageId"],
            "sailDate": ctx["sailDate"],
            "itineraryCode": ctx["itineraryCode"],
            "observedConfigurations": sorted(observed_layouts),
            "targetConfigurationSeen": target_seen,
            "hierarchyEntryCount": len(hierarchy),
            "queriedDeckCount": len(queried_decks),
            "newTargetCabins": len(after_target_cabins - before_target_cabins),
            "newTargetAssignments": len(after_target_assignments - before_target_assignments),
            "newTargetCategories": len(after_target_categories - before_target_categories),
            "newTargetCategoryDecks": len(after_target_category_decks - before_target_category_decks),
            "newTargetCabinNumbers": sorted(after_target_cabins - before_target_cabins),
            "failureCount": len(voyage_failures),
            "failures": voyage_failures,
            "queriedDecks": queried_decks,
        }
        voyage_reports.append(report)
        current_voyage_reports.append(report)
        dump_json(vdir / "voyage-report.json", report)

        print(
            f"    configs={','.join(sorted(observed_layouts)) or 'NONE'}; "
            f"target delta: +{report['newTargetCabins']} cabins, "
            f"+{report['newTargetAssignments']} assignments, "
            f"+{report['newTargetCategories']} categories, "
            f"+{report['newTargetCategoryDecks']} category/decks; "
            f"failures={report['failureCount']}"
        )

        eligible_now = [
            r for r in voyage_reports
            if r.get("targetConfigurationSeen") and r.get("failureCount", 0) == 0
        ]
        tail_now = eligible_now[-args.saturation_tail:]
        if (
            len(tail_now) >= args.saturation_tail
            and all(
                r.get("newTargetCabins", 0) == 0
                and r.get("newTargetAssignments", 0) == 0
                and r.get("newTargetCategories", 0) == 0
                and r.get("newTargetCategoryDecks", 0) == 0
                for r in tail_now
            )
            and len({r.get("itineraryCode") for r in tail_now if r.get("itineraryCode")})
                >= args.min_distinct_itineraries
        ):
            print(f"  Saturation reached after {len(voyage_reports)} voyage(s); stopping early.")
            break

    assignments = sorted(
        enrich_assignment_provenance([with_configuration(a) for a in assignment_map.values()]),
        key=lambda a: (
            a.get("configurationId") or "",
            a.get("classCode") or "", a.get("subtypeCode") or "",
            a.get("categoryCode") or "", (a.get("deck") or {}).get("code") or "",
            a.get("cabinNumber") or ""
        )
    )
    cabins, conflicts = build_physical(args.ship, assignments)

    # Build config-scoped category rows.
    category_master = []
    for cfg, mapping in sorted(hierarchy_by_config.items()):
        if cfg == "UNSCOPED":
            continue
        category_master.extend(category_master_from_hierarchy(
            sorted(mapping.values(), key=lambda h: (
                h.get("typeCode") or "", h.get("subtypeCode") or "",
                h.get("leadCategoryCode") or ""
            )),
            args.ship, cfg
        ))

    config_ids = sorted(set(
        [c.get("configurationId") for c in cabins if c.get("configurationId")]
        + [assignment_layout(a) for a in assignments]
    ))

    configurations = []
    for cfg in config_ids:
        cfg_cabins = [c for c in cabins if c.get("configurationId") == cfg]
        cfg_assign = [a for a in assignments if assignment_layout(a) == cfg]
        cfg_categories = {
            (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"))
            for a in cfg_assign
        }
        cfg_cat_decks = {
            (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"),
             (a.get("deck") or {}).get("code"))
            for a in cfg_assign
        }
        configurations.append({
            "configurationId": cfg,
            "layoutVersion": cfg,
            "physicalCabinCount": len(cfg_cabins),
            "categoryAssignmentCount": len(cfg_assign),
            "categoryCount": len(cfg_categories),
            "categoryDeckCount": len(cfg_cat_decks),
            "configurationFingerprint": configuration_fingerprint(
                args.ship, cfg, cabins, assignments, category_master
            ),
        })

    target_assignments = {
        assignment_key(a) for a in assignments
        if assignment_layout(a) == args.target_configuration
    }
    target_cabins = {
        a.get("cabinNumber") for a in assignments
        if assignment_layout(a) == args.target_configuration
    }
    target_categories = {
        (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"))
        for a in assignments if assignment_layout(a) == args.target_configuration
    }
    target_category_decks = {
        (a.get("classCode"), a.get("subtypeCode"), a.get("categoryCode"),
         (a.get("deck") or {}).get("code"))
        for a in assignments if assignment_layout(a) == args.target_configuration
    }

    # Saturation tail counts only successful voyages that actually exposed target config.
    eligible = [
        r for r in voyage_reports
        if r.get("targetConfigurationSeen") and r.get("failureCount", 0) == 0
    ]
    tail = eligible[-min(args.saturation_tail, len(eligible)):]
    tail_no_change = all(
        r.get("newTargetCabins", 0) == 0
        and r.get("newTargetAssignments", 0) == 0
        and r.get("newTargetCategories", 0) == 0
        and r.get("newTargetCategoryDecks", 0) == 0
        for r in tail
    )
    tail_itineraries = len(set(
        r.get("itineraryCode") for r in tail if r.get("itineraryCode")
    ))
    saturated = (
        len(tail) >= args.saturation_tail
        and tail_no_change
        and tail_itineraries >= args.min_distinct_itineraries
    )

    master = {
        "version": "2.3",
        "provider": "CELEBRITY",
        "shipCode": args.ship,
        "generatedAtUtc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "configurationModel": "deckPlanUrl layout token",
        "targetConfiguration": args.target_configuration,
        "fareProducts": baseline.get("fareProducts") or [],
        "configurations": configurations,
        "cabins": cabins,
        "categoryAssignments": assignments,
        "categoryMaster": category_master,
        "saturation": {
            "targetConfiguration": args.target_configuration,
            "excludedPreviouslyTestedVoyageCount": len(excluded),
            "candidateVoyageCount": len(candidates),
            "currentRunTestedVoyageCount": len(current_voyage_reports),
            "testedVoyageCount": len(voyage_reports),
            "eligibleTargetVoyageCount": len(eligible),
            "tailLength": len(tail),
            "tailNoChange": tail_no_change,
            "tailDistinctItineraryCount": tail_itineraries,
            "requiredTailLength": args.saturation_tail,
            "requiredDistinctItineraries": args.min_distinct_itineraries,
            "saturated": saturated,
        },
    }

    validation = {
        "version": "2.3",
        "provider": "CELEBRITY",
        "shipCode": args.ship,
        "targetConfiguration": args.target_configuration,
        "baselineTarget": {
            "physicalCabinCount": len(baseline_target_cabins),
            "categoryAssignmentCount": len(baseline_target_assignments),
            "categoryCount": len(baseline_target_categories),
            "categoryDeckCount": len(baseline_target_category_decks),
        },
        "finalTarget": {
            "physicalCabinCount": len(target_cabins),
            "categoryAssignmentCount": len(target_assignments),
            "categoryCount": len(target_categories),
            "categoryDeckCount": len(target_category_decks),
        },
        "targetGrowth": {
            "physicalCabins": len(target_cabins - baseline_target_cabins),
            "categoryAssignments": len(target_assignments - baseline_target_assignments),
            "categories": len(target_categories - baseline_target_categories),
            "categoryDecks": len(target_category_decks - baseline_target_category_decks),
        },
        "configurations": configurations,
        "cabinDeckConflictCount": len(conflicts),
        "cabinDeckConflicts": conflicts,
        "failureCount": sum(r.get("failureCount", 0) for r in voyage_reports),
        "currentRunFailureCount": sum(r.get("failureCount", 0) for r in current_voyage_reports),
        "voyages": voyage_reports,
        "saturation": master["saturation"],
    }

    dump_json(output / f"celebrity-ship-master-{args.ship}-v2.2.json", master)
    dump_json(output / f"celebrity-cabin-master-{args.ship}-v2.2.json", cabins)
    dump_json(output / f"celebrity-cabin-category-assignments-{args.ship}-v2.2.json", assignments)
    dump_json(output / f"celebrity-category-master-{args.ship}-v2.2.json", category_master)
    dump_json(output / f"celebrity-ship-master-validation-{args.ship}-v2.2.json", validation)
    dump_json(output / "celebrity-configuration-saturation-voyage-report-v2.2.json", voyage_reports)

    print()
    print("Celebrity JSON-only configuration crawl v2.3 complete.")
    print(f"  Target configuration:      {args.target_configuration}")
    print(f"  Baseline target cabins:    {len(baseline_target_cabins)}")
    print(f"  Final target cabins:       {len(target_cabins)}  (+{len(target_cabins - baseline_target_cabins)})")
    print(f"  Baseline target assigns:   {len(baseline_target_assignments)}")
    print(f"  Final target assigns:      {len(target_assignments)}  (+{len(target_assignments - baseline_target_assignments)})")
    print(f"  New target categories:     {len(target_categories - baseline_target_categories)}")
    print(f"  New target category/decks: {len(target_category_decks - baseline_target_category_decks)}")
    print(f"  Total failures:            {validation['failureCount']}")
    print(f"  Cabin/deck conflicts:      {len(conflicts)}")
    print(f"  Eligible target voyages:   {len(eligible)}")
    print(f"  Tail no-change:            {tail_no_change}")
    print(f"  Tail distinct itineraries: {tail_itineraries}")
    print(f"  Saturated:                 {saturated}")
    print()
    print("  Configurations:")
    for c in configurations:
        print(
            f"    {c['configurationId']}: "
            f"{c['physicalCabinCount']} cabins, "
            f"{c['categoryAssignmentCount']} assignments, "
            f"fingerprint={c['configurationFingerprint']}"
        )
    print(f"  Output:                    {output.resolve()}")

    if validation["failureCount"]:
        print()
        print("WARNING: one or more discovery/API calls failed. Review validation before declaring saturation.")


if __name__ == "__main__":
    main()
