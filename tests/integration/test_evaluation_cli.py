"""Exercise the contributor command with real temporary fixture files."""

import json
import runpy
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parents[2] / "scripts/check_evals.py"


def invoke(monkeypatch: pytest.MonkeyPatch, root: Path, *args: str) -> int:
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--root", str(root), *args])
    with pytest.raises(SystemExit) as result:
        runpy.run_path(str(SCRIPT), run_name="__main__")
    return result.value.code


def test_cli_reports_draft_as_json(evaluation_root, monkeypatch, capsys) -> None:
    assert invoke(monkeypatch, evaluation_root, "--json") == 0
    assert json.loads(capsys.readouterr().out)["status"] == "valid_draft"


def test_cli_explicit_review_gate_fails(evaluation_root, monkeypatch, capsys) -> None:
    assert invoke(monkeypatch, evaluation_root, "--json", "--require-reviewed") == 1
    report = json.loads(capsys.readouterr().out)
    assert report["status"] == "review_required"
    assert len(report["unreviewed_case_ids"]) == 2


def test_cli_malformed_data_still_emits_json(evaluation_root, monkeypatch, capsys) -> None:
    (evaluation_root / "manifest.json").write_text("bad json")
    assert invoke(monkeypatch, evaluation_root, "--json") == 1
    assert json.loads(capsys.readouterr().out)["status"] == "invalid"


def test_cli_generates_packet_and_rejects_stale_copy(evaluation_root, monkeypatch, capsys) -> None:
    assert invoke(monkeypatch, evaluation_root, "--write-review-packet") == 0
    assert invoke(monkeypatch, evaluation_root, "--check-review-packet") == 0
    (evaluation_root / "REVIEW.md").write_text("stale packet")
    assert invoke(monkeypatch, evaluation_root, "--json", "--check-review-packet") == 1
    report = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert "stale" in " ".join(report["errors"])


def test_cli_refuses_packet_write_through_external_symlink(
    evaluation_root, monkeypatch, capsys
) -> None:
    external = evaluation_root.parent / "external.md"
    external.write_text("Do not overwrite")
    (evaluation_root / "REVIEW.md").symlink_to(external)
    assert invoke(monkeypatch, evaluation_root, "--json", "--write-review-packet") == 1
    assert external.read_text() == "Do not overwrite"
    assert json.loads(capsys.readouterr().out)["status"] == "invalid"
