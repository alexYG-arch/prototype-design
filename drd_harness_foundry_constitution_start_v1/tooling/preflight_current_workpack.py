#!/usr/bin/env python3
import argparse, fnmatch, json, sys
from _common import ROOT, load_json, sha256
p=argparse.ArgumentParser(); p.add_argument('--post',action='store_true'); args=p.parse_args()
ctx=load_json(ROOT/'current_capsule/context_manifest.json')
errors=[]
for f in ctx['required_files']:
 path=ROOT/f['path']
 if not path.exists(): errors.append(f'missing required file: {f["path"]}')
 elif sha256(path)!=f['sha256']: errors.append(f'hash mismatch: {f["path"]}')
if not ctx['acceptance_commands']: errors.append('acceptance commands empty')
if args.post:
 out=ROOT/ctx.get('candidate_dir', f'build_program/phases/{ctx.get("phase", "")}/candidates/{ctx["workpack_id"]}')
 for rel in ctx['required_outputs']:
  if not (out/rel).exists(): errors.append(f'missing candidate output: {rel}')
if errors: print('\n'.join(errors)); sys.exit(1)
print('CURRENT WORKPACK PREFLIGHT: PASS'+(' (post)' if args.post else ''))
