#!/usr/bin/env python3
"""Provider-neutral static-master orchestration. Runtime data is written only below work/."""
import argparse,json,subprocess,sys,hashlib,shutil
from pathlib import Path

def load(p): return json.loads(Path(p).read_text(encoding='utf-8-sig'))
def dump(p,o):
 p=Path(p);p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(o,indent=2,ensure_ascii=False),encoding='utf-8')
def sha(p): return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def proven_configs(reg):
 out={}
 for v in reg.get('voyages',{}).values():
  if v.get('provider')!='CELEBRITY' or v.get('configurationEvidenceState')!='PROVEN_TARGET_SAILING': continue
  ship=v.get('shipCode');cfg=v.get('physicalConfigurationId')
  if ship and cfg: out.setdefault((ship,str(cfg)),[]).append(v.get('voyageId'))
 return out

def run(cmd):
 print('+',' '.join(map(str,cmd)),flush=True); subprocess.run(list(map(str,cmd)),check=True)

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--mode',choices=['Full','Daily'],required=True);ap.add_argument('--voyages',required=True);ap.add_argument('--registry',required=True);ap.add_argument('--state',required=True);ap.add_argument('--data',required=True);ap.add_argument('--python',default=sys.executable);a=ap.parse_args()
 root=Path(__file__).resolve().parent; state=Path(a.state); data=Path(a.data); masters=state/'static-masters'/'celebrity'; masters.mkdir(parents=True,exist_ok=True)
 configs=proven_configs(load(a.registry)); built=[]; skipped=[]
 for (ship,cfg),vids in sorted(configs.items()):
  final=masters/ship/cfg/f'celebrity-ship-master-{ship}-v2.2.json'
  if a.mode=='Daily' and final.exists(): skipped.append(f'{ship}:{cfg}'); continue
  out=masters/ship/cfg
  if a.mode=='Full' and out.exists(): shutil.rmtree(out)
  out.mkdir(parents=True,exist_ok=True); empty=out/'bootstrap-empty-master.json'
  dump(empty,{'version':'bootstrap','provider':'CELEBRITY','shipCode':ship,'fareProducts':[],'categoryAssignments':[],'categoryMaster':[]})
  run([
   a.python,root/'providers/celebrity/configuration-discovery.py',
   '--voyages',a.voyages,'--baseline-master',empty,'--ship',ship,
   '--target-configuration',cfg,'--include-voyage-ids',','.join(sorted(set(vids))),
   '--output',out
  ])
  if not final.exists(): raise SystemExit(f'missing expected master {final}')
  val=load(out/f'celebrity-ship-master-validation-{ship}-v2.2.json')
  if val.get('cabinDeckConflictCount',0): raise SystemExit(f'cabin/deck conflict {ship}:{cfg}')
  built.append({'shipCode':ship,'configurationId':cfg,'path':str(final),'sha256':sha(final),'saturated':bool((val.get('saturation') or {}).get('saturated'))})
 catalog_path=state/'static-masters'/'celebrity-catalog.json'
 existing={}
 if catalog_path.exists():
  for x in load(catalog_path).get('configurations',[]): existing[(x.get('shipCode'),str(x.get('configurationId')))]=x
 for x in built: existing[(x['shipCode'],str(x['configurationId']))]=x
 catalog={'schemaVersion':'1.0','provider':'CELEBRITY','configurations':[existing[k] for k in sorted(existing)]}
 dump(catalog_path,catalog)
 manifest={'schemaVersion':'1.0','provider':'CELEBRITY','mode':a.mode,'built':built,'skippedExisting':skipped,'knownProvenConfigurationCount':len(configs),'catalogPath':str(catalog_path)}
 dump(state/'static-masters'/'celebrity-manifest.json',manifest)
 print(json.dumps(manifest,indent=2))
if __name__=='__main__': main()
