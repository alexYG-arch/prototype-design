"""Runtime import and construction-boundary checks."""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Set


FORBIDDEN_IMPORT_ROOTS = {
    "build_program",
    "current_capsule",
    "references",
    "tooling",
}

FORBIDDEN_RUNTIME_READ_ROOTS = {
    ".agents",
    "build_program",
    "constitution",
    "control",
    "current_capsule",
    "references",
    "tooling",
}


@dataclass(frozen=True)
class BoundaryFinding:
    code: str
    path: str
    message: str


def find_forbidden_imports(source_root: Path, forbidden_roots: Iterable[str] = FORBIDDEN_IMPORT_ROOTS) -> List[BoundaryFinding]:
    roots = set(forbidden_roots)
    findings: List[BoundaryFinding] = []
    for path in _python_files(source_root):
        tree = _parse(path)
        for node in ast.walk(tree):
            imported_roots = _imported_roots(node)
            for root in sorted(imported_roots & roots):
                findings.append(
                    BoundaryFinding(
                        code="FND007",
                        path=str(path),
                        message=f"runtime source imports construction path root: {root}",
                    )
                )
    return findings


def find_forbidden_runtime_reads(source_root: Path, forbidden_roots: Iterable[str] = FORBIDDEN_RUNTIME_READ_ROOTS) -> List[BoundaryFinding]:
    roots = set(forbidden_roots)
    findings: List[BoundaryFinding] = []
    for path in _python_files(source_root):
        tree = _parse(path)
        literals = _runtime_path_literals(tree)
        for literal in sorted(literals):
            root = literal.split("/", 1)[0]
            if root in roots:
                findings.append(
                    BoundaryFinding(
                        code="FND010",
                        path=str(path),
                        message=f"runtime source references construction authority path: {literal}",
                    )
                )
    return findings


def _python_files(source_root: Path):
    if source_root.is_file():
        yield source_root
        return
    yield from sorted(source_root.rglob("*.py"))


def _parse(path: Path) -> ast.AST:
    return ast.parse(path.read_text(encoding="utf-8"), filename=str(path))


def _imported_roots(node: ast.AST) -> Set[str]:
    if isinstance(node, ast.Import):
        return {alias.name.split(".", 1)[0] for alias in node.names}
    if isinstance(node, ast.ImportFrom) and node.module:
        return {node.module.split(".", 1)[0]}
    return set()


def _runtime_path_literals(tree: ast.AST) -> Set[str]:
    literals: Set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not node.args:
            continue
        first_arg = node.args[0]
        if not isinstance(first_arg, ast.Constant) or not isinstance(first_arg.value, str):
            continue
        call_name = _call_name(node.func)
        if call_name in {"Path", "open"} or call_name.endswith(".open"):
            literals.add(first_arg.value)
    return literals


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""
