#!/usr/bin/env python3
import argparse, hashlib, json
from pathlib import Path
from datetime import datetime, timezone

VERSION="1.2"
KIND="FLEET_PHYSICAL_CONFIGURATION_EVIDENCE_REGISTRY"

def now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00","Z")

def load(path):
    with open(path,"r",encoding="utf-8-sig") as f:
        return json.load(f)

def save(path,obj):
    Path(path).parent.mkdir(parents=True,exist_ok=True)
    with open(path,"w",encoding="utf-8") as f:
        json.dump(obj,f,indent=2,ensure_ascii=False)
        f.write("\n")

def sha256_file(path):
    h=hashlib.sha256()
    size=0
    with open(path,"rb") as f:
        while True:
            b=f.read(1024*1024)
            if not b: break
            size += len(b); h.update(b)
    return h.hexdigest(), size

def canonical_hash(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    ).hexdigest()

def normalize_status(x):
    original=x.get("status") or x.get("probeStatus")
    cfg=x.get("physicalConfigurationId") or x.get("configurationId")
    x["sourceStatus"]=original
    x["physicalConfigurationId"]=cfg
    if cfg:
        x["probeStatus"]="SUCCESS"
        x["physicalConfigurationStatus"]="OBSERVED"
    elif original in ("UNRESOLVED_NO_INVENTORY","NO_ROOM_FOUND"):
        x["probeStatus"]="SUCCESS"
        x["physicalConfigurationStatus"]="UNOBSERVABLE_NO_INVENTORY"
    elif original in ("UNRESOLVED_PROVIDER_ERROR","PROVIDER_ERROR"):
        x["probeStatus"]="ERROR"
        x["physicalConfigurationStatus"]="UNOBSERVABLE_PROVIDER_ERROR"
    elif original=="UNRESOLVED_NO_PHYSICAL_EVIDENCE":
        x["probeStatus"]="SUCCESS"
        x["physicalConfigurationStatus"]="UNOBSERVABLE_NO_PHYSICAL_EVIDENCE"
    else:
        x["probeStatus"]="ERROR"
        x["physicalConfigurationStatus"]="UNOBSERVABLE_ERROR"
    return cfg

def extract(path, imported_at):
    path=Path(path)
    raw_hash, byte_length=sha256_file(path)
    source_survey_id="sha256:"+raw_hash
    doc=load(path)
    provider=(doc.get("provider") or "CELEBRITY").upper()
    arr=doc.get("observations")
    if arr is None:
        arr=doc.get("probes")
    if arr is None:
        raise ValueError(f"No observations/probes in {path}")

    source_generated_at=None
    for key in ("generatedAt","completedAt","surveyCompletedAt","surveyStartedAt","createdAt"):
        if doc.get(key):
            source_generated_at=doc[key]
            break

    survey_start=doc.get("surveyStartDate") or doc.get("surveyStart")
    meta={
        "sourceSurveyId":source_survey_id,
        "provider":provider,
        "surveyStartDate":survey_start,
        "schemaVersion":doc.get("schemaVersion") or doc.get("version"),
        "sourceFileDisplayName":path.name,
        "sourceByteLength":byte_length,
        "sourceSha256":raw_hash,
        "observationCount":len(arr),
        "importedAt":imported_at
    }
    if source_generated_at:
        meta["sourceGeneratedAt"]=source_generated_at

    observations=[]
    for ordinal,o in enumerate(arr):
        x=dict(o)
        x.setdefault("provider",provider)
        x["sourceSurveyId"]=source_survey_id
        x["sourceSurveyOrdinal"]=ordinal
        # Preserve a genuine observation timestamp only if the source supplied it.
        # Never synthesize observedAt from file mtime, import time, or survey metadata.
        cfg=normalize_status(x)
        if cfg:
            evidence=x.get("physicalConfigurationEvidence") or x.get("physicalEvidence") or x.get("evidence")
            material={
                "provider":x.get("provider"),
                "voyageId":x.get("voyageId"),
                "sailDate":x.get("sailDate"),
                "physicalConfigurationId":cfg,
                "evidence":evidence
            }
            x["evidenceHash"]=canonical_hash(material)
        observations.append(x)
    return observations,meta

def observation_key(o):
    # Ordinal is intentionally part of identity: if a source survey contains two
    # observations for the same voyage, both immutable source records survive.
    return "|".join([
        str(o.get("sourceSurveyId","")),
        str(o.get("provider","")),
        str(o.get("voyageId","")),
        str(o.get("sourceSurveyOrdinal",""))
    ])

