"""Source PRD snapshot helpers."""

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Mapping, Union

from drd_harness.kernel.hashline import sha256_file


@dataclass(frozen=True)
class SourceSnapshotFinding:
    code: str
    subject_id: str
    message: str


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


def validate_source_snapshot_manifest(
    manifest: Union[SourceSnapshotManifest, Mapping[str, object]]
) -> List[SourceSnapshotFinding]:
    try:
        manifest_obj = _manifest_from_mapping(manifest) if isinstance(manifest, Mapping) else manifest
    except (KeyError, TypeError, ValueError) as exc:
        return [
            SourceSnapshotFinding(
                code="STAGE012",
                subject_id="SOURCE_SNAPSHOT_MANIFEST",
                message=f"source snapshot manifest is malformed: {exc}",
            )
        ]
    if not isinstance(manifest_obj, SourceSnapshotManifest):
        return [
            SourceSnapshotFinding(
                code="STAGE012",
                subject_id="SOURCE_SNAPSHOT_MANIFEST",
                message="source snapshot manifest must be a SourceSnapshotManifest or mapping",
            )
        ]
    findings: List[SourceSnapshotFinding] = []
    subject_id = manifest_obj.source_prd_snapshot_id
    for field, value in manifest_obj.to_dict().items():
        if field == "byte_size":
            if not isinstance(value, int) or value < 0:
                findings.append(
                    SourceSnapshotFinding(
                        code="STAGE012",
                        subject_id=subject_id,
                        message="byte_size must be a non-negative integer",
                    )
                )
            continue
        if not isinstance(value, str) or not value.strip():
            findings.append(
                SourceSnapshotFinding(
                    code="STAGE012",
                    subject_id=subject_id or "SOURCE_SNAPSHOT_MANIFEST",
                    message=f"{field} must be non-empty text",
                )
            )
    if findings:
        return findings

    source_path = Path(manifest_obj.source_path)
    snapshot_path = Path(manifest_obj.snapshot_path)

    if len(manifest_obj.snapshot_hash) != 64 or any(char not in "0123456789abcdef" for char in manifest_obj.snapshot_hash):
        findings.append(
            SourceSnapshotFinding(
                code="STAGE003",
                subject_id=subject_id,
                message="snapshot_hash must be a sha256 hex digest",
            )
        )

    if not source_path.exists():
        findings.append(
            SourceSnapshotFinding(
                code="STAGE001",
                subject_id=subject_id,
                message=f"source path does not exist: {source_path}",
            )
        )
    if not snapshot_path.exists():
        findings.append(
            SourceSnapshotFinding(
                code="STAGE001",
                subject_id=subject_id,
                message=f"snapshot path does not exist: {snapshot_path}",
            )
        )
        return findings

    actual_hash = sha256_file(snapshot_path)
    if actual_hash != manifest_obj.snapshot_hash:
        findings.append(
            SourceSnapshotFinding(
                code="STAGE003",
                subject_id=subject_id,
                message="snapshot_hash does not match snapshot_path content",
            )
        )

    actual_size = snapshot_path.stat().st_size
    if actual_size != manifest_obj.byte_size:
        findings.append(
            SourceSnapshotFinding(
                code="STAGE012",
                subject_id=subject_id,
                message="byte_size does not match snapshot_path content",
            )
        )

    if source_path.exists() and source_path.read_bytes() != snapshot_path.read_bytes():
        findings.append(
            SourceSnapshotFinding(
                code="STAGE004",
                subject_id=subject_id,
                message="snapshot content drifted from source_path",
            )
        )

    return findings


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


def _manifest_from_mapping(manifest: Mapping[str, object]) -> SourceSnapshotManifest:
    return SourceSnapshotManifest(
        source_prd_snapshot_id=str(manifest["source_prd_snapshot_id"]),
        source_path=str(manifest["source_path"]),
        snapshot_path=str(manifest["snapshot_path"]),
        snapshot_hash=str(manifest["snapshot_hash"]),
        created_at=str(manifest["created_at"]),
        byte_size=int(manifest["byte_size"]),
        content_type=str(manifest["content_type"]),
        normalization_method=str(manifest["normalization_method"]),
        source_identity=str(manifest["source_identity"]),
    )
