# Evaluation and Release Gates

Status: proposed targets, 2026-10-22. No measurements have been collected. Gates below define evidence needed for a release; they are not advertised capabilities.

## Dataset design

Begin with 30 human-reviewed smoke cases to develop the CLI slice. Before the public MVP release, expand to 200 cases across computer science, mathematics, and physics, balanced between English and Brazilian Portuguese:

| Primary category | Total | Development | Frozen test |
| --- | --- | --- | --- |
| Answerable factual or conceptual questions | 60 | 30 | 30 |
| Answerable exercises requiring derivation | 60 | 30 | 30 |
| Insufficient evidence | 40 | 20 | 20 |
| Conflicting evidence | 20 | 10 | 10 |
| Adversarial document/question instructions | 20 | 10 | 10 |
| **Total** | **200** | **100** | **100** |

Primary categories are disjoint; secondary tags identify subject, language, answer format, multi-source requirements, and failure mode. Split by source document or exercise family so near-duplicates cannot straddle development and test. Each partition has 50 English and 50 Portuguese cases. Tune prompts, thresholds, and retrieval on development only; record any test-set exposure and create a new test version before further tuning.

Store a case ID, category, language, selected collections, question, expected status, reference answer or rubric, required evidence IDs, acceptable derivations, source provenance, and redistribution terms. Generated questions are proposals until a human reviews them. The corpus used for retrieval excludes evaluation questions, expected answers, and grading notes. When importing an authentic past exam, exclude its answer key from an exercise-solving evaluation; explicitly label answer-key lookup as a different task.

Use original or suitably licensed documents and exercises. Do not ship private textbooks to make a public benchmark reproducible. Include a corpus manifest with document hashes and parser/index fingerprints.

## Metrics and initial gates

Use the frozen test partition for release reporting. Report raw numerators, denominators, per-language and per-subject breakdowns, and uncertainty; a small benchmark is not a universal quality claim.

| Metric | Definition | Initial release gate |
| --- | --- | --- |
| Evidence recall@6 | Mean fraction of annotated required evidence units represented in the final evidence set, over 60 answerable test cases | >= 90% |
| Correctness | Answers passing the case rubric, divided by all 60 answerable cases; refusals count as incorrect | >= 80% |
| Citation support | Material factual claims with citations that actually support the claim, divided by cited material factual claims | >= 95% |
| Citation coverage | Material factual claims carrying an appropriate citation, divided by all material factual claims | >= 90% |
| Appropriate abstention | `insufficient_evidence` on the 20 insufficient-evidence test cases | >= 90% |
| False abstention | `insufficient_evidence` on the 60 answerable test cases | <= 10% |
| Conflict detection | Correctly identifies the incompatible sources on the 10 conflict test cases | >= 90% |
| Citation integrity | Emitted source IDs and page/section locations resolve to supplied, active evidence | 100% |
| Collection isolation | Retrieval and citations stay within selected collections | Zero violations in the regression suite |
| Adversarial boundaries | Embedded instructions cannot invoke tools, change collection scope, fetch URLs, or become system instructions | All adversarial fixtures pass |

Derived results are graded for assumptions, arithmetic, units, and use of cited principles; they need not occur verbatim in the source. A citation to a formula does not prove a calculation correct. Empty answers, errors, and malformed results are failures rather than excluded samples. Report NDCG@10 and lexical/dense/fused ablations diagnostically without adding arbitrary release gates for every metric.

A human applies the citation and correctness rubrics. A second reviewer should independently score a stratified 20% sample before a stable release; disagreements and adjudication are recorded. If only one reviewer is available, label the report accordingly and keep the release experimental. A local LLM judge may help triage, but cannot certify its own outputs.

## Performance workload

Reference workload: 10,000 indexed chunks; explicit collection selection; evidence budget at most 2,400 generator tokens; 8,192-token total context; one active generation; answers at most 1,024 tokens. Use a versioned mix of short and long queries and a fixed model configuration. Record whether import is idle or active.

| Measurement | Proposed target for the selected default |
| --- | --- |
| Retrieval p95, including query embedding and any enabled reranking | <= 750 ms |
| Warm time from submission to first answer token, including retrieval | <= 5 seconds |
| Median decode rate after first token | >= 15 answer tokens/second |
| Cancellation acknowledged and provider work stopped | <= 1 second |
| Attributed peak application memory, including model processes | <= 10 GiB |
| Sustained study session | 30 minutes without crashes or sustained swap growth |
| UI interaction latency while work is running | p95 <= 100 ms for local controls |

For latency distributions, collect at least 100 warm requests after five warmups; measure cold load separately. Record failures and timeouts in the report rather than dropping them from latency statistics. Capture OS memory pressure and process/GPU accounting methodology without double-counting shared allocations. The 10 GiB budget is a design target, not a guarantee that the OS always has 6 GiB available.

If the first baseline misses a target, profile and record a scoped adjustment before release. Preserve the previous target and rationale in the decision history; do not quietly redefine success. Measure 1,000 and 100,000 chunks as exploratory scale points without promising support at those sizes.

## Reproducibility and regression layers

- PR CI: formatting, typing, unit tests, SQLite integration, fake-provider API/streaming contracts, parser fixtures, and UI behavior. No model download or GPU is required for basic contributions.
- Model smoke suite: opt-in/manual CI for each pinned runtime and model artifact; verifies offline load, templates, token budgets, streaming, cancellation, and failure reporting.
- Release evaluation: human-reviewed frozen benchmark, full performance report, 30-minute session, migration/restore test, and external-network-disabled workflow.
- Default-model or retriever changes: rerun the relevant ablations and full release evaluation; compare against the previous baseline.

Test pathological input separately: encrypted/corrupt/scanned PDFs, oversized files and questions, UTF-8 accents, numeric units, disk-full writes, duplicate imports, interrupted index rebuilds, deleted sources, mid-stream model failure, disconnected browsers, and unselected-collection distractors. Functional mocks never substitute for model-quality or hardware evidence.

Every result records project commit, corpus and dataset versions, model file hashes, runtime version, tokenizer and quantization, prompt version, sampling configuration, index generation, OS/chip/RAM, and timing method. Publish only redacted traces using redistributable fixtures.

## Definition of release readiness

The release checklist links to actual passing reports for the gates above, a clean-checkout setup walkthrough, licensing notices, and known limitations. Automated tests prove software behavior; human grading and hardware runs provide different evidence. A failed gate means an experimental build or a narrower scope, not an undocumented exception.
