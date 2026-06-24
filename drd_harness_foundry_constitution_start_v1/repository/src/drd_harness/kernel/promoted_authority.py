"""Repository-local promoted authority path checks."""

from pathlib import Path


PROMOTED_AUTHORITY_ROOTS = {
    "contracts",
    "schemas",
    "templates",
}

CONSTRUCTION_AUTHORITY_ROOTS = {
    ".agents",
    "build_program",
    "constitution",
    "control",
    "current_capsule",
    "references",
    "tooling",
}


def require_repository_local_authority(path: str) -> None:
    parts = Path(path).parts
    if not parts:
        raise ValueError("authority path must not be empty")

    root = parts[0]
    if root in CONSTRUCTION_AUTHORITY_ROOTS:
        raise ValueError(f"runtime authority path must not read construction root: {root}")
    if root not in PROMOTED_AUTHORITY_ROOTS:
        raise ValueError(f"runtime authority path must be repository-local promoted authority: {path}")
