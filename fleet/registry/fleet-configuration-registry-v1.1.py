#!/usr/bin/env python3
import argparse, json, hashlib
from pathlib import Path
from datetime import datetime, timezone

VERSION="1.1"

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def load(p):
    with open(p,"r",encoding="utf-8-sig") as f: return json.load(f)

def save(p,o):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    with open(p,"w",encoding="utf-8") as f:
        json.dump(o,f,indent=2,ensure_ascii=False); f.write("\n")

def survey_time(doc,path):
    for k in ("completedAt","generatedAt","surveyCompletedAt","surveyStartedAt","createdAt"):
        if doc.get(k): return doc[k]
    return datetime.fromtimestamp(Path(path).stat().st_mtime,timezone.utc).isoformat().replace("+00:00","Z")

def survey_id(doc,path,ts):
    material={"path":Path(path).name,"timestamp":ts,
              "surveyStart":doc.get("surveyStart") or doc.get("surveyStartDate"),
              "version":doc.get("version")}
    return hashlib.sha256(json.dumps(material,sort_keys=True).encode()).hexdigest()[:20]

def normalize(o,provider,sid,sts,source):
    x=dict(o)
    x.setdefault("provider",provider)
    x["sourceSurveyId"]=sid
    x["sourceSurveyTimestamp"]=sts
    x["sourceSurveyFile"]=Path(source).name
    x["observedAt"]=x.get("observedAt") or sts
    original=x.get("status") or x.get("probeStatus")
    x["sourceStatus"]=original
    cfg=x.get("physicalConfigurationId") or x.get("configurationId")
    x["physicalConfigurationId"]=cfg
    if cfg:
        x["probeStatus"]="SUCCESS"; x["physicalConfigurationStatus"]="OBSERVED"
    elif original in ("UNRESOLVED_NO_INVENTORY","NO_ROOM_FOUND"):
        x["probeStatus"]="SUCCESS"; x["physicalConfigurationStatus"]="UNOBSERVABLE_NO_INVENTORY"
    elif original in ("UNRESOLVED_PROVIDER_ERROR","PROVIDER_ERROR"):
        x["probeStatus"]="ERROR"; x["physicalConfigurationStatus"]="UNOBSERVABLE_PROVIDER_ERROR"
    elif original=="UNRESOLVED_NO_PHYSICAL_EVIDENCE":
        x["probeStatus"]="SUCCESS"; x["physicalConfigurationStatus"]="UNOBSERVABLE_NO_PHYSICAL_EVIDENCE"
    else:
        x["probeStatus"]="ERROR"; x["physicalConfigurationStatus"]="UNOBSERVABLE_ERROR"
    if cfg:
        evidence=x.get("physicalConfigurationEvidence") or x.get("physicalEvidence") or x.get("evidence")
        material={"provider":x.get("provider"),"voyageId":x.get("voyageId"),
                  "sailDate":x.get("sailDate"),"physicalConfigurationId":cfg,
                  "evidence":evidence}
        x["evidenceHash"]=hashlib.sha256(json.dumps(material,sort_keys=True,separators=(",",":")).encode()).hexdigest()
    return x

def extract(doc,path):
    provider=(doc.get("provider") or "CELEBRITY").upper()
    ts=survey_time(doc,path); sid=survey_id(doc,path,ts)
    arr=doc.get("observations") or doc.get("probes")
    if arr is None: raise ValueError(f"No observations/probes in {path}")
    return [normalize(o,provider,sid,ts,path) for o in arr], {
        "surveyId":sid,"timestamp":ts,"sourceFile":Path(path).name,
        "provider":provider,"observationCount":len(arr),
        "surveyStart":doc.get("surveyStart") or doc.get("surveyStartDate")
    }

def unique_key(o):
    # Same survey + voyage is one immutable observation; different surveys remain history.
    return "|".join(str(o.get(k,"")) for k in ("sourceSurveyId","provider","voyageId","sailDate"))

def rebuild(reg):
    voyages={}
    for o in sorted(reg["observations"],key=lambda x:(x.get("observedAt") or "",x.get("sourceSurveyId") or "")):
        vid=o.get("voyageId")
        if not vid: continue
        v=voyages.setdefault(vid,{"provider":o.get("provider"),"voyageId":vid,
            "sailDate":o.get("sailDate"),"shipCode":o.get("shipCode"),
            "physicalConfigurationId":None,"configurationEvidenceState":"UNPROVEN",
            "provenEvidenceHashes":[],"latestObservation":None})
        v["latestObservation"]={"observedAt":o.get("observedAt"),
            "sourceSurveyId":o.get("sourceSurveyId"),"probeStatus":o.get("probeStatus"),
            "physicalConfigurationStatus":o.get("physicalConfigurationStatus")}
        if o.get("evidenceHash") and o["evidenceHash"] not in v["provenEvidenceHashes"]:
            v["provenEvidenceHashes"].append(o["evidenceHash"])
    conflicts=[]
    for vid,v in voyages.items():
        cfgs=sorted({str(o["physicalConfigurationId"]) for o in reg["observations"]
                     if o.get("voyageId")==vid and o.get("physicalConfigurationId")})
        if len(cfgs)==1:
            v["physicalConfigurationId"]=cfgs[0]; v["configurationEvidenceState"]="PROVEN_TARGET_SAILING"
        elif len(cfgs)>1:
            v["configurationEvidenceState"]="CONFLICT"
            conflicts.append({"voyageId":vid,"configurationIds":cfgs})
    reg["voyages"]=voyages; reg["conflicts"]=conflicts
    reg["statistics"]={"observationCount":len(reg["observations"]),"voyageCount":len(voyages),
      "provenVoyageCount":sum(v["configurationEvidenceState"]=="PROVEN_TARGET_SAILING" for v in voyages.values()),
      "currentlyUnobservableButPreviouslyProvenCount":sum(
          v["configurationEvidenceState"]=="PROVEN_TARGET_SAILING" and
          (v.get("latestObservation",{}).get("physicalConfigurationStatus") or "").startswith("UNOBSERVABLE")
          for v in voyages.values()),
      "conflictCount":len(conflicts),"surveyCount":len(reg["surveys"])}
    return reg

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True)
    ap.add_argument("--survey",action="append",required=True)
    a=ap.parse_args()
    rp=Path(a.registry)
    if rp.exists():
        reg=load(rp)
        reg["version"]=VERSION
        reg.setdefault("surveys",[])
        reg.setdefault("observations",[])
    else:
        reg={"version":VERSION,"kind":"FLEET_PHYSICAL_CONFIGURATION_EVIDENCE_REGISTRY",
             "createdAt":now(),"updatedAt":None,"surveys":[],"observations":[],"voyages":{},"conflicts":[]}
    keys={unique_key(o) for o in reg["observations"] if o.get("sourceSurveyId")}
    survey_ids={s.get("surveyId") for s in reg["surveys"]}
    for path in a.survey:
        observations,meta=extract(load(path),path)
        if meta["surveyId"] not in survey_ids:
            reg["surveys"].append(meta); survey_ids.add(meta["surveyId"])
        for o in observations:
            k=unique_key(o)
            if k not in keys:
                reg["observations"].append(o); keys.add(k)
    rebuild(reg); reg["updatedAt"]=now(); save(rp,reg)
    print(json.dumps(reg["statistics"],indent=2))
    if reg["conflicts"]: raise SystemExit("Configuration evidence conflicts detected.")

if __name__=="__main__": main()
