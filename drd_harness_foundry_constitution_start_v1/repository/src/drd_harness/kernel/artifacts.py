"""Artifact manifest and format primitives."""

import hashlib
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Mapping, Optional


class ArtifactFormat(str, Enum):
    MARKDOWN = "markdown"
    JSON = "json"


class ArtifactRole(str, Enum):
    HUMAN_SEMANTIC = "human_semantic"
    OPERATIONAL_CONTROL = "operational_control"
    INDEX = "index"
    SCHEMA = "schema"


@dataclass(frozen=True)
class ArtifactManifest:
    artifact_id: str
    path: str
    format: ArtifactFormat
    authority_role: ArtifactRole
    sha256: Optional[str] = None

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "ArtifactManifest":
        artifact_id = _required_text(data, "artifact_id")
        path = _required_text(data, "path")
        return cls(
            artifact_id=artifact_id,
            path=path,
            format=ArtifactFormat(_required_text(data, "format")),
            authority_role=ArtifactRole(_required_text(data, "authority_role")),
            sha256=data.get("sha256"),
        )

    def to_dict(self) -> Dict[str, Any]:
        result = {
            "artifact_id": self.artifact_id,
            "path": self.path,
            "format": self.format.value,
            "authority_role": self.authority_role.value,
        }
        if self.sha256:
            result["sha256"] = self.sha256
        return result

    def validate_format_policy(self) -> None:
        suffix = Path(self.path).suffix.lower()
        if suffix in {".yml", ".yaml"}:
            raise ValueError("semantic or mixed YAML artifacts are prohibited")

        if self.authority_role == ArtifactRole.HUMAN_SEMANTIC and self.format != ArtifactFormat.MARKDOWN:
            raise ValueError("human semantic artifacts must be markdown")

        machine_roles = {
            ArtifactRole.OPERATIONAL_CONTROL,
            ArtifactRole.INDEX,
            ArtifactRole.SCHEMA,
        }
        if self.authority_role in machine_roles and self.format != ArtifactFormat.JSON:
            raise ValueError("operational artifacts, indexes, and schemas must be json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _required_text(data: Mapping[str, Any], key: str) -> str:
    value = data.get(key)
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{key} must be a non-empty string")
    return value
