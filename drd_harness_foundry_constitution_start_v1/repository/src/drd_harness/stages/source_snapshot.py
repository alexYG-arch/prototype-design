"""Source PRD snapshot helpers."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict

from drd_harness.kernel.hashline import sha256_file


@dataclass(frozen=True)
class SourceSnapshotManifest:
    source_prd_snapshot_id: str
    source_path: str
    snapshot_path: str
    snapshot_hash: str
    created_at: str
    byte_size: int
    content_type: str
    normalization_method: str
    source_identity: str

    def to_dict(self) -> Dict[str, object]:
        return {
            "source_prd_snapshot_id": self.source_prd_snapshot_id,
            "source_path": self.source_path,
            "snapshot_path": self.snapshot_path,
            "snapshot_hash": self.snapshot_hash,
            "created_at": self.created_at,
            "byte_size": self.byte_size,
            "content_type": self.content_type,
            "normalization_method": self.normalization_method,
            "source_identity": self.source_identity,
        }


def create_source_snapshot(
    source_path: Path,
    snapshot_path: Path,
    *,
    snapshot_id: str,
    created_at: str,
    content_type: str = "text/markdown",
    normalization_method: str = "none",
    source_identity: str = "",
) -> SourceSnapshotManifest:
    if snapshot_path.exists():
        raise FileExistsError(f"snapshot already exists: {snapshot_path}")

    data = source_path.read_bytes()
    if normalization_method == "utf-8 line ending normalization":
        text = data.decode("utf-8").replace("\r\n", "\n").replace("\r", "\n")
        data = text.encode("utf-8")
    elif normalization_method != "none":
        raise ValueError(f"unsupported normalization method: {normalization_method}")

    snapshot_path.parent.mkdir(parents=True, exist_ok=True)
    snapshot_path.write_bytes(data)

    return SourceSnapshotManifest(
        source_prd_snapshot_id=snapshot_id,
        source_path=str(source_path),
        snapshot_path=str(snapshot_path),
        snapshot_hash=sha256_file(snapshot_path),
        created_at=created_at,
        byte_size=snapshot_path.stat().st_size,
        content_type=content_type,
        normalization_method=normalization_method,
        source_identity=source_identity or source_path.name,
    )
