#!/usr/bin/env python3
import sys
from _common import ROOT, load_json
m=load_json(ROOT/'build_program/program/PROGRAM_MANIFEST.json')
s=load_json(ROOT/'build_program/program/PROGRAM_STATE.json')
errors=[]
ids=[p['id'] for p in m['phases']]
if ids != ['P1','P2','P3','P4']: errors.append(f'phase order invalid: {ids}')
if s['current_workpack']!='P1-SPEC-00': errors.append('current workpack must be P1-SPEC-00')
if s['phases']['P1']['status']!='ACTIVE': errors.append('P1 must be ACTIVE')
for p in ['P2','P3','P4']:
 if s['phases'][p]['status']!='WAITING_UPSTREAM_LOCK': errors.append(f'{p} must wait for upstream lock')
for p in ids:
 if not (ROOT/f'build_program/phases/{p}/PHASE_MANIFEST.json').exists(): errors.append(f'missing phase manifest {p}')
if errors: print('\n'.join(errors)); sys.exit(1)
print('PROGRAM VALIDATION: PASS')
