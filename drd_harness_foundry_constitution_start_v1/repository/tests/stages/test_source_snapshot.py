from pathlib import Path

import pytest

from drd_harness.stages.source_snapshot import create_source_snapshot


def test_create_source_snapshot_copies_source_and_binds_hash(tmp_path: Path):
    source = tmp_path / "source.md"
    snapshot = tmp_path / "run" / "source.md"
    source.write_text("# PRD\nLine one\n", encoding="utf-8")

    manifest = create_source_snapshot(
        source,
        snapshot,
        snapshot_id="SRC-PRD-001",
        created_at="2026-06-24T00:00:00Z",
    )

    assert snapshot.read_text(encoding="utf-8") == "# PRD\nLine one\n"
    assert manifest.source_prd_snapshot_id == "SRC-PRD-001"
    assert manifest.snapshot_hash == "da7a9b4096b8e5b06107312e89e6b84e5060369ca15dac13476e54bd613dc269"
    assert manifest.byte_size == len("# PRD\nLine one\n".encode("utf-8"))


def test_source_snapshot_refuses_to_overwrite_existing_snapshot(tmp_path: Path):
    source = tmp_path / "source.md"
    snapshot = tmp_path / "snapshot.md"
    source.write_text("new", encoding="utf-8")
    snapshot.write_text("old", encoding="utf-8")

    with pytest.raises(FileExistsError):
        create_source_snapshot(source, snapshot, snapshot_id="SRC", created_at="now")


def test_source_snapshot_normalization_must_be_declared(tmp_path: Path):
    source = tmp_path / "source.md"
    snapshot = tmp_path / "snapshot.md"
    source.write_bytes(b"a\r\nb\r\n")

    manifest = create_source_snapshot(
        source,
        snapshot,
        snapshot_id="SRC",
        created_at="now",
        normalization_method="utf-8 line ending normalization",
    )

    assert snapshot.read_bytes() == b"a\nb\n"
    assert manifest.normalization_method == "utf-8 line ending normalization"
