import json
from pathlib import Path
from typing import Any

import pytest

from professor_ai.evaluation.fixtures import check_dataset, load_dataset, render_review


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Any) -> None:
    path.write_text(json.dumps(data, ensure_ascii=False), encoding="utf-8")


def test_valid_draft_is_not_reported_as_human_reviewed(evaluation_root: Path) -> None:
    report = check_dataset(evaluation_root)

    assert report.passed
    assert report.status == "valid_draft"
    assert report.case_count == 2
    assert report.document_count == 2
    assert report.reviewed_case_count == 0
    assert len(report.fingerprint) == 64


def test_explicit_review_gate_rejects_pending_cases(evaluation_root: Path) -> None:
    report = check_dataset(evaluation_root, require_reviewed=True)

    assert not report.passed
    assert report.status == "review_required"
    assert set(report.unreviewed_case_ids) == {"smoke-math-01-en", "smoke-math-01-pt"}


def test_named_human_review_metadata_can_satisfy_the_gate(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    for case in cases:
        case["review"] = {
            "status": "approved",
            "reviewer": "Human reviewer in this temporary test fixture",
            "reviewed_on": "2026-10-23",
            "notes": "Fixture metadata, not an actual dataset approval.",
        }
    write_json(path, cases)

    report = check_dataset(evaluation_root, require_reviewed=True)

    assert report.passed
    assert report.status == "human_reviewed"
    assert report.reviewed_case_count == 2


@pytest.mark.parametrize("field", ["reviewer", "reviewed_on"])
def test_approval_requires_a_named_reviewer_and_date(evaluation_root: Path, field: str) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["review"] = {
        "status": "approved",
        "reviewer": "Human fixture",
        "reviewed_on": "2026-10-23",
        "notes": "",
    }
    cases[0]["review"][field] = None
    write_json(path, cases)

    assert not check_dataset(evaluation_root).passed


def test_modified_source_fails_its_recorded_hash(evaluation_root: Path) -> None:
    (evaluation_root / "corpus/square.en.md").write_text("Changed content\n")

    report = check_dataset(evaluation_root)

    assert not report.passed
    assert "hash" in " ".join(report.errors).lower()


def test_duplicate_document_ids_are_rejected(evaluation_root: Path) -> None:
    path = evaluation_root / "manifest.json"
    manifest = read_json(path)
    manifest["documents"][1]["id"] = manifest["documents"][0]["id"]
    write_json(path, manifest)

    assert "duplicate" in " ".join(check_dataset(evaluation_root).errors).lower()


@pytest.mark.parametrize("bad_path", ["../private.md", "/tmp/private.md", "cases/answers.json"])
def test_source_allowlist_cannot_read_outside_corpus(evaluation_root: Path, bad_path: str) -> None:
    path = evaluation_root / "manifest.json"
    manifest = read_json(path)
    manifest["documents"][0]["path"] = bad_path
    write_json(path, manifest)

    assert not check_dataset(evaluation_root).passed


def test_symlink_cannot_escape_dataset(evaluation_root: Path) -> None:
    outside = evaluation_root.parent / "outside.md"
    outside.write_text("Not corpus material\n")
    source = evaluation_root / "corpus/square.en.md"
    source.unlink()
    source.symlink_to(outside)

    report = check_dataset(evaluation_root)

    assert not report.passed
    assert "outside" in " ".join(report.errors).lower()


def test_unknown_evidence_is_rejected(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["required_evidence_ids"] = ["unknown-source"]
    write_json(path, cases)

    assert "evidence" in " ".join(check_dataset(evaluation_root).errors).lower()


def test_unknown_selected_collection_is_rejected(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["selected_collections"] = ["another-collection"]
    write_json(path, cases)

    assert "collection" in " ".join(check_dataset(evaluation_root).errors).lower()


def test_evidence_cannot_cross_known_selected_collections(evaluation_root: Path) -> None:
    manifest_path = evaluation_root / "manifest.json"
    manifest = read_json(manifest_path)
    alternate = dict(manifest["documents"][0])
    alternate.update(
        id="alternate-en", collection="another-collection", path="corpus/alternate.en.md"
    )
    (evaluation_root / alternate["path"]).write_bytes(
        (evaluation_root / "corpus/square.en.md").read_bytes()
    )
    manifest["documents"].append(alternate)
    write_json(manifest_path, manifest)
    case_path = evaluation_root / "cases/smoke.json"
    cases = read_json(case_path)
    cases[0]["selected_collections"] = ["another-collection"]
    write_json(case_path, cases)

    report = check_dataset(evaluation_root)

    assert not report.passed
    assert "evidence outside selected collection" in " ".join(report.errors)


def test_translated_case_cannot_use_wrong_language_evidence(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[1]["required_evidence_ids"] = ["square-en"]
    write_json(path, cases)

    assert "language" in " ".join(check_dataset(evaluation_root).errors).lower()


def test_multi_source_case_needs_distinct_evidence(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["tags"] = ["multi_source"]
    write_json(path, cases)

    assert not check_dataset(evaluation_root).passed


def test_conflict_case_needs_two_sources(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["category"] = "conflicting_evidence"
    cases[0]["expected_status"] = "conflicting_evidence"
    write_json(path, cases)

    assert not check_dataset(evaluation_root).passed


def test_annotation_changes_change_the_fingerprint(evaluation_root: Path) -> None:
    original = check_dataset(evaluation_root).fingerprint
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["reference_answer"] += " Reviewed wording."
    write_json(path, cases)

    assert check_dataset(evaluation_root).fingerprint != original


def test_manifest_coverage_is_enforced(evaluation_root: Path) -> None:
    path = evaluation_root / "manifest.json"
    manifest = read_json(path)
    manifest["expected_counts"]["cases"] = 30
    write_json(path, manifest)

    assert not check_dataset(evaluation_root).passed


def test_numeric_targets_must_agree_across_translations(evaluation_root: Path) -> None:
    path = evaluation_root / "cases/smoke.json"
    cases = read_json(path)
    cases[0]["numeric_answer"] = {"value": 5, "unit": "unitless", "tolerance": 0}
    cases[1]["numeric_answer"] = {"value": 6, "unit": "unitless", "tolerance": 0}
    write_json(path, cases)

    assert not check_dataset(evaluation_root).passed


def test_malformed_json_is_a_validation_report(evaluation_root: Path) -> None:
    (evaluation_root / "cases/smoke.json").write_text("not json")

    report = check_dataset(evaluation_root)

    assert not report.passed
    assert report.status == "invalid"
    assert report.errors


def test_review_packet_includes_sources_and_reference_answers(evaluation_root: Path) -> None:
    text = render_review(load_dataset(evaluation_root))

    assert "pending_human_review" in text
    assert "What is a square?" in text
    assert "A rectangle with four equal sides." in text
    assert "corpus/square.en.md" in text
