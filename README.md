# Professor AI

**A local study assistant that answers from your learning materials, cites its sources, and acknowledges insufficient evidence.**

Professor AI aims to help students study multiple subjects and work through exam questions using a private, user-managed knowledge base. Documents, retrieval, embeddings, and answer generation run on the user's computer after dependencies and models have been downloaded.

> **Project status: foundation development.** The Python package, settings, diagnostics, health API, and [synthetic evaluation runner](docs/EVALUATION_RUNNER.md) are implemented. [Thirty bilingual development cases](evals/README.md) are prepared for human review. Learning-material ingestion, RAG, inference, and the web interface remain planned. There is no stable application release or measured model-performance result yet.

## Run the foundation

With [uv](https://docs.astral.sh/uv/getting-started/installation/) installed, run from the repository root:

```bash
uv sync --locked --group dev
uv run professor-ai doctor
uv run professor-ai serve
```

The health endpoint is `http://127.0.0.1:8765/health`. No model is needed for these commands. See the [development guide](docs/DEVELOPMENT.md) for configuration, troubleshooting, and the required checks.

## What we are building

- Collections for subjects such as mathematics, physics, biology, and computer science.
- Import of text PDFs, Markdown, and plain text in the first release.
- Hybrid search across explicitly selected collections.
- Answers with document, page or section, and supporting excerpts.
- Clear handling of missing evidence, conflicting sources, and failed imports.
- A responsive local web interface with streaming and cancellation.
- English project documentation and code; English and Brazilian Portuguese evaluation and user-facing language support.

Retrieval-augmented generation (RAG) supplies relevant material to a pretrained model. It does not train the model on each upload or guarantee expert-level accuracy. A useful answer must be evaluated for correctness as well as support from its sources. Solutions to new exercises may derive results from cited principles; those derivations must be distinguishable from facts stated by a source.

## Initial direction

The reference environment is the maintainer's reported Apple M4-family MacBook with 16 GB RAM. Exact chip, OS, and runtime details will be recorded with benchmarks. Desktop comes first; on-device iPhone support is a later milestone.

| Area | Proposed starting choice |
| --- | --- |
| Application and RAG | Python 3.12, FastAPI, Pydantic |
| Interface | TypeScript, React, Vite |
| Local generation | llama.cpp, GGUF, Metal on Apple Silicon |
| Persistence | SQLite, FTS5, sqlite-vec |
| Retrieval | BM25 + normalized dense vectors + reciprocal rank fusion |
| Embedding baseline | multilingual-e5-small |
| Generator shortlist | Qwen3.5-4B, Qwen3.5-9B, Phi-4-mini-instruct |
| Quality tooling | uv, Ruff, mypy, pytest; TypeScript checks and browser tests |

These are proposed project choices, not a tested compatibility matrix. See the [architecture](docs/ARCHITECTURE.md) and [model shortlist](docs/MODELS.md) for rationale, constraints, and primary sources.

## Project guide

1. [Roadmap: milestones, epics, and user stories](docs/ROADMAP.md)
2. [Architecture and algorithm decisions](docs/ARCHITECTURE.md)
3. [Model recommendations and selection protocol](docs/MODELS.md)
4. [Evaluation and release gates](docs/EVALUATION.md)
5. [Foundation implementation plan](docs/plans/2026-10-22-foundation.md)
6. [Development smoke corpus and review workflow](evals/README.md)
7. [Development evaluation runner](docs/EVALUATION_RUNNER.md)
8. [Contributing](CONTRIBUTING.md)
9. [Repository maintenance and security settings](docs/REPOSITORY.md)
10. [Development and local setup](docs/DEVELOPMENT.md)
11. [Pinned model catalog and explicit acquisition](docs/MODEL_ARTIFACTS.md)

The next vertical slice will import a small document collection, retrieve evidence, and produce a cited answer through the CLI. The interface follows that tested path. Current installation includes the foundation and synthetic evaluation tooling.

## Contributing

Contributions can improve document parsing, retrieval, evaluation questions, accessibility, documentation, and local runtime support. Start with a story in the [roadmap](docs/ROADMAP.md) or an [open issue](https://github.com/Paulohspaniago/professor-ai/issues), keep changes focused, and include evidence of behavior. The maintainer reviews scope and releases. See [CONTRIBUTING.md](CONTRIBUTING.md) and the [code of conduct](CODE_OF_CONDUCT.md). Questions belong in [Discussions](https://github.com/Paulohspaniago/professor-ai/discussions); vulnerabilities use [private reporting](SECURITY.md).

## License

Project code and original documentation are available under the [MIT License](LICENSE). Third-party model weights, dependencies, and learning materials retain their own licenses. Private documents and model binaries do not belong in this repository.
