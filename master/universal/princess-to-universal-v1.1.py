#!/usr/bin/env python3
from pathlib import Path
import argparse, json, re
from common import *

POSITION_MAP={
    "forward":"FORWARD","mid-forward":"MID_FORWARD","mid forward":"MID_FORWARD",
    "midship":"MIDSHIP","mid-ship":"MIDSHIP","mid-aft":"MID_AFT","mid aft":"MID_AFT","aft":"AFT"
}
PHYSICAL={"I":"INTERIOR","O":"OCEANVIEW","B":"BALCONY","M":"MINI_SUITE","S":"SUITE"}
ACCESS={"A":"AMBULATORY_ACCESSIBLE","W":"WHEELCHAIR_ACCESSIBLE","M":"WHEELCHAIR_SINGLE_SIDE_APPROACH"}

def load_audit(root: Path):
    p=root/"princess-provider-metadata-audit-v1.1.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}

def cabin_number(c):
    return str(first(c,"number","cabinNumber","roomNumber",default="")).strip()

def category_code(c):
    return str(first(c,"categoryCode","category","cat",default="")).strip()

def normalize_access(c, source):
    code=str(first(c,"accessible","accessibleCode","accessibilityCode",default="") or "").strip().upper()
    wa=first(c,"wheelchairAccessible",default=None)
    accessible = True if (code or wa is True) else (False if wa is False else None)
    ctype=ACCESS.get(code, "ACCESSIBLE_OTHER" if accessible else ("NOT_ACCESSIBLE" if accessible is False else "UNKNOWN"))
    ev=[]
    if code or wa is not None:
        ev.append(evidence(PROVENANCE["STRUCTURED"],"CABIN",source,{"code":code or None,"wheelchairAccessible":wa}))
    return {"accessible":accessible,"providerCode":code or None,"providerLabel":None,
            "canonicalType":ctype,"features":[],"evidence":ev}

def parse_connections(c, self_no, source):
    raw=first(c,"connectingRoom","connectingRooms","connectingCabin",default=None)
    if not raw: return []
    vals=[]
    if isinstance(raw,list): vals=[str(x) for x in raw]
    else: vals=re.findall(r"[A-Za-z]?\d{2,5}",str(raw))
    out=[]
    for x in vals:
        if x and x != self_no:
            out.append({"type":"CONNECTING_CABIN","targetCabinNumber":x,"bidirectional":None,
                        "providerRaw":str(raw),
                        "evidence":[evidence(PROVENANCE["RELATIONSHIP"],"CABIN",source,raw)]})
    return out

