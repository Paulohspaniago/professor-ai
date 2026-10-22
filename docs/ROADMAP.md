# Professor AI Roadmap

Planning baseline: 2026-10-22. Maintainer-owned, community-contributed, MIT-licensed. This roadmap tracks intended work; only explicitly checked stories are complete.

## Outcome and scope

Help a student ask questions about selected local learning materials and receive a useful, traceable answer or a clear explanation of missing evidence. Success means a reproducible local setup, reliable document lifecycle, measured retrieval and answer quality, a responsive interface, and contributions that can be reviewed independently.

The MVP targets one local user on the maintainer's reported Apple M4-family MacBook with 16 GB RAM. It covers English and Brazilian Portuguese, multiple subject collections, text PDFs/Markdown/TXT, and text-based conceptual questions and exercises. iPhone, OCR, image questions, model fine-tuning, and multi-user hosting are outside the first release.

The [architecture](ARCHITECTURE.md), [model shortlist](MODELS.md), and [evaluation gates](EVALUATION.md) define the technical contract. Numeric targets remain proposals until measured. No roadmap item is a guarantee of answer correctness on arbitrary exams.

## Milestones and order

| Milestone | Deliverable | Required stories | Exit evidence |
| --- | --- | --- | --- |
| M0 — Planning baseline | English documentation, design, backlog, MIT license | S01.01 | Documents agree and local links resolve |
| M1 — Reproducible foundation | Development setup, CI, community workflow, first real-model smoke run | S01.02–S01.04, S02.01–S02.02, S03.01–S03.02 | Fresh checkout works; CI passes; model artifacts are pinned |
| M2 — CLI vertical slice | Import materials, retrieve scoped evidence, answer with citations | S04.01–S04.03, all E05, S06.01–S06.03, S07.01–S07.03 | End-to-end local demo with success and refusal cases |
| M3 — Desktop alpha | Responsive UI and robust interactive requests | S03.03, S07.04, all E08 | Browser workflows pass; cancellation stops generation |
| M4 — Public MVP release | Evaluated, recoverable, offline application | S02.03–S02.04, S03.04, S04.04, S06.04, all E09 | Published quality, performance, restore, and offline reports |
| M5 — Teaching and content expansion | Qualified richer learning workflows | E10, selected by user demand | Each addition improves its targeted evaluation slice |
| M6 — Portability | Additional desktops, packaging, then iPhone feasibility | E11 | Platform-specific installation and performance evidence |

The repository can be published as a planning/experimental project once S01.04 is complete, before the application foundation. M4 publishes the first qualified application release. A public repository and a usable release are different deliverables.

The critical path is foundation → small evaluation set and runtime → storage → ingestion → retrieval → cited CLI answers → interface → release qualification. Evaluation grows alongside implementation. Optional experiments must not block the first vertical slice.

## Backlog conventions

- **P0:** required to meet an MVP milestone. **P1:** useful after the first release. **P2:** exploratory or conditional.
- **S / M / L:** relative effort, not promised dates. S is focused; M touches several components; L must be split into smaller issues before implementation.
- Checkboxes track accepted delivery. A story is ready when dependencies, acceptance criteria, sample inputs, and the affected contracts are understood.
- Copy a story into a GitHub issue using its stable ID. Add an owner, milestone, status, and links to its PR and validation evidence. Keep this document as the canonical scope until issue tracking exists.
- Keep one primary delivery story in progress per contributor. Pull a P1 item only after its dependencies and the current milestone's P0 work are covered.

## E01 — Foundation and community

**Outcome:** contributors can understand, run, verify, and propose changes to the project. **Priority:** P0. **Milestones:** M0–M1.

### S01.01 — Publish the planning baseline

- [x] As a contributor, I can understand the product, decisions, and delivery order before writing code.
- **Size:** S. **Dependencies:** none.
- **Acceptance:** English README, architecture, model shortlist, evaluation plan, epic/story roadmap, contribution guidance, and standard MIT license exist; planned features are identified as planned; documents link to one another.

### S01.02 — Bootstrap a reproducible local application

- [ ] As a developer, I can install the supported environment and run a diagnostic command from a fresh checkout.
- **Size:** M. **Dependencies:** S01.01.
- **Acceptance:** Python 3.12 and Node 22.12+ development requirements are explicit; uv and npm lockfiles are committed once their packages exist; a health endpoint and CLI diagnostic work without downloading a model; missing dependencies produce actionable messages; local data defaults outside the checkout.
- **Verification:** follow the [foundation implementation plan](plans/2026-10-22-foundation.md) on a clean checkout.

