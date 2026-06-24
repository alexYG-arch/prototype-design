"""DRD-06 read-only QA output boundary."""

from typing import Iterable


ALLOWED_DRD06_OUTPUTS = {
    "READ_ONLY_QA_REPORT.md",
    "qa_finding_index.json",
}

FORBIDDEN_DRD06_MUTATION_TARGETS = {
    "FINAL_DRD.md",
    "final_drd_manifest.json",
    "source_snapshot_manifest.json",
    "SPEC_LOCK.json",
    "BUILD_LOCK.json",
}


def require_read_only_qa_outputs(outputs: Iterable[str]) -> None:
    output_set = set(outputs)
    forbidden = sorted(output_set & FORBIDDEN_DRD06_MUTATION_TARGETS)
    if forbidden:
        raise ValueError("DRD-06 must not mutate canonical artifacts: " + ", ".join(forbidden))

    disallowed = sorted(output_set - ALLOWED_DRD06_OUTPUTS)
    if disallowed:
        raise ValueError("DRD-06 may only emit read-only QA report and finding index: " + ", ".join(disallowed))
