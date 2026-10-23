"""Check the committed smoke dataset without running a model or fetching sources."""

from collections import Counter
from pathlib import Path

from professor_ai.evaluation.fixtures import check_dataset, load_dataset, render_review

ROOT = Path(__file__).resolve().parents[2] / "evals"


def test_smoke_dataset_covers_the_agreed_scenarios() -> None:
    bundle = load_dataset(ROOT)
    assert check_dataset(ROOT).passed
    assert len(bundle.cases) == 30
    assert len(bundle.manifest.documents) == 36
    assert Counter(c.language for c in bundle.cases) == {"en": 15, "pt-BR": 15}
    assert Counter(c.subject for c in bundle.cases) == {
        "computer_science": 10,
        "mathematics": 10,
        "physics": 10,
    }
    assert Counter(c.category for c in bundle.cases) == {
        "conceptual": 8,
        "derivation": 10,
        "insufficient_evidence": 6,
        "conflicting_evidence": 6,
    }
    assert sum("multi_source" in c.tags for c in bundle.cases) == 6
    for doc in bundle.manifest.documents:
        assert doc.kind == "fictional_record" or doc.references
        assert doc.license == "MIT"


def test_review_packet_matches_the_checked_annotations() -> None:
    assert (ROOT / "REVIEW.md").read_text(encoding="utf-8") == render_review(load_dataset(ROOT))
