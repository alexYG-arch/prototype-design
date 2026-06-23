#!/usr/bin/env python3
from pathlib import Path
import json, re, sys
from _common import ROOT, load_json
REQUIRED=[
 'constitution/DRD_HARNESS_CHARTER.md','constitution/REASONING_DOCTRINE.md','constitution/AUTHORITY_MODEL.md',
 'constitution/STAGE_DEPENDENCY_AND_RUNTIME_MODEL.md','constitution/INTERACTION_CLOSURE_POLICY.md',
 'constitution/PRD_ELEMENT_ADOPTION_POLICY.md','constitution/INFORMATION_PRESENTATION_CONSISTENCY.md',
 'constitution/SHARED_COMPONENT_POLICY.md','constitution/NATURAL_LANGUAGE_LAYOUT_POLICY.md',
 'constitution/FIGMA_COMPATIBILITY_POLICY.md','constitution/VALIDATION_MODEL.md','constitution/SPEC_TO_CODE_POLICY.md'
]
errors=[]
for rel in REQUIRED:
 p=ROOT/rel
 if not p.exists() or not p.read_text(encoding='utf-8').strip(): errors.append(f'missing or empty: {rel}')
text='\n'.join((ROOT/r).read_text(encoding='utf-8') for r in REQUIRED if (ROOT/r).exists())
for token in ['演绎推理','归纳推理','所有可点击元素','自然语言','Figma','Spec-to-Code','信息呈现方式']:
 if token not in text: errors.append(f'missing doctrine token: {token}')
for bad in ['TBD','TODO','后续再定义','待补充']:
 if bad in text: errors.append(f'placeholder found: {bad}')
inv=load_json(ROOT/'control/CLAUSE_INVENTORY.json')
for item in inv['clauses']:
 if item['id'] not in text: errors.append(f'clause not found in constitution: {item["id"]}')
if errors:
 print('\n'.join(errors)); sys.exit(1)
print(f'CONSTITUTION VALIDATION: PASS ({len(inv["clauses"])} clauses)')