def rebuild(reg):
    survey_by_id={s["sourceSurveyId"]:s for s in reg["surveys"]}
    voyages={}
    for o in reg["observations"]:
        vid=o.get("voyageId")
        if not vid: continue
        key=f'{o.get("provider","")}|{vid}'
        v=voyages.setdefault(key,{
            "provider":o.get("provider"),
            "voyageId":vid,
            "sailDate":o.get("sailDate"),
            "shipCode":o.get("shipCode"),
            "physicalConfigurationId":None,
            "configurationEvidenceState":"UNPROVEN",
            "provenEvidenceHashes":[],
            "mostRecentlyImportedObservation":None,
            "latestSurveyObservation":None
        })
        if o.get("evidenceHash") and o["evidenceHash"] not in v["provenEvidenceHashes"]:
            v["provenEvidenceHashes"].append(o["evidenceHash"])

        survey=survey_by_id.get(o.get("sourceSurveyId"),{})
        candidate={
            "sourceSurveyId":o.get("sourceSurveyId"),
            "sourceSurveyOrdinal":o.get("sourceSurveyOrdinal"),
            "surveyStartDate":survey.get("surveyStartDate"),
            "importedAt":survey.get("importedAt"),
            "probeStatus":o.get("probeStatus"),
            "physicalConfigurationStatus":o.get("physicalConfigurationStatus")
        }
        current=v.get("mostRecentlyImportedObservation")
        cand_key=(candidate.get("importedAt") or "", candidate.get("sourceSurveyId") or "",
                  int(candidate.get("sourceSurveyOrdinal") or 0))
        cur_key=((current or {}).get("importedAt") or "", (current or {}).get("sourceSurveyId") or "",
                 int((current or {}).get("sourceSurveyOrdinal") or 0))
        if current is None or cand_key > cur_key:
            v["mostRecentlyImportedObservation"]=candidate

        latest=v.get("latestSurveyObservation")
        cand_survey_key=(candidate.get("surveyStartDate") or "", candidate.get("sourceSurveyId") or "",
                         int(candidate.get("sourceSurveyOrdinal") or 0))
        latest_survey_key=((latest or {}).get("surveyStartDate") or "", (latest or {}).get("sourceSurveyId") or "",
                           int((latest or {}).get("sourceSurveyOrdinal") or 0))
        if latest is None or cand_survey_key > latest_survey_key:
            v["latestSurveyObservation"]=candidate

    conflicts=[]
    for key,v in voyages.items():
        cfgs=sorted({
            str(o["physicalConfigurationId"]) for o in reg["observations"]
            if o.get("provider")==v["provider"] and o.get("voyageId")==v["voyageId"]
            and o.get("physicalConfigurationId")
        })
        if len(cfgs)==1:
            v["physicalConfigurationId"]=cfgs[0]
            v["configurationEvidenceState"]="PROVEN_TARGET_SAILING"
        elif len(cfgs)>1:
            v["configurationEvidenceState"]="CONFLICT"
            conflicts.append({
                "provider":v["provider"],
                "voyageId":v["voyageId"],
                "configurationIds":cfgs
            })

    proven=sum(v["configurationEvidenceState"]=="PROVEN_TARGET_SAILING" for v in voyages.values())
    unproven=sum(v["configurationEvidenceState"]=="UNPROVEN" for v in voyages.values())
    reg["voyages"]=voyages
    reg["conflicts"]=conflicts
    reg["statistics"]={
        "observationCount":len(reg["observations"]),
        "voyageCount":len(voyages),
        "provenVoyageCount":proven,
        "unprovenVoyageCount":unproven,
        "currentlyUnobservableButPreviouslyProvenCount":sum(
            v["configurationEvidenceState"]=="PROVEN_TARGET_SAILING" and
            ((v.get("latestSurveyObservation") or {}).get("physicalConfigurationStatus") or "").startswith("UNOBSERVABLE")
            for v in voyages.values()
        ),
        "conflictCount":len(conflicts),
        "surveyCount":len(reg["surveys"])
    }
    return reg

def new_registry():
    return {
        "version":VERSION,
        "kind":KIND,
        "createdAt":now(),
        "updatedAt":None,
        "surveys":[],
        "observations":[],
        "voyages":{},
        "conflicts":[],
        "statistics":{}
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",required=True)
    ap.add_argument("--survey",action="append",required=True)
    a=ap.parse_args()

    rp=Path(a.registry)
    if rp.exists():
        reg=load(rp)
        if reg.get("version") != VERSION:
            raise SystemExit(
                f"Registry {rp} is version {reg.get('version')}; V1.2 does not perform "
                "lossy in-place migration. Rebuild V1.2 from original survey files."
            )
    else:
        reg=new_registry()

    existing_surveys={s.get("sourceSurveyId") for s in reg["surveys"]}
    existing_obs={observation_key(o) for o in reg["observations"]}

    for survey_path in a.survey:
        # importedAt is assigned only if this exact raw-byte survey is new.
        raw_hash,_=sha256_file(survey_path)
        sid="sha256:"+raw_hash
        if sid in existing_surveys:
            continue
        imported_at=now()
        observations,meta=extract(survey_path,imported_at)
        reg["surveys"].append(meta)
        existing_surveys.add(sid)
        for o in observations:
            k=observation_key(o)
            if k not in existing_obs:
                reg["observations"].append(o)
                existing_obs.add(k)

    rebuild(reg)
    reg["updatedAt"]=now()
    save(rp,reg)
    print(json.dumps(reg["statistics"],indent=2))
    if reg["conflicts"]:
        raise SystemExit("Configuration evidence conflicts detected.")

if __name__=="__main__":
    main()
