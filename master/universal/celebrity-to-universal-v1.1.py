#!/usr/bin/env python3
"""
Celebrity -> Universal Cabin Model v1.1 adapter, patch 1.1.1.

Fixes:
- never relabels records from another configuration
- configuration filtering uses source evidence
- merges physical-cabin and assignment evidence by configuration+cabin
- understands nested deck objects and providerPositionCode
- reports unmatched physical cabins / assignments
"""
from pathlib import Path
import argparse, json, re
from common import *

POS={"FW":"FORWARD","MS":"MIDSHIP","AF":"AFT"}

def cfg_of(d):
    for k in ("configurationId","providerConfigurationId","physicalConfigurationId",
              "deckPlanVersion","layoutVersion","configuration"):
        v=d.get(k)
        if isinstance(v,(str,int)) and str(v).strip():
            return str(v).strip()
    # configurationKey may be CELEBRITY:XC:DECKPLAN:2434
    v=d.get("configurationKey")
    if isinstance(v,str):
        m=re.search(r"DECKPLAN:([^:]+)$",v)
        if m: return m.group(1)
    return None

def inherited_dicts(obj, inherited_cfg=None):
    """Yield (dict, nearest configuration id) while walking source JSON."""
    if isinstance(obj,dict):
        here=cfg_of(obj) or inherited_cfg
        yield obj,here
        for v in obj.values():
            yield from inherited_dicts(v,here)
    elif isinstance(obj,list):
        for v in obj:
            yield from inherited_dicts(v,inherited_cfg)

def cabin_no(d):
    # Only explicit cabin/room identifiers are valid here.
    # Generic `number` is intentionally excluded because Celebrity deck
    # objects also contain `number` (e.g. deck 10) plus deckPlanUrl.
    v=first(d,"cabinNumber","roomNumber",default=None)
    if v is None:
        return None
    s=str(v).strip()
    return s if s and any(ch.isdigit() for ch in s) else None

def nested_deck(d):
    deck=d.get("deck")
    if isinstance(deck,dict):
        code=first(deck,"code","providerCode",default=None)
        num=first(deck,"number","deckNumber",default=None)
        name=first(deck,"name","deckName",default=None)
        url=first(deck,"deckPlanUrl","url",default=None)
    else:
        code=first(d,"deckCode","providerDeckCode",default=None)
        num=first(d,"deckNumber",default=None)
        name=first(d,"deckName",default=None)
        url=first(d,"deckPlanUrl",default=None)
    try: num=int(num) if num not in (None,"") else None
    except: num=None
    return code,num,name,url

def category_of(d):
    v=first(d,"categoryCode","providerCategoryCode",default=None)
    if isinstance(v,dict): v=first(v,"code","categoryCode",default=None)
    return str(v).strip() if v not in (None,"") else None

def type_of(d):
    return first(d,"stateroomTypeCode","typeCode","classCode","providerTypeCode",default=None)

def subtype_of(d):
    return first(d,"stateroomSubtypeCode","subtypeCode","providerSubtypeCode",default=None)

def pos_of(d):
    v=first(d,"providerPositionCode","positionCode",default=None)
    if v is None and isinstance(d.get("position"),dict):
        v=first(d["position"],"code","providerCode",default=None)
    return str(v).strip().upper() if v not in (None,"") else None

def looks_physical(d):
    n=cabin_no(d)
    if not n: return False
    code,num,name,url=nested_deck(d)
    return any(x is not None for x in (code,num,name,url)) or pos_of(d) is not None

def looks_assignment(d):
    return cabin_no(d) is not None and category_of(d) is not None

def score_physical(d):
    code,num,name,url=nested_deck(d)
    return sum(x is not None for x in (code,num,name,url,pos_of(d))) + len(d)/10000

def score_assignment(d):
    return sum(x is not None for x in (category_of(d),type_of(d),subtype_of(d))) + len(d)/10000

def base_record(ship,cfg,n):
    return {
      "provider":{"code":"CELEBRITY","raw":{}},
      "ship":{"providerShipCode":ship,"name":None},
      "physicalConfiguration":{"configurationKey":f"CELEBRITY:{ship}:DECKPLAN:{cfg}",
        "providerConfigurationId":cfg,"firstObservedSailingDate":None,"lastObservedSailingDate":None,
        "fingerprint":None,"evidence":[]},
      "cabin":{"cabinNumber":n,
        "deck":{"providerCode":None,"number":None,"name":None,"deckPlanUrl":None,"evidence":[]},
        "location":{"providerCode":None,"providerLabel":None,"zone":"UNKNOWN","evidence":[]},
        "berths":fact(None,[]),
        "accessibility":{"accessible":None,"providerCode":None,"providerLabel":None,"canonicalType":"UNKNOWN","features":[],"evidence":[]},
        "relationships":[],
        "area":{"providerAreaSqFt":number_fact(None,[]),"interiorAreaSqFt":number_fact(None,[]),
                "outdoorAreaSqFt":number_fact(None,[]),"totalAreaSqFt":number_fact(None,[]),"providerSemantics":None},
        "bath":{"providerType":None,"hasTub":None,"hasShower":None,"evidence":[]},
        "providerLayoutVariant":{"code":None,"label":None,"evidence":[]},
        "rawAttributes":{}},
      "accommodationDefinition":{"providerTypeCode":None,"providerTypeName":None,"providerSubtypeCode":None,
        "providerSubtypeName":None,"physicalClass":"UNKNOWN","roomType":None,"view":"UNKNOWN",
        "outdoorSpace":"UNKNOWN","obstruction":"UNKNOWN",
        "size":{"interiorSqFt":number_fact(None,[]),"outdoorSqFt":number_fact(None,[]),"totalSqFt":number_fact(None,[]),"providerText":None},
        "occupancy":{"min":fact(None,[]),"max":fact(None,[]),"providerText":None},
        "physicalFeatures":[],"providerDescription":[],"providerFeaturesRaw":[],"galleryRaw":[]},
      "serviceTier":{"canonicalTier":None,"providerCode":None,"providerName":None,"benefits":[]},
      "commercialCategory":{"providerCategoryCode":None,"providerCategoryName":None,"providerMetaCode":None,
        "providerSubMetaCode":None,"guarantee":None,"firstObservedSailingDate":None,"lastObservedSailingDate":None,
        "hierarchyFingerprint":None,"raw":{}},
      "assignment":{"configurationKey":f"CELEBRITY:{ship}:DECKPLAN:{cfg}","cabinNumber":n,
        "providerCategoryCode":"UNKNOWN","firstObservedSailingDate":None,"lastObservedSailingDate":None,
        "sourceVoyageIds":[],"derivedCharacteristics":[],"evidence":[]}
    }