### S01.03 — Make automated checks useful to contributors

- [ ] As a maintainer, I receive deterministic feedback before merging a change.
- **Size:** M. **Dependencies:** S01.02.
- **Acceptance:** CI runs Python lint/format/type checks and behavior tests; frontend checks are added with the frontend; real-model tests are separately marked; no credentials or downloaded model are needed for the default suite; documentation links are checked.

### S01.04 — Launch the public contribution workflow

- [ ] As a contributor, I can open an issue or PR with enough context for review.
- **Size:** S. **Dependencies:** S01.01.
- **Acceptance:** create the public GitHub repository under the maintainer's chosen account; configure required documentation checks and branch protection where supported; add issue/PR templates, a code of conduct, SECURITY.md with a working private reporting route, and dependency update policy; label starter issues; document maintainer review and release authority; scan the initial tracked files for private data and large binaries before pushing. Application CI remains S01.03 and is added when application code exists.

## E02 — Evaluation and evidence

**Outcome:** development decisions are driven by repeatable measurements. **Priority:** P0. **Milestones:** M1 and M4.

### S02.01 — Create the first reviewed learning corpus

- [ ] As a developer, I can reproduce basic retrieval and answer failures using redistributable material.
- **Size:** M. **Dependencies:** S01.01.
- **Acceptance:** 30 reviewed smoke cases cover English, Portuguese, mathematics, physics, and computing; include missing evidence, conflicting sources, and multi-source questions; every source has provenance and distribution terms; questions and answer keys are kept out of the retrieval corpus.

### S02.02 — Build the evaluation runner

- [ ] As a contributor, I can run a fixed case set and inspect where the pipeline failed.
- **Size:** M. **Dependencies:** S01.02, S02.01.
- **Acceptance:** a CLI loads versioned cases and emits machine-readable results plus a readable report; fake providers test the runner before real inference exists; reports include stage timings, errors, selected evidence, and configuration fingerprints; failed cases stay in denominators.

### S02.03 — Freeze the MVP development and test partitions

- [ ] As a maintainer, I can evaluate changes on questions not used to tune the system.
- **Size:** L. **Dependencies:** S02.02.
- **Acceptance:** implement the 200-case, 100/100 split in [EVALUATION.md](EVALUATION.md); split by source/exercise family; balance languages; attach required evidence and grading rubrics; include novel exercises whose worked answers are absent from the corpus; hash and version the dataset.

### S02.04 — Produce an honest release evaluation

- [ ] As a user, I can see which subjects and failure modes were actually tested.
- **Size:** M. **Dependencies:** S02.03, S03.04, S07.04.
- **Acceptance:** publish raw counts, correctness, recall, citation support/coverage, abstention, per-language results, and known failures; record human review and disagreements; local LLM grading is advisory; publish only redacted, redistributable traces; a stable release requires the review policy in EVALUATION.md.

## E03 — Local models and runtime

**Outcome:** inference works reproducibly within the desktop resource budget. **Priority:** P0. **Milestones:** M1, M3, M4.

### S03.01 — Verify model artifacts and manifests

- [ ] As a user, I can obtain the expected model without guessing its origin or settings.
- **Size:** M. **Dependencies:** S01.02.
- **Acceptance:** verify one artifact for each of the three generator candidates and the embedding baseline; record upstream and conversion revisions, hashes, byte sizes, notices, tokenizer/template configuration, and runtime requirements; downloads are explicit, resumable, and checksum-verified; insufficient disk space is detected before installation.

### S03.02 — Implement the local generation adapter

- [ ] As an application developer, I can request a response through one typed interface.
- **Size:** M. **Dependencies:** S03.01.
- **Acceptance:** manage a pinned native llama.cpp process on loopback; verify Metal and model compatibility; expose readiness, tokenization, streaming, timeout, and cancellation; report missing/corrupt model files; Qwen non-thinking configuration is validated; no cloud fallback exists.

### S03.03 — Bound concurrency and resource use

