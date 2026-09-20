#!/usr/bin/env python3
import argparse,json,hashlib
from pathlib import Path
from catalog_state import resolve_catalog_path as resolve_local_path
ap=argparse.ArgumentParser();ap.add_argument('--state',required=True);a=ap.parse_args();root=Path(a.state)/'static-masters'; mf=root/'celebrity-manifest.json'; catalog=root/'celebrity-catalog.json'
def resolve_catalog_path(value, provider, ship, configuration, filename):
 return resolve_local_path(root,value,provider,ship,configuration,filename)
if not mf.exists(): raise SystemExit('missing Celebrity static-master manifest; run Full first')
if not catalog.exists(): raise SystemExit('missing Celebrity static-master catalog')
m=json.loads(mf.read_text(encoding='utf-8-sig')); c=json.loads(catalog.read_text(encoding='utf-8-sig')); errors=[]
for x in c.get('configurations',[]):
 p=resolve_catalog_path(x['path'],'celebrity',x.get('shipCode'),x.get('configurationId'),f"celebrity-ship-master-{x.get('shipCode')}-v2.2.json")
 if not p.exists(): errors.append(f'missing {p}');continue
 h=hashlib.sha256(p.read_bytes()).hexdigest()
 if h!=x['sha256']: errors.append(f'hash mismatch {p}')
if errors: raise SystemExit('\n'.join(errors))
print(f"Celebrity static masters valid: {len(c.get('configurations',[]))} catalogued configurations")

princess_catalog=root/'princess'/'catalog.json'
if not princess_catalog.exists(): raise SystemExit('missing Princess static-master catalog; run Full first')
pc=json.loads(princess_catalog.read_text(encoding='utf-8-sig'))
perrors=[]
for x in pc.get('configurations',[]):
 p=resolve_catalog_path(x['path'],'princess',x.get('shipCode'),x.get('configurationId'),'published-deck-plan.json')
 if not p.exists(): perrors.append(f'missing {p}');continue
 if hashlib.sha256(p.read_bytes()).hexdigest()!=x['sha256']:
  perrors.append(f'hash mismatch {p}');continue
 obj=json.loads(p.read_text(encoding='utf-8'))
 if obj.get('shipCode')!=x.get('shipCode'):
  perrors.append(f'ship mismatch {p}')
 if str(obj.get('physicalConfigurationId'))!=str(x.get('configurationId')):
  perrors.append(f'configuration mismatch {p}')
 if not obj.get('voyageBindingProven') or not x.get('voyageBindingProven'):
  perrors.append(f'unproven voyage binding {p}')
 decks=obj.get('decks') or []
 if not decks:
  perrors.append(f'no provider-confirmed decks {p}')
 codes=[str(d.get('deckCode')) for d in decks]
 if len(codes)!=len(set(codes)):
  perrors.append(f'duplicate deck codes {p}')
 for deck in decks:
  response=deck.get('response') or {}
  cabins=response.get('cabins') if isinstance(response,dict) else None
  if not isinstance(cabins,list):
   data=response.get('data') if isinstance(response,dict) else None
   cabins=data.get('cabins') if isinstance(data,dict) else None
  if not isinstance(cabins,list) or not cabins:
   perrors.append(f'empty/unstructured accepted deck {p} deck={deck.get("deckCode")}')
  elif deck.get('cabinCount')!=len(cabins):
   perrors.append(f'cabin count mismatch {p} deck={deck.get("deckCode")}')
if perrors: raise SystemExit('\n'.join(perrors))
print(f"Princess static masters valid: {len(pc.get('configurations',[]))} voyage-bound configurations")