def merge(ship,cfg,n,p,a):
    r=base_record(ship,cfg,n); src="Celebrity configuration-saturation source"
    if p:
        code,num,name,url=nested_deck(p)
        r["cabin"]["deck"].update({"providerCode":str(code) if code is not None else None,
                                  "number":num,"name":name,"deckPlanUrl":url})
        if any(x is not None for x in (code,num,name,url)):
            r["cabin"]["deck"]["evidence"]=[evidence(PROVENANCE["STRUCTURED"],"CABIN",src,
                {"code":code,"number":num,"name":name,"deckPlanUrl":url})]
        pos=pos_of(p)
        if pos:
            r["cabin"]["location"].update({"providerCode":pos,
                "providerLabel":{"FW":"Forward","MS":"Mid-Ship","AF":"Aft"}.get(pos),
                "zone":POS.get(pos,"UNKNOWN"),
                "evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",src,pos)]})
        r["cabin"]["rawAttributes"]["physical"]=p
    if a:
        cat=category_of(a); typ=type_of(a); sub= subtype_of(a)
        r["commercialCategory"]["providerCategoryCode"]=cat
        r["accommodationDefinition"]["providerTypeCode"]=str(typ) if typ is not None else None
        r["accommodationDefinition"]["providerSubtypeCode"]=str(sub) if sub is not None else None
        r["assignment"]["providerCategoryCode"]=cat or "UNKNOWN"
        if cat:
            r["assignment"]["evidence"]=[evidence(PROVENANCE["STRUCTURED"],"CABIN",src,cat)]
        r["cabin"]["rawAttributes"]["assignment"]=a
    return r

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--ship",default="XC"); ap.add_argument("--configuration",default=None)
    a=ap.parse_args(); p=Path(a.input); files=[p] if p.is_file() else sorted(p.rglob("*.json"))

    physical={}; assignments={}; detected=set(); skipped_other_cfg=0; unscoped=0
    for f in files:
        try: obj=json.loads(f.read_text(encoding="utf-8"))
        except: continue
        for d,cfg in inherited_dicts(obj):
            if cfg: detected.add(cfg)
            if a.configuration and cfg and cfg != a.configuration:
                skipped_other_cfg += 1; continue
            # With an explicit target, unscoped records are accepted only if the payload itself
            # contains a target configuration marker. This prevents silent cross-config relabeling.
            effective=cfg
            if effective is None:
                unscoped += 1
                continue
            if a.configuration and effective != a.configuration: continue
            n=cabin_no(d)
            if not n: continue
            key=(effective,n)
            if looks_physical(d) and (key not in physical or score_physical(d)>score_physical(physical[key])):
                physical[key]=d
            if looks_assignment(d) and (key not in assignments or score_assignment(d)>score_assignment(assignments[key])):
                assignments[key]=d

    keys=sorted(set(physical)|set(assignments))
    records=[merge(a.ship,cfg,n,physical.get((cfg,n)),assignments.get((cfg,n))) for cfg,n in keys]
    unmatched_p=sorted([{"configurationId":c,"cabinNumber":n} for c,n in physical if (c,n) not in assignments],
                       key=lambda x:(x["configurationId"],x["cabinNumber"]))
    unmatched_a=sorted([{"configurationId":c,"cabinNumber":n} for c,n in assignments if (c,n) not in physical],
                       key=lambda x:(x["configurationId"],x["cabinNumber"]))

    result={"schemaVersion":"1.1","adapterVersion":"1.1.2","provider":"CELEBRITY",
      "requestedConfigurationId":a.configuration,"detectedConfigurationIds":sorted(detected),
      "physicalCabinCount":len(physical),"assignmentCabinCount":len(assignments),
      "mergedCabinCount":len(records),"unmatchedPhysicalCabins":unmatched_p,
      "unmatchedAssignments":unmatched_a,"skippedOtherConfigurationObjects":skipped_other_cfg,
      "unscopedObjectsSkipped":unscoped,"records":records}
    dump_json(Path(a.out),result)
    print(json.dumps({k:result[k] for k in ("requestedConfigurationId","detectedConfigurationIds",
      "physicalCabinCount","assignmentCabinCount","mergedCabinCount",
      "skippedOtherConfigurationObjects","unscopedObjectsSkipped")},indent=2))
    print(f"Unmatched physical cabins: {len(unmatched_p)}")
    print(f"Unmatched assignments: {len(unmatched_a)}")

if __name__=="__main__": main()