- [ ] As a student, I can keep using the interface during model work and cancel an unwanted response.
- **Size:** M. **Dependencies:** S03.02, S05.03.
- **Acceptance:** default to one active generation, a visible bounded queue, and batched ingestion; cancellation reaches the provider; shutdown cleans owned processes; test model crash and pressure scenarios; model changes do not leave unused copies resident.

### S03.04 — Choose the default model from measurements

- [ ] As a maintainer, I can justify the default with quality and performance evidence.
- **Size:** M. **Dependencies:** S02.03, S07.04.
- **Acceptance:** compare the three candidates with identical retrieved evidence, then the full pipeline; record warm/cold performance, memory, settings, and failures; select according to MODELS.md and release gates; leave the default undecided if all fail.

## E04 — Persistence and data lifecycle

**Outcome:** learning materials and their provenance survive updates and failures. **Priority:** P0. **Milestones:** M2 and M4.

### S04.01 — Implement the SQLite schema and migrations

- [ ] As a user, I can manage collections and documents without losing their relationships.
- **Size:** M. **Dependencies:** S01.02.
- **Acceptance:** implement collections, memberships, versioned documents/chunks, jobs, conversations, and migration ledger; enable foreign keys and controlled WAL writes; use parameterized queries; test migration from an older fixture and rollback of a failed write; detect unsupported SQLite/extension builds.

### S04.02 — Publish indexes atomically

- [ ] As a user, I can search the previous index while a replacement is being built.
- **Size:** M. **Dependencies:** S04.01.
- **Acceptance:** stage lexical/vector data under explicit generations; activate only complete versions; reject mismatched embedding fingerprints; resume or recover interrupted rebuilds; preserve a rollback path until cleanup; readers never receive mixed vector dimensions.

### S04.03 — Support correct update and deletion semantics

- [ ] As a user, I can replace or delete material and know which content remains searchable.
- **Size:** M. **Dependencies:** S04.02.
- **Acceptance:** unchanged content avoids duplicate work; collection removal preserves other memberships; global deletion removes originals, searchable data, cached responses and citation excerpts, and cancels related jobs; history identifies removed evidence; tests verify no stale retrieval results.

### S04.04 — Back up and restore a knowledge base

- [ ] As a user, I can move or recover my data with its provenance intact.
- **Size:** M. **Dependencies:** S04.03, S05.04.
- **Acceptance:** use a consistent SQLite backup with originals and a manifest; restore into a separate directory; verify hashes and supported schema; rebuild disposable indexes when necessary; fail safely on missing files or incompatible versions; test an actual restore rather than only backup creation.

## E05 — Document ingestion

**Outcome:** usable source content reaches the index with accurate locations. **Priority:** P0. **Milestone:** M2.

### S05.01 — Extract supported source formats

- [ ] As a student, I can import text PDFs, Markdown, and plain text with visible extraction results.
- **Size:** M. **Dependencies:** S04.01.
- **Acceptance:** retain PDF page indexes, headings and text locations; apply the architecture's file/page/time limits; reject corrupt/encrypted files with specific errors; scanned PDFs receive an OCR-needed state; empty or suspicious extraction is visible rather than silently accepted.

### S05.02 — Chunk without losing provenance

- [ ] As a student, I can trace a retrieved passage to the original material.
- **Size:** M. **Dependencies:** S05.01.
- **Acceptance:** implement deterministic structure-aware splitting with the documented token budgets; include prefixes/special tokens in length checks; preserve units, equations and section labels; maintain source offsets and hashes; test oversized paragraphs, accented text and page boundaries.

### S05.03 — Run resumable import jobs

- [ ] As a user, I can see progress and recover from an interrupted import.
- **Size:** M. **Dependencies:** S04.02, S05.02, S03.01.
- **Acceptance:** persist parsing/embedding/indexing progress; load the embedding model from local verified files; batch work outside the API event loop; cancellation and retry are idempotent; a crash or full disk cannot mark a partial document ready.

### S05.04 — Provide an inspectable ingestion workflow

- [ ] As a contributor, I can diagnose why a document produced poor search results.
- **Size:** S. **Dependencies:** S05.03.
- **Acceptance:** CLI inspection exposes extraction warnings, chunk count, page/section coverage and index fingerprint; duplicate import is a no-op unless configuration changes; file replacement creates a new version; tests exercise import → restart → query → replace → delete.

## E06 — Retrieval and ML algorithms

