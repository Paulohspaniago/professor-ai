"""Load only manifest-allowlisted evidence; keep answer annotations separate."""

import hashlib
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from pydantic import TypeAdapter, ValidationError

from professor_ai.evaluation.models import Case, Manifest, ValidationReport


@dataclass(frozen=True)
class DatasetBundle:
    manifest: Manifest
    cases: list[Case]
    fingerprint: str


def dataset_path(root: Path, relative: str, directory: str | None = None) -> Path:
    """Reject traversal and symlink escape before reading any target bytes."""
    part = PurePosixPath(relative)
    if part.is_absolute() or ".." in part.parts or "\\" in relative:
        raise ValueError(f"path outside dataset: {relative}")
    if directory and (not part.parts or part.parts[0] != directory):
        raise ValueError(f"path must be inside {directory}: {relative}")
    target = (root / relative).resolve()
    allowed = (root / directory).absolute() if directory else root.resolve()
    if not target.is_relative_to(allowed):
        raise ValueError(f"path outside dataset area: {relative}")
    return target


def _unique(values: list[str], name: str) -> None:
    if len(values) != len(set(values)):
        raise ValueError(f"duplicate {name}")


def load_dataset(root: Path) -> DatasetBundle:
    root = root.resolve()
    manifest_bytes = dataset_path(root, "manifest.json").read_bytes()
    manifest = Manifest.model_validate_json(manifest_bytes)
    case_bytes = dataset_path(root, manifest.case_file, "cases").read_bytes()
    cases = TypeAdapter(list[Case]).validate_json(case_bytes)
    _unique([doc.id for doc in manifest.documents], "document IDs")
    _unique([doc.path for doc in manifest.documents], "document paths")
    _unique([case.id for case in cases], "case IDs")
    documents = {doc.id: doc for doc in manifest.documents}
    for doc in manifest.documents:
        path = dataset_path(root, doc.path, "corpus")
        if path.suffix != ".md":
            raise ValueError(f"source must be Markdown: {doc.path}")
        if hashlib.sha256(path.read_bytes()).hexdigest() != doc.sha256:
            raise ValueError(f"source hash mismatch: {doc.id}")
    families: dict[str, list[Case]] = defaultdict(list)
    for case in cases:
        families[case.family_id].append(case)
        for collection in case.selected_collections:
            if not any(
                d.collection == collection
                and d.language == case.language
                and d.subject == case.subject
                for d in manifest.documents
            ):
                raise ValueError(f"unknown collection/language/subject in {case.id}: {collection}")
        for evidence in case.required_evidence_ids:
            if evidence not in documents:
                raise ValueError(f"unknown evidence in {case.id}: {evidence}")
            doc = documents[evidence]
            if doc.collection not in case.selected_collections:
                raise ValueError(f"evidence outside selected collection: {case.id}")
            if doc.language != case.language or doc.subject != case.subject:
                raise ValueError(f"evidence language/subject mismatch: {case.id}")
    for family, pair in families.items():
        if len(pair) != 2 or {c.language for c in pair} != {"en", "pt-BR"}:
            raise ValueError(f"family needs exactly two language versions: {family}")
        for field in (
            "subject",
            "category",
            "expected_status",
            "numeric_answer",
            "tags",
            "selected_collections",
        ):
            if getattr(pair[0], field) != getattr(pair[1], field):
                raise ValueError(f"translation {field} mismatch: {family}")
    counts = manifest.expected_counts
    if (
        len(cases) != counts.cases
        or Counter(c.language for c in cases) != counts.languages
        or Counter(c.subject for c in cases) != counts.subjects
    ):
        raise ValueError("actual coverage differs from manifest expected_counts")
    fingerprint = hashlib.sha256(manifest_bytes + b"\0" + case_bytes).hexdigest()
    return DatasetBundle(manifest, cases, fingerprint)


def check_dataset(root: Path, *, require_reviewed: bool = False) -> ValidationReport:
    try:
        bundle = load_dataset(root)
    except (OSError, ValueError, RuntimeError, ValidationError) as error:
        return ValidationReport(passed=False, status="invalid", errors=[str(error)])
    pending = [case.id for case in bundle.cases if case.review.status != "approved"]
    return ValidationReport(
        passed=not (require_reviewed and pending),
        status=(
            "human_reviewed"
            if not pending
            else "review_required"
            if require_reviewed
            else "valid_draft"
        ),
        case_count=len(bundle.cases),
        document_count=len(bundle.manifest.documents),
        reviewed_case_count=len(bundle.cases) - len(pending),
        unreviewed_case_ids=pending,
        fingerprint=bundle.fingerprint,
    )


def render_review(bundle: DatasetBundle) -> str:
    """Render the same annotations CI validates; this never records approval."""
    lines = [
        "# Smoke corpus review packet",
        "",
        "Generated from the manifest and case annotations. Review the original notes too.",
        "These are development proposals until a named human approves each case.",
        "",
        f"Dataset: `{bundle.manifest.dataset_id}`. Split: `{bundle.manifest.split}`.",
        "",
        f"Fingerprint: `{bundle.fingerprint}`",
        "",
        "## Sources",
        "",
    ]
    for doc in bundle.manifest.documents:
        lines += [
            f"- `{doc.id}`: [{doc.title}]({doc.path}) — {doc.language}, "
            f"`{doc.collection}`, {doc.kind}, {doc.license}."
        ]
    lines += [
        "",
        "## Cases",
        "",
        "For insufficient-evidence cases, inspect every source in the selected collection",
        "and language to confirm the requested information is absent.",
        "",
    ]
    for case in bundle.cases:
        lines += [
            f"### {case.id}",
            "",
            f"Review: `{case.review.status}`. "
            f"Reviewer: {case.review.reviewer or '—'}. "
            f"Date: {case.review.reviewed_on or '—'}.",
            "",
            f"Language: {case.language}. Category: `{case.category}`. "
            f"Tags: {', '.join(case.tags) or 'none'}.",
            "",
            f"Selected collections: {', '.join(case.selected_collections)}.",
            "",
            f"**Question:** {case.question}",
            "",
            f"**Expected status:** `{case.expected_status}`",
            "",
            f"**Reference answer:** {case.reference_answer}",
            "",
            "**Required evidence:**",
        ]
        lines += [f"- `{item}`" for item in case.required_evidence_ids] or ["- None."]
        lines += ["", "**Must include:**"]
        lines += [f"- {item}" for item in case.rubric.must_include]
        lines += ["", "**Must not include:**"]
        lines += [f"- {item}" for item in case.rubric.must_not_include] or [
            "- No extra exclusions."
        ]
        if case.missing_information:
            lines += ["", "**Missing information:** " + "; ".join(case.missing_information)]
        if case.numeric_answer:
            n = case.numeric_answer
            lines += ["", f"**Numeric target:** {n.value:g} {n.unit}; tolerance {n.tolerance:g}."]
        if case.review.notes:
            lines += ["", f"**Review notes:** {case.review.notes}"]
        lines += [""]
    return "\n".join(lines)
