"""Hash binding utilities for artifact lineage."""

import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass(frozen=True)
class HashBinding:
    artifact_id: str
    sha256: str


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_text(text: str) -> str:
    return sha256_bytes(text.encode("utf-8"))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def binding_root(bindings: Iterable[HashBinding]) -> str:
    rows: List[str] = [f"{binding.artifact_id}\0{binding.sha256}" for binding in bindings]
    return sha256_text("\n".join(rows))


def changed_bindings(previous: Iterable[HashBinding], current: Iterable[HashBinding]) -> List[str]:
    previous_map = {binding.artifact_id: binding.sha256 for binding in previous}
    current_map = {binding.artifact_id: binding.sha256 for binding in current}
    changed = []
    for artifact_id, old_hash in previous_map.items():
        if current_map.get(artifact_id) != old_hash:
            changed.append(artifact_id)
    return sorted(changed)
