"""Postflight scope checks for generated workpack changes."""

from dataclasses import dataclass
from fnmatch import fnmatch
from typing import Iterable, List


@dataclass(frozen=True)
class PostflightFinding:
    code: str
    subject_id: str
    message: str


def validate_scope(
    changed_paths: Iterable[str],
    allowed_patterns: Iterable[str],
    forbidden_patterns: Iterable[str],
) -> List[PostflightFinding]:
    allowed = list(allowed_patterns)
    forbidden = list(forbidden_patterns)
    findings: List[PostflightFinding] = []

    for path in sorted(_normalize(path) for path in changed_paths):
        forbidden_match = _first_match(path, forbidden)
        if forbidden_match:
            findings.append(
                PostflightFinding(
                    "VLOCK-CHECK-003",
                    path,
                    f"changed path matches forbidden pattern {forbidden_match}",
                )
            )
            continue

        allowed_match = _first_match(path, allowed)
        if not allowed_match:
            findings.append(PostflightFinding("VLOCK-CHECK-003", path, "changed path is outside allowed scope"))

    return findings


def build_scope_report(
    changed_paths: Iterable[str],
    allowed_patterns: Iterable[str],
    forbidden_patterns: Iterable[str],
) -> dict:
    findings = validate_scope(changed_paths, allowed_patterns, forbidden_patterns)
    return {
        "status": "PASS" if not findings else "FAIL",
        "changed_paths": sorted(_normalize(path) for path in changed_paths),
        "allowed_patterns": list(allowed_patterns),
        "forbidden_patterns": list(forbidden_patterns),
        "findings": [finding.__dict__ for finding in findings],
    }


def _normalize(path: str) -> str:
    return path.replace("\\", "/").lstrip("./")


def _first_match(path: str, patterns: Iterable[str]) -> str:
    for pattern in patterns:
        if fnmatch(path, pattern):
            return pattern
    return ""
