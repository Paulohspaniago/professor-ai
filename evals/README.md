# Development smoke corpus

This is a small, original learning fixture for building the evaluation harness.
It contains **30 case proposals**, grouped into 15 English/Brazilian Portuguese
translation families, and **36 short source documents**. Computing, mathematics,
and physics each have ten cases. All initial cases are pending human review.
This is not a frozen test set, a model benchmark, or evidence of answer quality.

Read the [review packet](REVIEW.md) alongside the original sources before approving
any case. The [evaluation design](../docs/EVALUATION.md) defines the later release
evaluation; these development fixtures do not count toward its held-out 200 cases.

## Layout and retrieval boundary

- [manifest.json](manifest.json) is the only source allowlist. Each entry has a
  stable evidence ID, collection, subject, language, MIT terms, authorship,
  SHA-256 hash, and corroborating primary references/check dates where applicable.
- `corpus/` contains only original Markdown notes or clearly fictional records.
  Each short document is one evidence unit; there is no chunker yet.
- [cases/smoke.json](cases/smoke.json) contains questions, expected statuses,
  reference answers, rubrics, evidence IDs, optional numeric targets, and reviews.
- [REVIEW.md](REVIEW.md) is a deterministic human-readable view of the annotations.

A future ingestion adapter must read **only manifest-listed corpus files**.
Never ingest the whole `evals/` directory, annotations, reference answers, rubrics,
or review packet. Load only the selected collections and the case language.
Collection IDs here are logical fixture names, not application database IDs.
The six fictional conflict records live in separate collections so they cannot
contaminate ordinary learning questions. Do not retrieve external reference URLs:
they establish provenance, not additional answer evidence for these cases.

## Provenance and redistribution

All committed learning text and annotations are AI-assisted original contributions
under the repository's [MIT license](../LICENSE). They are proposals requiring
human factual and bilingual review. No exam questions or textbook passages were
copied. External primary-source URLs corroborate principles; their content retains
its own terms and is neither bundled nor relicensed. Invented configurations and
measurements are explicitly labeled fictional and have no external factual claim.
For the conflict tasks, the desired behavior is to expose the disagreement rather
than prefer one equally authoritative record.

## Validate and review

From the repository root after `uv sync --locked --dev`:

```bash
uv run python scripts/check_evals.py --check-review-packet
uv run python scripts/check_evals.py --json
uv run python scripts/check_evals.py --require-reviewed
```

Structural checks pass for valid drafts. The explicit `--require-reviewed` gate
fails while any case is pending or has changes requested. A successful recorded
review gate validates attribution metadata; it cannot authenticate the reviewer
or prove semantic correctness. No command runs an LLM or computes accuracy.

A human reviewer must verify every question, answer, calculation, rubric, evidence
link, source note, and both language versions. For insufficient-evidence cases,
inspect **all notes in the selected collection and language**, not just an empty
evidence list. Numeric tolerances are zero for these exact arithmetic exercises;
rubric text expresses semantic criteria, not substring scoring rules.

Record an explicit review in a PR, then update each reviewed case's `review` with
`status: approved`, a real reviewer identity, `reviewed_on: YYYY-MM-DD`, and notes.
Use `changes_requested` with the reviewer/date when corrections remain. Do not
invent a reviewer, infer review from a generic request to continue, or treat an AI
code review as human approval. S02.01 remains open until this review is complete.

After editing source text, update its manifest hash. Changes to a case **or any
source in its selected collections/language** require another human review: reset
affected review records to `pending_human_review` with null identity/date. The
current schema does not enforce review invalidation automatically; reviewers
must check the PR diff. Regenerate the packet and commit it with the annotations:

```bash
uv run python scripts/check_evals.py --write-review-packet
uv run python scripts/check_evals.py --check-review-packet
```

The dataset fingerprint covers manifest and annotation bytes; source hashes bind
the allowlisted content. It changes when any annotation or recorded source hash
changes. Review packets therefore go stale on those changes. Hashes detect
inconsistent edits, not malicious edits to both the source and manifest.