def normalize_cabin(ship, version, deck_no, c):
    no=cabin_number(c); source=f"getDeckJSON.do ship={ship} version={version} deck={deck_no}"
    loc=str(first(c,"location","position","locationName",default="") or "")
    zone=POSITION_MAP.get(loc.lower().strip(),"UNKNOWN")
    meta=str(first(c,"metaCode",default="") or "")
    sub=str(first(c,"subMetaCode",default="") or "")
    cat=category_code(c)
    berths=first(c,"numberOfBerths","noOfBerths","berths",default=None)
    try: berths=int(berths) if berths not in (None,"") else None
    except: berths=None
    area=first(c,"areaInSqft",default=None); balcony=first(c,"balconyAreaInSqft",default=None)
    try: area=float(area) if area not in (None,"") else None
    except: area=None
    try: balcony=float(balcony) if balcony not in (None,"") else None
    except: balcony=None
    bath=str(first(c,"bathType","bathShower",default="") or "")
    has_tub=True if "tub" in bath.lower() else (False if bath else None)
    has_shower=True if "shower" in bath.lower() else (False if bath else None)
    layout=first(c,"cabinLayout",default=None)
    deck_name=first(c,"deckName",default=None)
    deck_num=first(c,"deckNumber",default=deck_no)
    try: deck_num=int(deck_num)
    except: deck_num=None
    return {
      "provider":{"code":"PRINCESS","raw":{}},
      "ship":{"providerShipCode":ship,"name":None},
      "physicalConfiguration":{
        "configurationKey":f"PRINCESS:{ship}:DECKPLAN:{version}",
        "providerConfigurationId":str(version),"firstObservedSailingDate":None,"lastObservedSailingDate":None,
        "fingerprint":None,
        "evidence":[evidence(PROVENANCE["STRUCTURED"],"CONFIGURATION","Princess deck-plan version",version)]
      },
      "cabin":{
        "cabinNumber":no,
        "deck":{"providerCode":str(deck_no),"number":deck_num,"name":deck_name,"deckPlanUrl":None,
                "evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,{"deck":deck_no,"deckName":deck_name})]},
        "location":{"providerCode":None,"providerLabel":loc or None,"zone":zone,
                    "evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,loc)] if loc else []},
        "berths":fact(berths,[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,berths)] if berths is not None else []),
        "accessibility":normalize_access(c,source),
        "relationships":parse_connections(c,no,source),
        "area":{
          "providerAreaSqFt":number_fact(area,[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,area)] if area is not None else []),
          "interiorAreaSqFt":number_fact(None,[]),
          "outdoorAreaSqFt":number_fact(None,[]),
          "totalAreaSqFt":number_fact(None,[]),
          "providerSemantics":"Princess areaInSqft; semantics intentionally not promoted to interior/total"
        },
        "bath":{"providerType":bath or None,"hasTub":has_tub,"hasShower":has_shower,
                "evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,bath)] if bath else []},
        "providerLayoutVariant":{"code":str(layout) if layout not in (None,"") else None,"label":None,
                "evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,layout)] if layout not in (None,"") else []},
        "rawAttributes":c
      },
      "accommodationDefinition":{
        "providerTypeCode":meta or None,"providerTypeName":None,"providerSubtypeCode":sub or None,"providerSubtypeName":None,
        "physicalClass":PHYSICAL.get(meta,"UNKNOWN"),"roomType":None,"view":"UNKNOWN",
        "outdoorSpace":"BALCONY" if meta in ("B","M","S") else ("NONE" if meta=="I" else "UNKNOWN"),
        "obstruction":"UNKNOWN",
        "size":{"interiorSqFt":number_fact(None,[]),"outdoorSqFt":number_fact(None,[]),"totalSqFt":number_fact(None,[]),"providerText":None},
        "occupancy":{"min":fact(None,[]),"max":fact(None,[]),"providerText":None},
        "physicalFeatures":[],"providerDescription":[],"providerFeaturesRaw":[],"galleryRaw":[]
      },
      "serviceTier":{"canonicalTier":None,"providerCode":None,"providerName":None,"benefits":[]},
      "commercialCategory":{"providerCategoryCode":cat or None,"providerCategoryName":None,"providerMetaCode":meta or None,
          "providerSubMetaCode":sub or None,"guarantee":None,"firstObservedSailingDate":None,"lastObservedSailingDate":None,
          "hierarchyFingerprint":None,"raw":{}},
      "assignment":{"configurationKey":f"PRINCESS:{ship}:DECKPLAN:{version}","cabinNumber":no,
          "providerCategoryCode":cat or "UNKNOWN","firstObservedSailingDate":None,"lastObservedSailingDate":None,
          "sourceVoyageIds":[],"derivedCharacteristics":[],"evidence":[evidence(PROVENANCE["STRUCTURED"],"CABIN",source,cat)] if cat else []}
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input",required=True); ap.add_argument("--out",required=True)
    a=ap.parse_args(); inp=Path(a.input); out=Path(a.out); audit=load_audit(inp)
    result={"schemaVersion":"1.1","provider":"PRINCESS","ships":{}}
    for shipdir in sorted([p for p in inp.iterdir() if p.is_dir()]):
        ship=shipdir.name
        version=str(audit.get("ships",{}).get(ship,{}).get("deckPlanVersion","UNKNOWN"))
        records=[]
        for p in sorted(shipdir.glob("deck-*.json")):
            deck=re.search(r"deck-(.+)\.json$",p.name).group(1)
            try: obj=json.loads(p.read_text(encoding="utf-8"))
            except: continue
            cabins=obj.get("cabins",[]) if isinstance(obj,dict) else []
            for c in cabins:
                if isinstance(c,dict) and cabin_number(c):
                    records.append(normalize_cabin(ship,version,deck,c))
        # dedupe cabin number within config; flag conflicting duplicate payloads
        by={}; conflicts=[]
        for r in records:
            n=r["cabin"]["cabinNumber"]
            if n in by and stable_hash(by[n]["cabin"]["rawAttributes"]) != stable_hash(r["cabin"]["rawAttributes"]):
                conflicts.append(n)
            by[n]=r
        result["ships"][ship]={"configurationId":version,"cabinCount":len(by),"conflicts":sorted(set(conflicts)),
                               "records":[by[k] for k in sorted(by)]}
    dump_json(out,result)
    print(json.dumps({k:{"configurationId":v["configurationId"],"cabins":v["cabinCount"],"conflicts":len(v["conflicts"])}
                      for k,v in result["ships"].items()},indent=2))
if __name__=="__main__": main()
