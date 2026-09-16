#!/usr/bin/env python3
"""
Celebrity fleet configuration + commercial hierarchy survey v1.0.

Uses public room-selection endpoints. Requires curl_cffi because ordinary clients may
receive Akamai 403 responses.

Per probe:
1) type-and-subtype RSC => commercial hierarchy tuples
2) room-location RSC for one viable subtype/category => deckPlanUrl => layout token
No cabin saturation and no checkout/pricing.

The survey is future-only: sailDate > surveyStartDate.
"""
from pathlib import Path
from datetime import date
import argparse, json, re, time, urllib.parse
from timeline_common import *
from curl_cffi import requests

BASE="https://www.celebritycruises.com"
ROOMS_URL=BASE+"/room-selection/api/v1/rooms"
TRANSIENT={429,500,502,503,504}
TOKEN_RE=re.compile(r'/svg_c_([A-Za-z0-9]+)_([0-9]+)/')

def voyage_id(v):
    return str(first(v,"providerId","groupId","voyageId","id",default=""))

def ship_code(v):
    value=first(v,"shipCode","ship","providerShipCode",default="")
    # Canonical voyage V3.1 may store ship as an object:
    # {"providerId":"AT","name":"Celebrity Ascent"}.
    if isinstance(value,dict):
        value=first(value,"providerId","shipCode","code","id",default="")
    return str(value or "")

def package_code(v):
    value=first(v,"packageCode","packageId",default=None)
    if value:
        return value
    src=v.get("source") if isinstance(v.get("source"),dict) else {}
    # Canonical voyage V3.1 preserves Celebrity's package/itinerary code here.
    return first(src,"providerItineraryCode","packageCode","providerProductId",default=None)

def group_id(v):
    src=v.get("source") if isinstance(v.get("source"),dict) else {}
    return first(v,"groupId",default=None) or first(src,"providerGroupId",default=None)

def walk_values(obj,path="$"):
    if isinstance(obj,dict):
        for k,v in obj.items():
            p=f"{path}.{k}"
            yield p,k,v
            yield from walk_values(v,p)
    elif isinstance(obj,list):
        for i,v in enumerate(obj):
            yield from walk_values(v,f"{path}[{i}]")

def common_filter(v):
    return {"countryCode":"CAN","packageId":str(package_code(v) or ""),
            "sailDate":str(sailing_date(v) or ""),"currencyCode":"CAD",
            "language":"en","platform":"web"}

def api_get(session,filt,label,max_attempts=3):
    url=ROOMS_URL+"?"+urllib.parse.urlencode({"filter":json.dumps(filt,separators=(",",":"))})
    last=None
    for attempt in range(1,max_attempts+1):
        try:
            r=session.get(url,headers={"accept":"application/json, text/plain, */*",
                "referer":BASE+"/room-selection/","origin":BASE},timeout=45)
            rec={"label":label,"attempt":attempt,"status":r.status_code,"requestUrl":url}
            try: rec["json"]=r.json()
            except Exception: rec["bodyExcerpt"]=(r.text or "")[:1200].replace("\r"," ").replace("\n"," ")
            last=rec
            if r.status_code not in TRANSIENT: return rec
        except Exception as e:
            last={"label":label,"attempt":attempt,"exception":repr(e),"requestUrl":url}
        if attempt<max_attempts: time.sleep((2,5)[min(attempt-1,1)])
    return last

def room0(js):
    rooms=(js or {}).get("rooms") or []
    return rooms[0] if rooms else {}

def no_room_found(js):
    r=room0(js)
    if r.get("outcome")=="NO_ROOM_FOUND": return True
    return any(a.get("code")=="NO_ROOM_FOUND" for a in (r.get("advisories") or []) if isinstance(a,dict))

def hierarchy_from_json(js):
    entries=[]; viable=[]
    types=((room0(js).get("options") or {}).get("stateroomTypes") or [])
    for t in types:
        tc=str(t.get("code") or "")
        for sub in t.get("stateroomSubtypes") or []:
            sc=str(sub.get("code") or ""); cc=str(sub.get("categoryCode") or "")
            if not sc: continue
            e={"typeCode":tc,"subtypeCode":sc,"categoryCode":cc}
            entries.append(e)
            viable.append((tc,sc,cc,sub.get("roomsLeft"),bool(sub.get("guarantee"))))
    uniq={(e["typeCode"],e["subtypeCode"],e["categoryCode"]):e for e in entries}
    # Positive inventory + non-guarantee first; then all other advertised choices.
    viable.sort(key=lambda x:(0 if isinstance(x[3],(int,float)) and x[3]>0 and not x[4] else 1 if not x[4] else 2,
                              x[0],x[1],x[2]))
    return list(uniq.values()),viable

