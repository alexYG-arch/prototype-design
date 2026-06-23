#!/usr/bin/env python3
import hashlib, json, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for c in iter(lambda:f.read(1024*1024),b''): h.update(c)
 return h.hexdigest()
m=json.loads((ROOT/'START_PACKAGE_MANIFEST.json').read_text(encoding='utf-8'))
errors=[]; expected={x['path'] for x in m['files']}; actual=set()
for p in ROOT.rglob('*'):
 if p.is_file():
  rel=p.relative_to(ROOT).as_posix()
  if rel not in {'START_PACKAGE_MANIFEST.json','ROOT.sha256'} and '__pycache__' not in rel and not rel.endswith('.pyc'): actual.add(rel)
for e in m['files']:
 p=ROOT/e['path']
 if not p.exists(): errors.append('missing: '+e['path'])
 elif sha(p)!=e['sha256']: errors.append('hash mismatch: '+e['path'])
for rel in sorted(actual-expected): errors.append('untracked: '+rel)
for rel in sorted(expected-actual): errors.append('manifest-only: '+rel)
lines='\n'.join(f"{e['path']}\0{e['sha256']}" for e in m['files']).encode('utf-8')
root=hashlib.sha256(lines).hexdigest()
if root!=m['root_sha256'] or root!=(ROOT/'ROOT.sha256').read_text().strip(): errors.append('root hash mismatch')
if errors: print('\n'.join(errors)); sys.exit(1)
print(f'START PACKAGE INTEGRITY: PASS ({len(expected)} files)')
