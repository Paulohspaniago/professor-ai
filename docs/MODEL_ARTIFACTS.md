# Pinned Model Artifacts

The packaged catalog pins publisher metadata for the three generator candidates
and the E5 embedding baseline. Catalog inspection is offline. Acquiring weights
requires an explicit command; no import, health check, diagnostic, or test
automatically transfers or loads a model.

## Inspect before acquiring

```bash
uv run professor-ai models list --json
uv run professor-ai models inspect qwen3.5-4b-q4_k_m --json
uv run professor-ai models verify qwen3.5-4b-q4_k_m --json
```

`list` and `inspect` only read the packaged JSON catalog. `verify` reads local
files and computes SHA-256; it creates no directory and makes no network request.
All commands accept `--catalog PATH` for an explicitly supplied local catalog.
Such catalogs must satisfy the same immutable-reference and path constraints.
Destination paths must be distinct even on case-insensitive filesystems, including
the spelling of shared parent directories.

| ID | Weight bytes | Complete snapshot bytes | Declared license |
| --- | --- | --- | --- |
| `qwen3.5-4b-q4_k_m` | 2,707,513,696 | 2,707,632,628 | Apache-2.0 |
| `qwen3.5-9b-q4_k_m` | 5,627,044,256 | 5,627,163,135 | Apache-2.0 |
| `phi-4-mini-q4_k_m` | 2,491,874,400 | 2,491,912,626 | MIT |
| `multilingual-e5-small` | 470,641,600 | 493,292,828 | MIT (model card) |

Snapshot sizes include configuration, tokenizer assets where needed, and notice
material. These are exact catalog byte counts, **not RAM estimates**. Required
free disk includes the outstanding bytes and a 64 MiB reserve. Acquire candidates
sequentially, following [MODELS.md](MODELS.md); none is a selected application default.

## Explicit acquisition and verification levels

```bash
uv run professor-ai models fetch qwen3.5-4b-q4_k_m --json
uv run professor-ai models verify qwen3.5-4b-q4_k_m --json
```

The default store is `models/` under the application's per-user data directory.
`--directory PATH` overrides the store for fetch/verify; quote paths with spaces.
Each installed snapshot is stored at `STORE/ID/ENTRY_FINGERPRINT/`. Changes to
catalog provenance, configuration, references, or files produce a new fingerprint,
preserving old snapshots. No runtime is installed or launched by these commands.

There are three distinct states of evidence:

1. **Publisher metadata:** immutable commits, announced sizes/digests and declared
   settings are recorded. This does not prove the entire weight file was locally
   downloaded or inspected. The bundled catalog remains at this level.
2. **Local integrity:** `fetch`/`verify` report `verified` only after all local files
   match sizes and SHA-256 and the receipt matches the entry fingerprint. A cached
   receipt alone is insufficient. Interrupted partials never count as installed.
3. **Runtime qualification:** tokenization, embedded GGUF templates, non-thinking
   operation, Metal, memory, latency, cancellation, and answer quality need later
   real-model tests. `runtime_qualified` stays false, including after a successful
   integrity check. Health therefore continues to report `not_configured`.

Exit 0 means successful catalog inspection or verified local integrity. Exit 1
means missing/invalid local files, a transfer failure, or insufficient disk.
Exit 2 means invalid catalog, model ID, or application configuration. `--json`
keeps results/errors machine-readable; acquisition messages go to stderr.

## Resume and recovery

Downloads stream over verified HTTPS into `.downloads/ID-FINGERPRINT/`, with
partials under `.partials/`. Re-run the same `fetch` command after interruption.
Valid range responses append; a server returning the full file restarts safely.
Bad ranges, unexpected encoding/length, and digest mismatches are rejected.
HTTPS redirects are bounded and checked before following; credentials are not
sent by this feature. No arbitrary remote Python code is fetched or executed.

