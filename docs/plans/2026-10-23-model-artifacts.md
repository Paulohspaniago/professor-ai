# Model Artifacts Implementation Plan

> **For agentic workers:** Use superpowers:executing-plans, with a fresh whole-branch review after all tasks.

**Goal:** Pin the three generator candidates and E5 baseline, and provide explicit, resumable, checksum-verified acquisition without loading models.

**Architecture:** A packaged JSON catalog records immutable publisher references and declared settings. An HTTPX downloader stages one artifact under a lock, validates every byte count/hash, and publishes the complete directory atomically. Read-only CLI commands inspect the catalog and verify local installations.

**Tech Stack:** Python 3.12, existing Pydantic/Typer, HTTPX promoted from development to runtime dependencies, and standard-library hashing/filesystem operations.

**Spec:** [S03.01](../ROADMAP.md#s0301--verify-model-artifacts-and-manifests), [model policy](../MODELS.md), and [architecture](../ARCHITECTURE.md).

## Design decisions and scope

- Builder decision: use immutable LM Studio GGUF distributions and upstream E5 safetensors rather than converting full-precision models in this task. Publisher metadata supplies weight sizes/digests; small configuration/notice files are fetched and hashed during research.
- Publisher metadata is not a local weight verification or runtime smoke test. The catalog records this limitation. No multi-gigabyte model is automatically downloaded or loaded during development/tests.
- Converted model cards identify base repositories but do not attest exact source commits. Independently pinned upstream reference commits are recorded without claiming reproducible conversion ancestry.
- Pin llama.cpp v0.7.0/commit and Sentence Transformers 6.2.0 as proposed runtime references; compatibility, Metal operation, embedded GGUF template comparison, and inference remain S03.02/later adapter work.
- Each immutable artifact installation is keyed by its complete catalog-entry fingerprint. Partial files have a distinct suffix; a cooperative per-artifact lock prevents concurrent writers. Invalid existing installations are preserved and rejected.
- HTTPX provides verified TLS, bounded streaming and test transports. No credentials, remote Python code, cloud inference, or automatic model selection are introduced.

## Global Constraints

- Keep all existing tests/checks, local API behavior, and human corpus review records unchanged.
- Code/technical documentation is English; no model binaries enter Git.
- All remote files use Hugging Face repositories plus 40-hex commits; SHA-256 is 64 hex and sizes are positive integers.
- Model/license/config file paths cannot escape their managed directories or alias internal metadata; reject symlink components.
- Check free disk before installation, reserve 64 MiB, preserve interrupted partials, validate HTTP Range responses, and never publish checksum failures.
- Downloads happen only through `professor-ai models fetch`; list/inspect/verify never connect to a network.
- Use network-blocked tests and small in-memory HTTP transports; runtime qualification stays pending.

## Review Focus

- A server ignores Range, returns a wrong range, truncates a stream, or changes content: resume safely or reject, and never publish invalid bytes.
- File paths, symlinked parents, and an existing invalid installation must not cause unintended overwrites.
- A process is interrupted or a concurrent fetch starts: retain resumable state, release owned locks on ordinary failure, and reject another writer.
- Catalog revisions, source references, hashes, or file layouts change: change the installation fingerprint and preserve old snapshots.
- Metadata-only pins, missing notices, or untested runtime settings must never be advertised as locally verified, installed, or inference-ready.

## Task 1: Typed catalog and pinned research data

**Files:** create `src/professor_ai/model_artifacts/{__init__.py,catalog.py,catalog.json}`, `tests/unit/test_model_catalog.py`, and shared test fixtures.

**Interfaces:** `load_catalog(path: Path | None = None) -> Catalog`, `find_artifact(catalog, artifact_id: str) -> Artifact`, `artifact_fingerprint(artifact: Artifact) -> str`. File records contain immutable source, remote/destination paths, size, digest, and weight/notice/config purpose. Artifact records contain role, upstream/distribution references, license evidence, runtime/settings, provenance limitation, and verification status.

- [x] Test immutable revisions/hashes, safe paths, duplicate IDs/destinations, file-versus-directory collisions, fingerprint changes, unknown IDs, and all four bundled candidates.
- [x] Run focused tests; expect missing implementation.
- [x] Implement contracts and package the researched catalog. Promote HTTPX and regenerate the lock with uv. No existing version is intentionally upgraded.
- [x] Run catalog tests, full suite, Ruff and mypy; expect passing. Commit catalog/contracts.

## Task 2: Resumable acquisition and local verification

**Files:** create `model_artifacts/store.py`, `transfer.py`, and `tests/unit/test_model_downloads.py`.

**Interfaces:** `fetch_artifact(artifact: Artifact, root: Path, *, client: httpx.Client | None = None) -> InstallReport` and `verify_artifact(artifact, root) -> InstallReport`. Install reports distinguish missing/invalid/verified local files from runtime qualification. Transfer helpers are private to the package.

- [x] Test successful hash/notice installation, idempotent verified re-fetch without network, interruption/resume, ignored Range restart, bad ranges/size/hash/encoding, HTTPS redirect policy, disk exhaustion before network, locks, corrupt existing installs, and symlink refusal.
- [x] Run focused tests; expect missing implementation.
- [x] Implement bounded streaming, immutable staging, cooperative lock, disk preflight, verified receipt, and atomic directory publication. Verify local bytes read-only without trusting a receipt alone.
- [x] Run full suite and quality gates; expect passing. Commit acquisition/verification.

## Task 3: Explicit CLI and contributor handoff

**Files:** create `model_artifacts/command.py`, CLI integration tests, and `docs/MODEL_ARTIFACTS.md`; modify CLI composition, MODELS.md, ROADMAP.md, DEVELOPMENT.md, and README.md.

**Interfaces:** `professor-ai models list|inspect ID|verify ID|fetch ID`. Each command supports `--json` and optional `--catalog`; verify/fetch accept `--directory`, defaulting to the application's data directory under `models/`. Exit 0 succeeds; 1 reports missing/invalid local artifacts or transfer failures; 2 rejects invalid catalog/configuration. No model runtime is executed.

- [x] Test read-only list/inspect/verify, explicit tiny-artifact fetch through a test transport, unknown IDs, corrupt catalogs, valid JSON errors, and unchanged missing-model health semantics.
- [x] Run CLI tests; expect absent command.
- [x] Implement thin CLI commands and document provenance, settings, bytes, notices, verification levels, partial/lock recovery, and remaining qualification. Preserve upstream terms without relicensing weights.
- [x] Run all gates, inspect offline CLI output, build a wheel and verify bundled catalog inclusion. Commit CLI/docs.

## Handoff

Obtain a fresh whole-branch review, fix Important/Critical findings with regression
tests, publish a focused S03.01 issue/PR and inspect hosted CI. Keep the story open
for unperformed local-weight/runtime qualification and un-attested conversion
ancestry. No automatic merge or multi-gigabyte download is part of this handoff.

## Review outcome

A fresh reviewer checked the whole implementation and all 30 catalog file records
against cached source bytes or pinned publisher LFS metadata. The review identified
partial hardlink overwrites, malformed staged receipts escaping JSON output, and
publication of unlisted staging entries. Each has a regression that failed before
its fix and passed afterward. Case aliases were treated as Important because they
can waste large transfers or miscount files on the primary macOS platform; custom
catalogs now require portable, consistent path spelling. The final local suite
passes 152 tests with formatting, lint, strict typing, documentation, and evaluation
packet checks. There are no deferred minor findings from this review.

Real weights, inference/Metal, tokenizer/template behavior, conversion ancestry,
E5 notice qualification, live CDN behavior, power-loss durability, and hostile
concurrent filesystem mutation were outside this review's evidence. Integrity
mechanics and publisher pins do not establish model/runtime qualification.
