from __future__ import annotations
from pathlib import Path
from typing import Any, Iterable
from datetime import date, datetime
import hashlib, json, re

def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8-sig"))

def dump_json(path: str | Path, obj: Any) -> None:
    p=Path(path); p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf-8")

def stable_hash(obj: Any, version: str="sha256-json-v1") -> str:
    if version != "sha256-json-v1":
        raise ValueError(version)
    raw=json.dumps(obj, sort_keys=True, separators=(",",":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def parse_date(s: str) -> date:
    return date.fromisoformat(str(s)[:10])

def sailing_date(v: dict) -> str | None:
    return first(v, "sailDate", "departureDate", default=None)

def future_voyages(voyages: list[dict], survey_start: date) -> list[dict]:
    # Permanent rule: departing today is already excluded.
    out=[]
    for v in voyages:
        sd=sailing_date(v)
        if not sd: continue
        if parse_date(sd) > survey_start:
            out.append(v)
    return sorted(out, key=lambda x: (str(x.get("shipCode","")), sailing_date(x) or ""))

def first(d: dict, *keys, default=None):
    for k in keys:
        if k in d and d[k] not in (None,""):
            return d[k]
    return default

def normalize_hierarchy_tuples(entries: Iterable[dict]) -> list[list[str]]:
    rows=set()
    for e in entries:
        t=str(first(e,"typeCode","classCode","stateroomTypeCode",default="") or "")
        s=str(first(e,"subtypeCode","stateroomSubtypeCode",default="") or "")
        c=str(first(e,"categoryCode","leadCategoryCode",default="") or "")
        rows.add((t,s,c))
    return [list(x) for x in sorted(rows)]

def build_signature(entries: Iterable[dict]) -> dict:
    rows=normalize_hierarchy_tuples(entries)
    return {"algorithm":"sha256-json-v1","tupleCount":len(rows),"hash":stable_hash(rows),"tuples":rows}

def transition_records(observations: list[dict]) -> list[dict]:
    """
    Build explicit observed transition bounds. These are NOT inferred effective dates.
    AdjacentPublishedSailings is true only if the two differing observations are adjacent
    in the supplied published-voyage sequence for that ship.
    """
    by_ship={}
    for o in observations:
        by_ship.setdefault(o["shipCode"],[]).append(o)
    result=[]
    for ship, xs in by_ship.items():
        xs=sorted(xs,key=lambda x:x["sailDate"])
        successful=[x for x in xs if x.get("status")=="SUCCESS"]
        for a,b in zip(successful, successful[1:]):
            pa=a.get("physicalConfigurationId")
            pb=b.get("physicalConfigurationId")
            # Only proven stable physical configuration participates in transition detection.
            # commercialOfferSignature is intentionally excluded because it can vary with
            # sailing-level availability/sellability and must not create fake config eras.
            if pa != pb:
                # Count published voyage records strictly between the two observations.
                between=[x for x in xs if a["sailDate"] < x["sailDate"] < b["sailDate"]]
                result.append({
                  "shipCode":ship,
                  "previous":{
                    "voyageId":a.get("voyageId"),"sailDate":a["sailDate"],
                    "physicalConfigurationId":a.get("physicalConfigurationId"),
                    "commercialSchemaId":a.get("commercialSchemaId")
                  },
                  "next":{
                    "voyageId":b.get("voyageId"),"sailDate":b["sailDate"],
                    "physicalConfigurationId":b.get("physicalConfigurationId"),
                    "commercialSchemaId":b.get("commercialSchemaId")
                  },
                  "adjacentPublishedSailings": len(between)==0,
                  "unresolvedPublishedSailingCount": len(between),
                  "windowStartExclusive": a["sailDate"],
                  "windowEndInclusive": b["sailDate"]
                })
    return result

def observed_eras(observations: list[dict]) -> list[dict]:
    by_ship={}
    for o in observations:
        if o.get("status")!="SUCCESS": continue
        by_ship.setdefault(o["shipCode"],[]).append(o)
    eras=[]
    for ship,xs in by_ship.items():
        xs=sorted(xs,key=lambda x:x["sailDate"])
        current=None
        for x in xs:
            key=x.get("physicalConfigurationId")
            if current is None or current["_key"] != key:
                if current:
                    current.pop("_key",None); eras.append(current)
                current={"_key":key,"shipCode":ship,
                  "physicalConfigurationId":key,
                  "firstObservedSailingDate":x["sailDate"],
                  "lastObservedSailingDate":x["sailDate"],
                  "observedVoyageIds":[x.get("voyageId")]}
            else:
                current["lastObservedSailingDate"]=x["sailDate"]
                current["observedVoyageIds"].append(x.get("voyageId"))
        if current:
            current.pop("_key",None); eras.append(current)
    return eras
