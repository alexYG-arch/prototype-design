#!/usr/bin/env python3
import json, re, sys
from _common import ROOT
base=ROOT/'.agents/skills/foundry'
errors=[]; count=0
for d in sorted(base.iterdir()):
 if not d.is_dir(): continue
 count+=1; p=d/'SKILL.md'; m=d/'SKILL_MANIFEST.json'
 if not p.exists(): errors.append(f'missing SKILL.md: {d.name}'); continue
 text=p.read_text(encoding='utf-8')
 if not text.startswith('---\n') or 'name:' not in text or 'description:' not in text: errors.append(f'invalid frontmatter: {d.name}')
 if not m.exists(): errors.append(f'missing manifest: {d.name}')
 else:
  obj=json.loads(m.read_text(encoding='utf-8'))
  if obj.get('skill_id')!=d.name: errors.append(f'skill id mismatch: {d.name}')
if count<15: errors.append(f'expected at least 15 skills, found {count}')
if errors: print('\n'.join(errors)); sys.exit(1)
print(f'SKILL VALIDATION: PASS ({count} skills)')
