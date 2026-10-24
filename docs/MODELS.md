# Local Model Recommendations

Research date: 2026-10-22. Reference hardware: the maintainer's reported M4-family MacBook with 16 GB RAM. This is a shortlist for project evaluation, not a global leaderboard or a claim of measured performance on that computer.

## Top three generator candidates

| Evaluation order | Exact upstream checkpoint | Proposed role | Starting representation | Upstream license |
| --- | --- | --- | --- | --- |
| 1 | [Qwen/Qwen3.5-4B](https://huggingface.co/Qwen/Qwen3.5-4B) | First candidate for the balanced default | GGUF Q4_K_M, text input | Apache-2.0 |
| 2 | [Qwen/Qwen3.5-9B](https://huggingface.co/Qwen/Qwen3.5-9B) | Quality comparison if memory and latency permit | GGUF Q4_K_M, text input | Apache-2.0 |
| 3 | [microsoft/Phi-4-mini-instruct](https://huggingface.co/microsoft/Phi-4-mini-instruct) | Compact alternative from a different model family | GGUF Q4_K_M, text input | MIT |

**Qwen3.5-4B:** Start here to test whether a compact current Qwen checkpoint can meet our grounded QA and responsiveness targets. The candidate choice is an engineering hypothesis. Its upstream model card includes multimodal capabilities, but the MVP qualifies text only. Use the runtime's validated non-thinking chat-template configuration and bound output; do not assume a `/nothink` string configures this family. [Upstream card](https://huggingface.co/Qwen/Qwen3.5-4B).

**Qwen3.5-9B:** Compare with the smaller model to measure the actual quality/memory tradeoff. Promote it only if it passes the same constraints and offers a material gain on held-out questions. Upstream long-context and reasoning benchmarks do not establish performance under our shorter context and output limits. [Upstream card](https://huggingface.co/Qwen/Qwen3.5-9B).

**Phi-4-mini-instruct:** Its upstream card describes a 3.8B model and includes Portuguese among supported languages. It provides a useful independent comparison for instruction following and exercise explanations. Test grounding and abstention explicitly; language support and upstream math scores are not evidence of reliable citations. Use the model's own chat template. [Upstream card](https://huggingface.co/microsoft/Phi-4-mini-instruct).

The shortlist favors practical experiments and available upstream documentation, not novelty alone. Revisit it when evaluation results or deployment requirements change. No candidate is a released default yet.

## Memory and runtime policy

At exactly four bits per parameter, the arithmetic lower bound for weights is approximately 2.0 GB for 4B, 4.5 GB for 9B, and 1.9 GB for 3.8B parameters, using decimal units. These are **not model download sizes or runtime RAM estimates**: mixed quantization, metadata, buffers, caches, and other model components add overhead.

For every candidate, start with an 8,192-token total context, one generation slot, and a 1,024-token answer limit. Reserve memory for the OS, browser, API, embedding model, and import worker. Keep the number of loaded models bounded; download and test candidates sequentially. Test both cold start and warm operation, including a sustained session.

Use a pinned llama.cpp build and verify Metal operation, tokenization, cancellation, and chat-template behavior for each exact artifact. A model name or an OpenAI-compatible endpoint is insufficient to prove compatibility. [llama.cpp](https://github.com/ggml-org/llama.cpp).

Do not copy upstream large-context or cloud-server examples into the desktop configuration. Keep sampling settings explicit per model and begin from upstream non-thinking guidance where applicable; the evaluation report records all deviations.

## Embeddings and reranking

The baseline is [intfloat/multilingual-e5-small](https://huggingface.co/intfloat/multilingual-e5-small). Its MIT-licensed model card specifies 384-dimensional embeddings, retrieval prefixes `query: ` and `passage: ` even for non-English text, normalized vectors in its example, and a 512-token input ceiling. These requirements belong in adapter tests. [Model card source](https://huggingface.co/intfloat/multilingual-e5-small/raw/main/README.md).

Compare [Qwen/Qwen3-Embedding-0.6B](https://huggingface.co/Qwen/Qwen3-Embedding-0.6B), licensed Apache-2.0, only after establishing the baseline. A larger embedding model must earn its memory and latency cost with better English/Portuguese retrieval. It creates a different index generation; its vectors cannot be mixed with E5 vectors.

Reranking is initially disabled. Evaluate a multilingual cross-encoder on the same development split if retrieval errors justify it. Reject an English-only choice based solely on English benchmarks. EmbeddingGemma remains a possible later experiment, not an additional required runtime in the MVP.

## Artifact manifest required before installation

The [packaged catalog and acquisition CLI](MODEL_ARTIFACTS.md) now pin the three
GGUF candidates and the direct E5 baseline, with announced sizes/digests and
independently hashed small configuration/notice files. Explicit `models fetch`
performs local size/hash verification; offline inspection never downloads weights.
All entries remain publisher-metadata-only and runtime-unqualified. Converter
ancestry and E5 standalone notice evidence retain the documented limitations;
this does not select or qualify a default model.

For each generator or embedding artifact, record:

- Upstream repository, immutable revision, and license reference.
- Conversion repository and immutable revision, or a reproducible conversion recipe.
- File names, byte sizes, SHA-256 digests, format, and quantization.
- Runtime version or commit, tokenizer revision, and chat-template settings.
- Context/output limits, sampling settings, and supported capabilities.
- For embeddings: dimension, pooling, normalization, and input prefixes.

Verify a quantized artifact's provenance and terms independently of its display name. These manifest values must be measured or read from the chosen artifacts; this planning document deliberately does not invent checksums or a download size. Automated installation cannot ship until the manifest is populated and verified. Never enable arbitrary remote model code as a convenience default.

## Selection experiment

1. Validate runtime compatibility with a short smoke suite and record failures.
2. Compare generators on identical retrieved evidence to isolate generation quality.
3. Compare the full pipeline with each candidate, holding corpus and retrieval settings fixed.
4. Measure the [evaluation gates](EVALUATION.md), warm and cold latency, attributed memory, and cancellation.
5. Choose the fastest candidate passing the quality and memory gates. A larger candidate may become an opt-in quality profile when it improves held-out answer accuracy by at least five percentage points without failing citation support or the resource gates.
6. Publish results with exact artifacts, settings, sample counts, uncertainty, and known failures. If no candidate passes, improve the pipeline or explicitly revise scope; do not declare a winner anyway.

The project's MIT license covers its own code and documentation. It does not relicense Qwen weights, dependency code, or user-provided learning materials. Preserve upstream notices with redistributed artifacts.
