#!/usr/bin/env python3
import hashlib, json, os, shutil, subprocess, sys, tempfile, time
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
TOOL=ROOT/"fleet/registry/fleet-configuration-registry-v1.2.py"

def run(reg,*surveys):
    cmd=[sys.executable,str(TOOL),"--registry",str(reg)]
    for s in surveys: cmd += ["--survey",str(s)]
    subprocess.run(cmd,check=True,capture_output=True,text=True)

def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))

with tempfile.TemporaryDirectory() as td:
    d=Path(td)
    survey=d/"survey-original.json"
    survey.write_text(json.dumps({
      "schemaVersion":"1.0","provider":"CELEBRITY","surveyStartDate":"2026-09-16",
      "observations":[
        {"voyageId":"A","sailDate":"2027-01-01","shipCode":"XC","status":"SUCCESS",
         "physicalConfigurationId":"2331","physicalConfigurationEvidence":{"deckPlanUrl":"https://example/2331"}},
        {"voyageId":"B","sailDate":"2027-01-02","shipCode":"FL","status":"UNRESOLVED_NO_INVENTORY"}
      ]
    },indent=2),encoding="utf-8")
    original_bytes=survey.read_bytes()
    expected_sid="sha256:"+hashlib.sha256(original_bytes).hexdigest()

    reg=d/"registry.json"
    run(reg,survey)
    a=load(reg)
    assert a["version"]=="1.2"
    assert a["surveys"][0]["sourceSurveyId"]==expected_sid
    assert a["statistics"]["observationCount"]==2
    assert a["statistics"]["voyageCount"]==2
    assert a["statistics"]["provenVoyageCount"]==1
    assert a["statistics"]["unprovenVoyageCount"]==1
    assert all("observedAt" not in o for o in a["observations"])
    imported=a["surveys"][0]["importedAt"]

    # Same raw bytes under a different name must be a no-op.
    copy=d/"renamed-copy.json"; shutil.copyfile(survey,copy)
    run(reg,copy)
    b=load(reg)
    assert b["statistics"]["surveyCount"]==1
    assert b["statistics"]["observationCount"]==2
    assert b["surveys"][0]["importedAt"]==imported

    # Touching the file must not change identity.
    time.sleep(0.02); os.utime(copy,None)
    run(reg,copy)
    c=load(reg)
    assert c["statistics"]["surveyCount"]==1
    assert c["statistics"]["observationCount"]==2
    assert c["surveys"][0]["importedAt"]==imported

    # Changed bytes are a new immutable survey.
    changed=d/"changed.json"
    doc=json.loads(survey.read_text())
    doc["observations"][1]["status"]="SUCCESS"
    doc["observations"][1]["physicalConfigurationId"]="2126"
    changed.write_text(json.dumps(doc,indent=2),encoding="utf-8")
    run(reg,changed)
    e=load(reg)
    assert e["statistics"]["surveyCount"]==2
    assert e["statistics"]["observationCount"]==4
    assert e["statistics"]["provenVoyageCount"]==2
    assert e["statistics"]["unprovenVoyageCount"]==0

print("Registry V1.2 idempotency/provenance tests: PASS")