**Outcome:** the generator receives relevant, scoped, nonredundant evidence. **Priority:** P0. **Milestones:** M2 and M4.

### S06.01 — Implement lexical retrieval

- [ ] As a student, I can find passages containing exact subject terminology.
- **Size:** M. **Dependencies:** S05.03.
- **Acceptance:** FTS5/BM25 returns ranked chunk IDs with metadata; collection and active-version filters apply before top-k; query syntax is safely constructed; test Portuguese accents, abbreviations, dates, and mathematical symbols; empty queries and no matches are explicit states.

### S06.02 — Implement multilingual dense retrieval

- [ ] As a student, I can retrieve relevant material when my wording differs from the source.
- **Size:** M. **Dependencies:** S05.03.
- **Acceptance:** encode queries with the baseline's prescribed prefix and normalization; perform exact cosine search over the matching index generation and selected collections; compare scores/order against a small independent reference calculation; reject wrong dimensions and non-finite vectors.

### S06.03 — Fuse and select evidence

- [ ] As a student, I receive relevant evidence from semantic and lexical search together.
- **Size:** M. **Dependencies:** S06.01, S06.02.
- **Acceptance:** implement the documented RRF formula and stable tie order; deduplicate overlap; select at most six chunks within the generator-token budget; preserve citation IDs; out-of-scope high-scoring distractors cannot crowd out selected-collection results.

### S06.04 — Tune retrieval using ablations

- [ ] As a maintainer, I can demonstrate whether an added algorithm improves the system.
- **Size:** M. **Dependencies:** S06.03, S02.03.
- **Acceptance:** compare lexical-only, dense-only, and fused retrieval on development data; calibrate evidence sufficiency there; evaluate embedding alternatives, reranking, or MMR only when justified; record recall and latency tradeoffs; freeze settings before the release test; investigate ANN only if measured scale requires it.

## E07 — Grounded answers and CLI slice

**Outcome:** a complete local question-to-answer workflow with auditable sources. **Priority:** P0. **Milestones:** M2–M3.

### S07.01 — Assemble bounded, trustworthy context

- [ ] As a student, I receive an answer based on my selected materials and current question.
- **Size:** M. **Dependencies:** S06.03, S03.02.
- **Acceptance:** count actual generator tokens; fit evidence, question, instructions and bounded history into the context budget; treat source instructions as data; preserve answer choices; separate `answered`, `insufficient_evidence`, and `conflicting_evidence`; record the development-calibrated evidence-policy version; stale history cannot act as source evidence.

### S07.02 — Stream answers and validate references

- [ ] As a student, I can read an answer progressively and inspect its supporting passages.
- **Size:** M. **Dependencies:** S07.01.
- **Acceptance:** use the architecture's ordered stream and terminal states; resolve source IDs to supplied excerpts and page/section locations; mark draft output as provisional; invalid citations and timeouts do not produce a completed state; validation is described as structural, not a proof of factual correctness.

### S07.03 — Deliver the first end-to-end CLI demo

- [ ] As a contributor, I can reproduce the whole pipeline before a UI is available.
- **Size:** M. **Dependencies:** S07.02, S05.04, S02.02.
- **Acceptance:** one documented workflow imports a licensed example, selects collections, answers a covered question with citations, refuses an uncovered question, and survives a restart; runs offline with installed artifacts; CI covers orchestration with a fake model and a recorded manual run covers real inference.

### S07.04 — Explain text-based exercises

- [ ] As a student, I receive a concise worked solution that distinguishes cited principles from derived results.
- **Size:** M. **Dependencies:** S07.03.
- **Acceptance:** preserve alternative labels; state assumptions and units; cite relevant definitions/formulas; avoid inventing a source for a derived answer; identify missing givens or ambiguous questions; grade calculations and explanations against human rubrics in both languages.

## E08 — Responsive learning interface

**Outcome:** students can use the validated pipeline comfortably. **Priority:** P0. **Milestone:** M3.

### S08.01 — Manage collections and imports visually

- [ ] As a student, I can organize learning materials and understand import progress.
- **Size:** M. **Dependencies:** S05.04, S01.03.
- **Acceptance:** typed API client, collection selection, upload progress, extraction warnings, retry/cancel, and deletion are available; original names are displayed safely; status survives a browser refresh; ready and incomplete documents are distinguishable.

### S08.02 — Build the streaming study chat

