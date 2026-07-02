import ast
from pathlib import Path


CLI_MAIN = Path("repository/src/drd_harness/cli/main.py")


def test_cli_module_has_no_domain_classes_or_dataclasses():
    tree = ast.parse(CLI_MAIN.read_text(encoding="utf-8"))
    decorators = [
        decorator.id
        for node in ast.walk(tree)
        if isinstance(node, ast.FunctionDef)
        for decorator in node.decorator_list
        if isinstance(decorator, ast.Name)
    ]

    assert [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)] == []
    assert "dataclass" not in decorators


def test_cli_module_has_no_graph_compiler_promotion_or_review_constructors():
    source = CLI_MAIN.read_text(encoding="utf-8").lower()
    forbidden_terms = [
        "graph.nodes",
        "semantic_unit",
        "compile_final_drd",
        "compare_semantic_units",
        "build_review_lock",
        "build_promotion_record",
        "approve_candidate",
    ]

    assert [term for term in forbidden_terms if term in source] == []


def test_cli_module_imports_only_delegation_targets():
    tree = ast.parse(CLI_MAIN.read_text(encoding="utf-8"))
    imported_modules = {
        node.module
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    imported_roots = {
        alias.name.split(".", 1)[0]
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }

    assert imported_modules <= {
        "dataclasses",
        "json",
        "pathlib",
        "typing",
        "drd_harness.adapters.markdown_prd",
        "drd_harness.adapters.prd_harness",
        "drd_harness.kernel.import_boundaries",
        "drd_harness.orchestrator.codex_stage",
        "drd_harness.orchestrator.program_driver",
        "drd_harness.orchestrator.qa_completion",
        "drd_harness.orchestrator.stage_compilation",
        "drd_harness.orchestrator.stage_promotion",
        "drd_harness.orchestrator.workpacks",
        "drd_harness.validators.spec_validator",
        "drd_harness.validators.workpack_scope",
    }
    assert imported_roots <= {"argparse", "json"}


def test_review_and_stage_manifest_templates_are_json():
    for path in [
        Path("repository/templates/review_decision.template.json"),
        Path("repository/templates/stage_manifest.template.json"),
    ]:
        ast.literal_eval(path.read_text(encoding="utf-8"))
