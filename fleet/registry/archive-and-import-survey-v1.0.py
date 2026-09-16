#!/usr/bin/env python3
import argparse, hashlib, shutil, subprocess, sys
from pathlib import Path
def digest(p):
    h=hashlib.sha256()
    with open(p,"rb") as f:
        for b in iter(lambda:f.read(1048576),b""): h.update(b)
    return h.hexdigest()
def main():
    a=argparse.ArgumentParser()
    a.add_argument("--survey",required=True); a.add_argument("--archive-dir",required=True)
    a.add_argument("--registry",required=True); a.add_argument("--registry-tool",required=True)
    x=a.parse_args(); s=Path(x.survey); d=digest(s)
    ad=Path(x.archive_dir); ad.mkdir(parents=True,exist_ok=True)
    dst=ad/f"sha256-{d}.json"
    if dst.exists():
        if digest(dst)!=d: raise SystemExit(f"Archive hash mismatch: {dst}")
    else:
        tmp=Path(str(dst)+".tmp"); shutil.copyfile(s,tmp)
        if digest(tmp)!=d: tmp.unlink(missing_ok=True); raise SystemExit("Archive verification failed")
        tmp.replace(dst)
    print(f"Archived survey: {dst}")
    print(f"sourceSurveyId: sha256:{d}")
    subprocess.run([sys.executable,x.registry_tool,"--registry",x.registry,"--survey",str(dst)],check=True)
if __name__=="__main__": main()
