#!/usr/bin/env python3
"""
Princess fleet configuration timeline PRE-FLIGHT v1.0.

Important design constraint:
The public deckPlans.do page exposes a ship/version signal, but our current evidence
does NOT establish that querying the page today yields the layout version applicable
to an arbitrary future voyage. Therefore this script deliberately does NOT assign that
version to every future sailing.

It performs the safe pieces now:
- future-only voyage enumeration
- ship inventory
- current public deck-plan version discovery per ship
- category hierarchy signature for that discovered version across its decks, when possible
- emits unresolved voyage->configuration bindings rather than inventing them

The resulting artifact tells us exactly which missing provider contract must be discovered
before Princess sailing-era boundaries can be asserted.
"""
from pathlib import Path
from datetime import date
import argparse,json,re,requests,urllib.parse,xml.etree.ElementTree as ET
from timeline_common import *

BASE="https://www.princess.com"
PAGE=BASE+"/deckPlans.do"

def ship_code(v):
    value=first(v,"shipCode","ship","providerShipCode",default="")
    if isinstance(value,dict):
        value=first(value,"providerId","shipCode","code","id",default="")
    return str(value or "")

def voyage_id(v):
    return str(first(v,"providerId","voyageId","id",default=""))

def page_version(html):
    pats=[r'filter\.version\s*=\s*["\']?(\d+)',r'version["\']?\s*[:=]\s*["\']?(\d+)']
    for p in pats:
        m=re.search(p,html,re.I)
        if m: return m.group(1)
    return None

def deck_candidates(html):
    vals=set(re.findall(r'(?:deck|deckNumber)["\']?\s*[:=]\s*["\']?([0-9]{1,2})',html,re.I))
    # conservative standard deck range fallback is NOT used; unknown remains unknown
    return sorted(vals,key=lambda x:int(x))

def category_entries(session,ship,version,decks):
    entries=[]
    for deck in decks:
        u=BASE+"/getCategories.do"
        r=session.get(u,params={"shipCode":ship,"version":version,"deck":deck},timeout=30)
        if not r.ok: continue
        try: obj=r.json()
        except: continue
        candidates=obj if isinstance(obj,list) else obj.get("categories",[]) if isinstance(obj,dict) else []
        for c in candidates:
            if not isinstance(c,dict): continue
            entries.append({"typeCode":str(first(c,"metaCode",default="") or ""),
                            "subtypeCode":str(first(c,"subMetaCode",default="") or ""),
                            "categoryCode":str(first(c,"categoryCode","code",default="") or "")})
    return entries

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--voyages",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--survey-start",default=str(date.today()))
    a=ap.parse_args(); start=parse_date(a.survey_start)
    obj=load_json(a.voyages); voyages=obj if isinstance(obj,list) else first(obj,"voyages","items",default=[])
    fv=future_voyages(voyages,start)
    ships=sorted(set(ship_code(v) for v in fv if ship_code(v)))
    ses=requests.Session()
    ship_inventory={}
    for ship in ships:
        rec={"shipCode":ship,"status":"FAILURE"}
        try:
            r=ses.get(PAGE,params={"shipCode":ship},timeout=30); r.raise_for_status()
            ver=page_version(r.text); decks=deck_candidates(r.text)
            entries=category_entries(ses,ship,ver,decks) if ver and decks else []
            rec={"shipCode":ship,"status":"SUCCESS","currentlyPublishedDeckPlanVersion":ver,
                 "deckCandidatesFromPage":decks,
                 "commercialHierarchySignatureForPublishedVersion":build_signature(entries) if entries else None,
                 "warning":"Current published deck-plan version is NOT assigned to arbitrary future voyages."}
        except Exception as e:
            rec["error"]=repr(e)
        ship_inventory[ship]=rec
        print(ship,rec["status"],rec.get("currentlyPublishedDeckPlanVersion"))
    observations=[]
    for v in fv:
        observations.append({"provider":"PRINCESS","voyageId":voyage_id(v),"shipCode":ship_code(v),
          "sailDate":sailing_date(v),"status":"UNRESOLVED",
          "physicalConfigurationId":None,"commercialHierarchySignature":None,
          "reason":"Voyage-specific Princess deck-plan version binding not yet proven."})
    result={"schemaVersion":"1.0","provider":"PRINCESS","surveyStartDate":str(start),
      "eligibilityRule":"sailDate > surveyStartDate","shipPublishedVersionInventory":ship_inventory,
      "observations":observations,"observedEras":[],"transitions":[],
      "notes":["Fail-closed by design: current ship deck-plan version is not projected onto future voyages.",
               "Next Princess discovery target is the voyage-specific binding between sailing and deck-plan version."]}
    dump_json(a.out,result)

if __name__=="__main__": main()