def token_evidence(js):
    found=[]
    for path,k,v in walk_values(js):
        if k=="deckPlanUrl" and isinstance(v,str):
            m=TOKEN_RE.search(v)
            if m: found.append((m.group(2),v,path,m.group(1)))
    if not found: return None,None,[]
    ids=sorted(set(x[0] for x in found))
    if len(ids)!=1:
        raise RuntimeError(f"Conflicting Celebrity physical layout tokens in one target response: {ids}")
    return ids[0],found[0][1],[{"physicalConfigurationId":x[0],"deckPlanUrl":x[1],"path":x[2],"shipCode":x[3]} for x in found]

def probe(session,v):
    request_count=0
    f=common_filter(v)
    f.update({"options":True,"roomNumbers":False,"rooms":[{
        "adultCount":2,"childCount":0,"accessible":False,
        "selectionFallbackStrategy":"RECOMMENDATION","editMode":True,
        "reset":False,"taxesAndFeesBundled":True}]})
    rr=api_get(session,f,"options-only"); request_count += int(rr.get("attempt",1) or 1)
    status=rr.get("status")
    if status!=200:
        raise ProbeFailure("UNRESOLVED_PROVIDER_ERROR",
            f"Celebrity rooms API persistent HTTP {status}; attempts={rr.get('attempt')} url={rr.get('requestUrl')}",request_count)
    js=rr.get("json") or {}
    if no_room_found(js):
        raise ProbeFailure("UNRESOLVED_NO_INVENTORY","Celebrity returned NO_ROOM_FOUND for 2 adults",request_count)
    entries,viable=hierarchy_from_json(js)
    if not viable:
        raise ProbeFailure("UNRESOLVED_NO_INVENTORY","Celebrity returned no advertised room options for 2 adults",request_count)
    offer_sig=build_signature(entries)

    # JSON-only physical discovery. A deliberately low deck code is useful because Celebrity
    # can return FALLBACK_DECK plus the actual selected/available decks. Try only a small,
    # bounded set of viable selectors; never brute-force the ship.
    attempts=[]
    for typ,sub,cat,rooms_left,guarantee in viable[:4]:
        for deck in ("02","07"):
            q=common_filter(v)
            q.update({"options":True,"roomNumbers":True,"rooms":[{
                "adultCount":2,"childCount":0,"stateroomTypeCode":typ,
                "stateroomSubtypeCode":sub,"accessible":False,
                "selectionFallbackStrategy":"RECOMMENDATION","editMode":True,
                "reset":False,"taxesAndFeesBundled":True,"room":{"deckCode":deck}}]})
            x=api_get(session,q,f"{typ}/{sub}:deck-{deck}"); request_count += int(x.get("attempt",1) or 1)
            xjs=x.get("json") or {}
            attempts.append({"typeCode":typ,"subtypeCode":sub,"categoryCode":cat,
                             "requestedDeckCode":deck,"status":x.get("status")})
            if x.get("status")!=200:
                if x.get("status") in TRANSIENT:
                    continue
                continue
            token,url,evidence=token_evidence(xjs)
            if token:
                return token,url,offer_sig,len(viable),request_count,evidence,attempts
            if no_room_found(xjs):
                # This selector has no inventory; try the next advertised selector, but there
                # is no value trying more deck codes for it.
                break
    raise ProbeFailure("UNRESOLVED_NO_PHYSICAL_EVIDENCE",
        f"No target-sailing deckPlanUrl after bounded JSON probes; advertisedOptions={len(viable)}",request_count)

class ProbeFailure(RuntimeError):
    def __init__(self,classification,message,request_count):
        super().__init__(message); self.classification=classification; self.request_count=request_count

