from pathlib import Path

from drd_harness.kernel.import_boundaries import (
    find_forbidden_imports,
    find_forbidden_runtime_reads,
)
from drd_harness.kernel.promoted_authority import require_repository_local_authority


def test_forbidden_runtime_imports_are_reported(tmp_path: Path):
    source = tmp_path / "module.py"
    source.write_text("from build_program.program import runner\n", encoding="utf-8")

    findings = find_forbidden_imports(tmp_path)

    assert len(findings) == 1
    assert findings[0].code == "FND007"
    assert "build_program" in findings[0].message


def test_repository_local_imports_are_allowed(tmp_path: Path):
    source = tmp_path / "module.py"
    source.write_text("from drd_harness.kernel.runtime import RuntimeDeclaration\n", encoding="utf-8")

    assert find_forbidden_imports(tmp_path) == []


def test_forbidden_runtime_reads_are_reported(tmp_path: Path):
    source = tmp_path / "module.py"
    source.write_text('Path("control/CONSTITUTION_LOCK.json").read_text()\n', encoding="utf-8")

    findings = find_forbidden_runtime_reads(tmp_path)

    assert len(findings) == 1
    assert findings[0].code == "FND010"


def test_runtime_read_boundary_ignores_policy_constants(tmp_path: Path):
    source = tmp_path / "module.py"
    source.write_text(
        'FORBIDDEN_RUNTIME_READ_ROOTS = {"control", "constitution", "references"}\n',
        encoding="utf-8",
    )

    assert find_forbidden_runtime_reads(tmp_path) == []


def test_forbidden_runtime_open_calls_are_reported(tmp_path: Path):
    source = tmp_path / "module.py"
    source.write_text('open("control/CONSTITUTION_LOCK.json")\n', encoding="utf-8")

    findings = find_forbidden_runtime_reads(tmp_path)

    assert len(findings) == 1
    assert findings[0].code == "FND010"


def test_promoted_authority_path_must_be_repository_local():
    require_repository_local_authority("contracts/foundation.md")
    require_repository_local_authority("schemas/runtime_declaration.schema.json")


def test_construction_authority_path_is_rejected():
    try:
        require_repository_local_authority("control/CONSTITUTION_LOCK.json")
    except ValueError as exc:
        assert "construction root" in str(exc)
    else:
        raise AssertionError("expected construction authority path rejection")