- [ ] As a student, I can ask a question, see progress, and stop generation.
- **Size:** M. **Dependencies:** S08.01, S07.02, S03.03.
- **Acceptance:** show queued/retrieving/generating/validating states; preserve drafts; cancel provider work; handle disconnect/reconnect without duplicate answers; render model output as sanitized content; excessive or failed requests produce usable recovery actions.

### S08.03 — Make evidence inspectable

- [ ] As a student, I can verify a claim in the cited material.
- **Size:** M. **Dependencies:** S08.02.
- **Acceptance:** citations open an evidence panel with excerpt, source title, collection and page/section; PDF page indexes and printed labels are distinguished; removed sources are clearly marked; conflicting evidence is shown side by side; keyboard users can open and close the panel.

### S08.04 — Qualify responsiveness, accessibility, and language

- [ ] As a student, I can study comfortably across screen sizes and input methods.
- **Size:** M. **Dependencies:** S08.03, S07.04.
- **Acceptance:** browser tests cover 360/768/1440 px layouts, long filenames and equations; keyboard focus, accessible labels, contrast, reduced motion, and screen-reader status updates are reviewed; English and pt-BR resources exist; math rendering and fonts work offline; import/generation do not freeze local controls.

## E09 — Reliability and public MVP release

**Outcome:** a release can be installed, evaluated, recovered, and maintained. **Priority:** P0. **Milestone:** M4.

### S09.01 — Verify offline and local-access boundaries

- [ ] As a user, I can use my materials without sending them to external services.
- **Size:** M. **Dependencies:** S08.04.
- **Acceptance:** after explicit setup downloads, import/search/answer/UI work with external network access disabled; all application/model servers bind to loopback; host/origin/session checks reject foreign requests; parser/model inputs cannot invoke shell commands or remote URLs; default logs omit private text.

### S09.02 — Exercise recovery and failure paths

- [ ] As a user, I can recover from interrupted work without a corrupted knowledge base.
- **Size:** M. **Dependencies:** S09.01, S04.04.
- **Acceptance:** simulate disk exhaustion, parser timeout, model crash, interrupted rebuild, stale client, and incompatible schema; transactions preserve consistency; errors contain useful next actions; restore and deletion tests prove no stale evidence is exposed.

### S09.03 — Meet the resource and latency gates

- [ ] As a user, I can understand expected performance on the reference computer.
- **Size:** M. **Dependencies:** S09.02, S03.04, S06.04.
- **Acceptance:** measure the exact workload, warm/cold conditions, p95 retrieval, first-token latency, throughput, cancellation, memory, and sustained session described in EVALUATION.md; profile failures; publish methodology and limitations; never infer local performance from unrelated hardware.

### S09.04 — Publish a reproducible MVP release

- [ ] As a new user, I can follow setup instructions and reproduce the example workflow.
- **Size:** M. **Dependencies:** S09.03, S02.04.
- **Acceptance:** clean-checkout installation and the example run pass on reference hardware; release artifacts and model manifests have checksums and notices; publish changelog, supported-platform matrix, known limitations and evaluation report; provide migration/rollback instructions; smoke-test the packaged release before tagging it stable.

## E10 — Teaching and content expansion

**Outcome:** expand useful learning capabilities only after the core is measured. **Priority:** P1. **Milestone:** M5.

### S10.01 — Check arithmetic with bounded tools

- [ ] As a student, I can receive a numerically checked solution where the exercise permits it.
- **Size:** M. **Dependencies:** S09.04.
- **Acceptance:** use an allowlisted expression grammar, numeric/unit rules and time limits; do not execute arbitrary code; show what was checked; compare against the exercise baseline; unsupported symbolic problems receive an explicit limitation.

### S10.02 — Add optional hints and multi-source question decomposition

- [ ] As a student, I can request a hint or an explanation that connects multiple supplied concepts.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** hint mode avoids disclosing the final answer until requested; decomposition has a bounded retrieval-call budget; citations retain their origin; evaluate learning usefulness and correctness separately; avoid changing the default answering path without comparison.

### S10.03 — Qualify scanned documents and image questions

- [ ] As a student, I can import a scanned page and inspect the extracted content before relying on it.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** compare local OCR/layout approaches such as Docling and alternatives under the resource budget; preserve page coordinates and flag uncertain extraction; evaluate tables, formulas and reading order; qualify any vision model separately; never label OCR output as verified fact.

