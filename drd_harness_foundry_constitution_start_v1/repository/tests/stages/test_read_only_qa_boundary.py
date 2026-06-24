import pytest

from drd_harness.stages.read_only_qa import require_read_only_qa_outputs


def test_drd06_allows_only_read_only_qa_outputs():
    require_read_only_qa_outputs(["READ_ONLY_QA_REPORT.md", "qa_finding_index.json"])


def test_drd06_rejects_final_drd_mutation():
    with pytest.raises(ValueError, match="must not mutate"):
        require_read_only_qa_outputs(["READ_ONLY_QA_REPORT.md", "FINAL_DRD.md"])


def test_drd06_rejects_extra_output():
    with pytest.raises(ValueError, match="may only emit"):
        require_read_only_qa_outputs(["READ_ONLY_QA_REPORT.md", "extra.json"])
