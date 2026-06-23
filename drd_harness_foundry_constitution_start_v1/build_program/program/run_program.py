#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
STATE_PATH = ROOT / "build_program/program/PROGRAM_STATE.json"
MANIFEST_PATH = ROOT / "build_program/program/PROGRAM_MANIFEST.json"

def load(path): return json.loads(path.read_text(encoding="utf-8"))

def status():
    state=load(STATE_PATH); manifest=load(MANIFEST_PATH)
    print(json.dumps({"program":manifest["program_id"],"target":state["target"],"current_phase":state["current_phase"],"current_lane":state["current_lane"],"current_workpack":state["current_workpack"],"phases":state["phases"]}, ensure_ascii=False, indent=2))

def preflight():
    import subprocess
    cmds=[
      [sys.executable, str(ROOT/'tooling/verify_start_package.py')],
      [sys.executable, str(ROOT/'tooling/validate_constitution.py')],
      [sys.executable, str(ROOT/'tooling/validate_program.py')],
      [sys.executable, str(ROOT/'tooling/validate_skills.py')],
      [sys.executable, str(ROOT/'tooling/preflight_current_workpack.py')],
    ]
    for cmd in cmds:
        rc=subprocess.run(cmd, cwd=ROOT).returncode
        if rc: raise SystemExit(rc)
    print('PROGRAM PREFLIGHT: PASS')

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--status', action='store_true')
    p.add_argument('--preflight', action='store_true')
    args=p.parse_args()
    if args.status: status()
    elif args.preflight: preflight()
    else: p.print_help()

if __name__=='__main__': main()