### S10.04 — Add DOCX and portable knowledge packs

- [ ] As a contributor, I can distribute a versioned collection of reusable learning material.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** parse DOCX paragraphs/tables with provenance; knowledge packs include source licenses, hashes and schema/model fingerprints; imports reject incompatible or unsafe paths; rebuild indexes when required; separately test DOCX parsing and pack import/export before combining releases.

## E11 — Platform expansion and iPhone

**Outcome:** support more devices with explicit evidence for each environment. **Priority:** P1/P2. **Milestone:** M6.

### S11.01 — Qualify Linux and Windows desktop paths

- [ ] As a contributor on another desktop OS, I can install the project and run its examples.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** validate native sqlite-vec and model runtime installation; add platform CI and clean-machine setup checks; distinguish CPU and GPU performance profiles; publish supported combinations and platform-specific failures.

### S11.02 — Evaluate native desktop packaging

- [ ] As a student, I can launch the application without manually starting servers.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** compare packaging approaches with install size, updates, process lifecycle and license obligations; bundle local UI assets; keep models/data outside immutable app assets; support uninstall without silently deleting user material; document signing and update provenance before distribution.

### S11.03 — Run an on-device iPhone feasibility study

- [ ] As a maintainer, I can decide whether an iPhone version meets a useful quality and responsiveness bar.
- **Size:** L. **Dependencies:** S09.04.
- **Acceptance:** benchmark actual target devices with compact models, embeddings, and the same evaluation fixtures; measure RAM, thermals, battery, offline behavior, and cancellation; compare Swift/runtime integrations; produce an explicit go/no-go decision and a separate mobile design. A phone browser connected to the Mac does not count as local iPhone inference.

### S11.04 — Implement the qualified iPhone scope

- [ ] As a student, I can study from a compatible knowledge pack while offline on a supported iPhone.
- **Size:** L. **Dependencies:** S11.03 with a go decision, S10.04.
- **Acceptance:** port the qualified contracts and storage interchange format; support compatible pack import, local retrieval/generation and citations; measure on-device gates; document supported devices and desktop/mobile differences; release only the scope proven by the feasibility study.

## First delivery sequence

Start with S01.02 and S01.03 using the [foundation plan](plans/2026-10-22-foundation.md). Prepare S02.01 alongside that work. Then qualify S03.01/S03.02 and implement storage and ingestion before retrieval. Stop expanding features until S07.03 provides a real local end-to-end demo.

Large later stories are roadmap commitments to investigate a capability, not implementation-ready specifications. Split them only when prerequisites are complete and the relevant evidence is available.

## Definition of done

A story is accepted when its behavior and failure paths meet the acceptance criteria, meaningful checks pass, affected documentation is updated, and a reviewer can reproduce its evidence. Model-quality claims need a versioned evaluation; performance claims need hardware measurements. A UI screenshot alone does not complete a backend story, and a mock-only test does not qualify a model.

## Risks and responses

| Risk | Response | Owning stories |
| --- | --- | --- |
| Plausible answers unsupported by sources | Human citation grading, calibrated refusal, explicit derived explanations | S02.04, S06.04, S07.01–S07.04 |
| Small model cannot solve target exercises | Compare model sizes; narrow scope based on failed cases | S03.04, S07.04 |
| 16 GB resource budget is exceeded | Bounded context/concurrency; native inference; measured default selection | S03.03–S03.04, S09.03 |
| PDF structure or formulas are damaged | Extraction inspection and unsupported-content warnings | S05.01–S05.04, S10.03 |
| Native vector extension breaks on upgrade | Pinned versions, disposable generations, migration/restore tests | S04.01–S04.04 |
| Benchmarks overstate quality | Frozen splits, source-family separation, human review and failure counts | S02.01–S02.04 |
| Community cannot reproduce development | Lockfiles, model-free CI, public starter stories | S01.02–S01.04 |
| Roadmap grows faster than delivery | One vertical slice first; enforce milestone dependencies | Maintainer, all epics |

## Operating cadence

At each milestone, review failed evaluation cases and contributor friction, update priorities, and record decisions. Prefer a working demonstration over expanding the backlog. Estimate calendar dates after M1 reveals actual setup and model constraints; relative sizes in this roadmap are intentionally not delivery promises.
