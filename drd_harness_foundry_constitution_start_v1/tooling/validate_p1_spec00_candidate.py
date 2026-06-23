#!/usr/bin/env python3
import json, sys
from _common import ROOT, load_json
base=ROOT/'build_program/phases/P1/candidates/P1-SPEC-00'
required=['P1_PHASE_PLAN.md','P1_CLAUSE_OWNERSHIP.json','P1_SPEC_PART_MAP.json','P1_IMPLEMENTATION_WORKPACK_MAP.json','P1_ACCEPTANCE_MATRIX.json','P1_ASSEMBLY_SEED.json','CANDIDATE_MANIFEST.json','PART_SELF_CHECK.md','HANDOFF.md']
errors=[]
for rel in required:
 p=base/rel
 if not p.exists() or p.stat().st_size==0: errors.append(f'missing or empty: {rel}')
for rel in [r for r in required if r.endswith('.json')]:
 p=base/rel
 if p.exists():
  try: json.loads(p.read_text(encoding='utf-8'))
  except Exception as e: errors.append(f'invalid json {rel}: {e}')
if (base/'P1_CLAUSE_OWNERSHIP.json').exists():
 own=load_json(base/'P1_CLAUSE_OWNERSHIP.json'); inv=load_json(ROOT/'control/CLAUSE_INVENTORY.json')
 expected={x['id'] for x in inv['clauses']}; rows=own.get('ownership',[]); seen=[x.get('clause_id') for x in rows]
 missing=expected-set(seen); dup={x for x in seen if seen.count(x)>1}
 if missing: errors.append('missing clause ownership: '+','.join(sorted(missing)))
 if dup: errors.append('duplicate clause ownership: '+','.join(sorted(dup)))
for p in base.rglob('*') if base.exists() else []:
 if p.is_file() and p.suffix in {'.md','.json'}:
  t=p.read_text(encoding='utf-8')
  for bad in ['TBD','TODO','后续定义','待补充']:
   if bad in t: errors.append(f'placeholder {bad}: {p.relative_to(base)}')
if errors: print('\n'.join(errors)); sys.exit(1)
print('P1-SPEC-00 CANDIDATE VALIDATION: PASS')
