#!/usr/bin/env python3
import hashlib,json,subprocess,sys,tempfile
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; REG=ROOT/"fleet/registry/fleet-configuration-registry-v1.2.py"; ARCH=ROOT/"fleet/registry/archive-and-import-survey-v1.0.py"
def write(p,date,status,cfg=None):
 o={"provider":"CELEBRITY","voyageId":"BY06E036_2027-07-25","shipCode":"BY","sailDate":"2027-07-25","status":status}
 if cfg:o["physicalConfigurationId"]=cfg
 p.write_text(json.dumps({"schemaVersion":"1.0","provider":"CELEBRITY","surveyStartDate":date,"observations":[o]},indent=2))
def imp(reg,s): subprocess.run([sys.executable,str(REG),"--registry",str(reg),"--survey",str(s)],check=True,capture_output=True,text=True)
with tempfile.TemporaryDirectory() as td:
 d=Path(td); reg=d/"r.json"; newer=d/"new.json"; older=d/"old.json"
 write(newer,"2026-09-16","UNRESOLVED_PROVIDER_ERROR"); write(older,"2026-09-15","SUCCESS","2451")
 imp(reg,newer); imp(reg,older); r=json.loads(reg.read_text()); v=r["voyages"]["CELEBRITY|BY06E036_2027-07-25"]
 assert v["physicalConfigurationId"]=="2451" and v["configurationEvidenceState"]=="PROVEN_TARGET_SAILING"
 assert v["latestSurveyObservation"]["surveyStartDate"]=="2026-09-16"
 assert v["latestSurveyObservation"]["physicalConfigurationStatus"]=="UNOBSERVABLE_PROVIDER_ERROR"
 assert v["mostRecentlyImportedObservation"]["surveyStartDate"]=="2026-09-15"
 assert r["statistics"]["currentlyUnobservableButPreviouslyProvenCount"]==1
 reg2=d/"r2.json"; arc=d/"arc"
 for _ in range(2): subprocess.run([sys.executable,str(ARCH),"--survey",str(older),"--archive-dir",str(arc),"--registry",str(reg2),"--registry-tool",str(REG)],check=True,capture_output=True,text=True)
 rr=json.loads(reg2.read_text()); dg=hashlib.sha256(older.read_bytes()).hexdigest()
 assert (arc/f"sha256-{dg}.json").read_bytes()==older.read_bytes()
 assert rr["statistics"]["surveyCount"]==1 and rr["statistics"]["observationCount"]==1
print("Registry V1.2 chronology + immutable archive tests: PASS")
