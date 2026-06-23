from pathlib import Path
import hashlib, json
ROOT=Path(__file__).resolve().parents[1]
def sha256(path:Path)->str:
    h=hashlib.sha256()
    with path.open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024), b''): h.update(chunk)
    return h.hexdigest()
def load_json(path:Path): return json.loads(path.read_text(encoding='utf-8'))
def fail(msg): raise SystemExit(msg)
