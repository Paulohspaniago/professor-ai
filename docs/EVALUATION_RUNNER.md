# Development Evaluation Runner

The runner executes versioned fixtures through retrieval and generation stages,
writing `report.json` and `report.md`. It supports **synthetic providers only**;
no model, database, embedding, or actual retrieval system is required.

## Run the baseline

Install the [development environment](DEVELOPMENT.md), then from the repository root:

```bash
uv run professor-ai evaluate --dataset evals --provider abstain --allow-unreviewed --json
```

The committed cases await human review. Without `--allow-unreviewed`, execution
rejects them before writing artifacts. This explicit development override never
approves a case or completes the human-review prerequisite.

The abstention baseline retrieves nothing and always returns insufficient
evidence, in the question's language. On the current corpus, it agrees with six
expected status labels and disagrees with 24, so **exit 1 is expected**. This
verifies harness behavior; it is not a model accuracy result.

The default output is a new timestamp/UUID directory under ignored
`artifacts/evaluations/`. Use `--output PATH` for a specific **new** directory.
Existing runs and symbolic-link outputs are preserved. Output cannot be inside
the dataset, including through an aliased parent. Quote paths containing spaces.
Reports contain questions, expected answers, rubrics, and outputs: never ingest
them as learning sources. On a writing failure, cleanup removes only files created
by that write; the command reports an error rather than publishing success.

`--json` prints a summary with status, counts, and absolute artifact paths.
Warnings go to stderr; full results are in `report.json`.

| Exit | Meaning |
| --- | --- |
| 0 | Every case completed without stage errors and expected statuses agree |
| 1 | Reports were written, with case errors or status disagreements |
| 2 | Invalid configuration/dataset, missing review, or report-writing failure |

Exit 0 does not certify correctness or release readiness. Ctrl+C interrupts rather
than becoming a provider error; an interrupted run has no completed report.

## Replay recorded outputs

A UTF-8 replay file uses schema version 1. Its `dataset_fingerprint` must match
`uv run python scripts/check_evals.py --json`. The shape is:

```json
{
  "schema_version": 1,
  "dataset_fingerprint": "<exact fixture fingerprint>",
  "results": {
    "<case ID>": {
      "evidence_ids": ["<source ID>"],
      "answer": {
        "status": "answered",
        "text": "An externally recorded answer.",
        "citations": ["<source ID>"]
      }
    }
  }
}
```

This shape example is not a runnable/graded answer file. Answer statuses are
`answered`, `insufficient_evidence`, or `conflicting_evidence`. Text must be
nonempty. Evidence/citation IDs must be distinct; retrieval must stay in the
selected collection, subject, and language. Citations must resolve to evidence
actually supplied to generation.

```bash
uv run professor-ai evaluate --dataset evals --provider replay --responses path/to/outputs.json --allow-unreviewed --output artifacts/evaluations/replay-01 --json
```

Replay reproduces recorded IDs/text; it does not search or generate. Unknown case
IDs or stale dataset bindings reject configuration. Missing cases become retrieval
errors; malformed answer objects become generation errors. Both stay in totals,
and later cases still run. An entry without `evidence_ids` or `answer` is malformed
configuration. The file is read once and its byte hash identifies loaded outputs;
execution also rejects a dataset changed after provider construction.

## Interpret reports

Overall, per-language, and per-subject summaries show raw numerators/denominators.
Each case preserves the question, reference answer/rubric, expected status,
returned evidence IDs, answer/citations, stage error, and timings. Provider text
stays literal in Markdown, including embedded Markdown and code fences.

- **Status agreement:** expected and returned statuses match, divided by all cases.
  Empty/malformed outputs and stage errors contribute zero.
- **Evidence recall:** mean fraction of required IDs returned, over cases with
  required evidence. Retrieval errors contribute zero. Generation errors retain
  any valid retrieval evidence, measuring retrieval separately. With no eligible
  cases the value is null, not a perfect score. This is not release recall@6.
- **Correctness, citation support, citation coverage:** explicitly ungraded/null.
  A human must apply the rubrics under [EVALUATION.md](EVALUATION.md).
- **Timings:** monotonic milliseconds around retrieval/validation,
  generation/validation, and the full case, including errors. Generation time is
  null when not attempted. These harness times are not LLM/hardware qualification.

Citation validation is structural; factual support is not certified. Every report
has `purpose: development_harness` and `benchmark_qualified: false`, even with a
reviewed dataset or a perfect replay.

## Reproducibility and boundaries

Metadata records dataset/provider/configuration hashes, project revision, dirty
state when discoverable, package/Python/platform versions, run ID, and start time.
Dataset hashes cover annotations and manifest source hashes; source bytes are
checked again before provider execution. Configuration hashes exclude run IDs and
timings so identical configurations remain comparable.

Git discovery uses the installed source checkout. Outside Git, revision is
`unknown` and dirty state is null. The dirty flag does not identify local edits;
use a clean commit for reproducible reports. Synthetic providers have no model
artifacts, tokenizer, prompt version, or index generation: those metadata fields
are empty/null. Future real adapters need pinned runtime/model identity.

`EvaluationProvider` accepts only an immutable request (ID, question, language,
selected collections) and immutable source records. Retrieval receives scoped
text; generation receives validated selected evidence. No reference answers,
rubrics, expected statuses, or required-evidence annotations enter provider inputs.
This in-process API is not a sandbox for untrusted Python plugins.

Reports use schema version 1 with no legacy migration. Incompatible future changes
must increment the version and explicitly convert old reports. Model integration,
retrieval, and frozen release evaluation remain separate roadmap work.