def select_stride(vs,stride):
    if len(vs)<=2: return vs
    idx={0,len(vs)-1}
    idx.update(range(0,len(vs),max(1,stride)))
    return [vs[i] for i in sorted(idx)]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--voyages",required=True); ap.add_argument("--out",required=True)
    ap.add_argument("--survey-start",default=str(date.today()))
    ap.add_argument("--mode",choices=["stride","all"],default="stride")
    ap.add_argument("--stride",type=int,default=6); ap.add_argument("--sleep",type=float,default=.15)
    ap.add_argument("--max-probes",type=int,default=0,
                    help="Diagnostic limit; 0 means no limit.")
    a=ap.parse_args()
    obj=load_json(a.voyages)
    voyages=obj if isinstance(obj,list) else first(obj,"voyages","items",default=[])
    start=parse_date(a.survey_start)
    fv=future_voyages(voyages,start)
    by={}
    for v in fv: by.setdefault(ship_code(v),[]).append(v)
    selected=[]
    for ship,vs in by.items():
        selected += vs if a.mode=="all" else select_stride(vs,a.stride)
    selected=sorted(selected,key=lambda x:(ship_code(x),sailing_date(x) or ""))
    if a.max_probes and a.max_probes > 0:
        selected=selected[:a.max_probes]
    ses=requests.Session(impersonate="chrome")
    obs=[]
    for i,v in enumerate(selected,1):
        rec={"provider":"CELEBRITY","voyageId":voyage_id(v),"shipCode":ship_code(v),
             "sailDate":sailing_date(v),"status":"FAILURE"}
        try:
            ship=ship_code(v)
            token,url,offer_sig,viable_count,request_count,evidence,attempts=probe(ses,v)
            rec.update({"status":"SUCCESS","physicalConfigurationId":token,
                        "physicalConfigurationEvidence":{"deckPlanUrl":url,"allDeckPlanEvidence":evidence},
                        "commercialSchemaId":None,"commercialOfferSignature":offer_sig,
                        "currentOfferTupleCount":viable_count,"requestCount":request_count,
                        "physicalProbeAttempts":attempts})
        except ProbeFailure as e:
            rec.update({"status":e.classification,"error":str(e),"requestCount":e.request_count})
        except Exception as e:
            rec.update({"status":"UNRESOLVED_ERROR","error":repr(e)})
        obs.append(rec)
        line=(f"[{i}/{len(selected)}] {rec['shipCode']} {rec['sailDate']} {rec['status']} "
              f"{rec.get('physicalConfigurationId','')}")
        print(line, flush=True)
        if rec["status"] != "SUCCESS":
            print(f"    ERROR: {rec.get('error','unknown')}", flush=True)
            print(f"    voyageId={rec.get('voyageId')} packageCode={package_code(v)!r} "
                  f"groupId={group_id(v)!r} requestCount={rec.get('requestCount')}", flush=True)
        # Write a partial diagnostic file after every probe so failures can be inspected
        # without waiting for the whole fleet run.
        partial={"schemaVersion":"1.0","provider":"CELEBRITY","surveyStartDate":str(start),
                 "eligibilityRule":"sailDate > surveyStartDate","observations":obs}
        dump_json(str(a.out)+".partial.json", partial)
        time.sleep(a.sleep)
    result={"schemaVersion":"1.0","provider":"CELEBRITY","surveyStartDate":str(start),
      "eligibilityRule":"sailDate > surveyStartDate","observations":obs,
      "observedEras":observed_eras(obs),"transitions":transition_records(obs),
      "notes":["Celebrity discovery is JSON-only via /room-selection/api/v1/rooms; RSC endpoints are not used.",
               "NO_ROOM_FOUND is recorded as UNRESOLVED_NO_INVENTORY and is retryable on a later survey.",
               "Persistent provider HTTP failures are recorded as UNRESOLVED_PROVIDER_ERROR.",
               "No configuration is inferred from adjacent sailings or same-ship cached selectors.",
               "Observed bounds are not asserted effective dates.",
               "Physical configuration transitions are detected only from physicalConfigurationId.",
               "commercialOfferSignature is sailing/observation-level and is excluded from configuration-era detection.",
               "commercialSchemaId remains null until a stable complete Celebrity taxonomy source is proven."]}
    dump_json(a.out,result)

if __name__=="__main__": main()
