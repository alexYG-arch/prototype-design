"""Runtime import and construction-boundary checks."""

import ast
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List, Optional, Set


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
ALLOWED_RUNTIME_PATH_PREFIXES = {
    "current_capsule/outputs",
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
            if root in roots and not _is_allowed_runtime_path(literal):
                findings.append(
                    BoundaryFinding(
                        code="FND010",
                        path=str(path),
                        message=f"runtime source references construction authority path: {literal}",
                    )
                )
    return findings


def _is_allowed_runtime_path(literal: str) -> bool:
    normalized = literal.rstrip("/")
    return any(
        normalized == prefix or normalized.startswith(prefix + "/")
        for prefix in ALLOWED_RUNTIME_PATH_PREFIXES
    )


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
        if isinstance(node, ast.BinOp):
            literal = _path_literal_from_expr(node)
            if literal:
                literals.add(literal)
            continue
        if not isinstance(node, ast.Call):
            continue
        call_name = _call_name(node.func)
        if call_name == "Path":
            literal = _path_literal_from_expr(node)
        elif (call_name == "open" or call_name.endswith(".open")) and node.args:
            literal = _path_literal_from_expr(node.args[0]) or _string_literal(node.args[0])
        else:
            literal = None
        if literal:
            literals.add(literal)
    return _longest_path_literals(literals)


def _path_literal_from_expr(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Call) and _call_name(node.func) == "Path":
        if not node.args:
            return ""
        return _string_literal(node.args[0])
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Div):
        left = _path_literal_from_expr(node.left)
        right = _string_literal(node.right)
        if left is None or right is None:
            return None
        if not left:
            return right
        return left.rstrip("/") + "/" + right.lstrip("/")
    return None


def _string_literal(node: ast.AST) -> Optional[str]:
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _longest_path_literals(literals: Set[str]) -> Set[str]:
    result = set()
    for literal in literals:
        prefix = literal.rstrip("/") + "/"
        if not any(other != literal and other.startswith(prefix) for other in literals):
            result.add(literal)
    return result


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""
