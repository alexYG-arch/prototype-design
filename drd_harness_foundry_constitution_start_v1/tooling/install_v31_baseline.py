#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, shutil, stat, sys, zipfile
from pathlib import Path
EXPECTED='f668e4943c26b64f27a06ef0c07d67aa4b5e2087927601ac69e18317b0a510ba'
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with open(p,'rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
def main():
 ap=argparse.ArgumentParser(); ap.add_argument('--archive',required=True); a=ap.parse_args(); src=Path(a.archive).resolve()
 if sha(src)!=EXPECTED: raise SystemExit('v3.1 archive hash mismatch')
 out=ROOT/'references/v3_1/source_snapshot'
 if out.exists(): shutil.rmtree(out)
 out.mkdir(parents=True)
 with zipfile.ZipFile(src) as z:
  for info in z.infolist():
   name=info.filename.replace('\\','/')
   if name.startswith('__MACOSX/') or '/._' in name or name.startswith('._'): continue
   dest=(out/name).resolve()
   if out.resolve() not in dest.parents and dest!=out.resolve(): raise SystemExit(f'unsafe path: {name}')
   if info.is_dir(): dest.mkdir(parents=True,exist_ok=True); continue
   dest.parent.mkdir(parents=True,exist_ok=True)
   with z.open(info) as r, open(dest,'wb') as w: shutil.copyfileobj(r,w)
 for p in sorted(out.rglob('*'), reverse=True):
  try: p.chmod(0o555 if p.is_dir() else 0o444)
  except OSError: pass
 (ROOT/'references/v3_1/INSTALLATION.json').write_text(json.dumps({'archive_sha256':EXPECTED,'installed_to':str(out.relative_to(ROOT))},indent=2)+'\n',encoding='utf-8')
 print('v3.1 read-only baseline installed')
if __name__=='__main__': main()