All files remain unpublished until verified; the complete directory is then
renamed into the immutable destination. Re-fetching a verified installation uses
no network. An invalid existing installation is preserved and rejected; inspect
it or choose a fresh store rather than expecting automatic replacement.

A cooperative per-snapshot `.lock` prevents simultaneous writers. Ordinary errors
and Ctrl+C release the owned lock. A killed process/power interruption can leave
a stale lock: confirm its recorded PID is no longer acquiring the model before
removing that exact lock, then retry. Oversized or complete-but-corrupt partials
need inspection/removal before retrying; they are never silently installed.
The store rejects symlink components below its resolved root and hardlinked
partials. Before publication and during verification, it rejects entries outside
the catalog-defined tree and its receipt. Malformed or oversized receipts fail
with a structured error while preserving staged files for inspection. This is a local
cooperative cache, not protection against a hostile process mutating the filesystem.

## Sources, terms, and pending provenance

Generator distributions are pinned snapshots of LM Studio's community GGUFs:
[Qwen 4B](https://huggingface.co/lmstudio-community/Qwen3.5-4B-GGUF/tree/f9f88ac3e234be915e23811a6d28ea287bdb927e),
[Qwen 9B](https://huggingface.co/lmstudio-community/Qwen3.5-9B-GGUF/tree/1379f25c6b505a3fc737bd7818cb09389cf807c1),
and [Phi mini](https://huggingface.co/lmstudio-community/Phi-4-mini-instruct-GGUF/tree/009f2b81869a0afd6b9aae23d29fa7b7ee2dcac9).
Their model cards identify upstream base repositories and converter releases
b8185 (Qwen) and b4792 (Phi), but do not attest the exact upstream source commit.
The catalog's upstream revisions are independently observed references, **not a
claim of reproducible conversion ancestry**. Source-commit attestation remains open.

Generator acquisitions include pinned upstream LICENSE files and both source and
distribution model cards. E5 is a
[direct upstream safetensors snapshot](https://huggingface.co/intfloat/multilingual-e5-small/tree/614241f622f53c4eeff9890bdc4f31cfecc418b3).
Its model card declares MIT, but the repository has no standalone LICENSE file;
the card is retained and standalone notice/redistribution qualification remains
pending. The project does not bundle or relicense any model weights. Preserve
upstream terms with artifacts rather than applying the project's MIT license.

Weight digests/lengths came from the pinned Hugging Face API's LFS metadata. Small
configuration/notice files were independently fetched and hashed during catalog
preparation on 2026-10-23. API metadata is not a signature, provenance attestation,
or a local full-file hash measurement. No full candidate weight was transferred
as part of this implementation or its CI.

## Proposed runtime settings

The generator reference is
[llama.cpp v0.7.0 at commit 620d2225cc436ab0b001e3200e590e3b286ef9ab](https://github.com/ggml-org/llama.cpp/tree/620d2225cc436ab0b001e3200e590e3b286ef9ab).
This is a proposed qualification target, not a tested installed runtime. Use GGUF
embedded tokenizer/Jinja metadata; compare it with the pinned upstream template
reference before accepting it. Qwen profiles propose `enable_thinking: false`,
temperature 0.7, top-p 0.8, top-k 20, min-p 0, presence penalty 1.5, repetition
penalty 1, following upstream general non-thinking guidance. Phi starts from its
temperature-0 example. Both use project limits of 8,192 context tokens, 1,024 answer
tokens and one generation slot. These settings have not been validated locally.

E5 records a proposed Sentence Transformers 6.2.0 reference, a 512-token input
ceiling, 384 dimensions, attention-mask-aware mean pooling and normalized vectors.
Use `query: ` / `passage: ` prefixes even for Portuguese. Its tokenizer/config and
safetensors are pinned. The future embedding adapter must lock its complete
runtime dependencies, use local files only, and disable remote custom code.

S03.01 stays open for local-weight/runtime qualification, exact converter ancestry,
and unresolved notice evidence. These commands establish acquisition/integrity
mechanics; they do not complete S03.02 or select the best model.
