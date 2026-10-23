# Original Concept and Design Evolution

This document summarizes the original concept in English. The current project direction is defined by the [README](../README.md), [architecture](ARCHITECTURE.md), and [roadmap](ROADMAP.md).

## Original vision

Professor AI began as a private, fully local study assistant for computer science. The intended experience was a personal tutor on an iPhone, answering questions using learning materials supplied by the user. Answers would cite their sources and acknowledge when the material did not cover a question.

The proposed pipeline was document extraction, structure-aware chunking, local embeddings, vector retrieval, and generation from selected passages. The initial document formats were PDF, TXT, and DOCX. The first scope emphasized conceptual questions and excluded code generation.

## Principles retained

- User-provided material is the primary evidence for an answer.
- Retrieval quality and document quality deserve explicit evaluation.
- Citations should let the student inspect the supporting material.
- Insufficient evidence should produce an honest limitation.
- Privacy and local operation remain product requirements.

## Decisions updated on 2026-10-22

| Original direction | Current direction |
| --- | --- |
| iPhone 14 as the initial target | Desktop first; iPhone after a separate feasibility study |
| Computer science only | Multiple subject collections, initially evaluated on computing, mathematics, and physics |
| Conceptual questions only | Conceptual questions and text-based exercises with cited principles and explicit derivations |
| Small Qwen2.5 models chosen around phone constraints | Three desktop candidates selected through a reproducible benchmark |
| EmbeddingGemma as a fixed embedding choice | A lightweight multilingual baseline with measured alternatives |
| Portuguese project document | English code, project documentation, and contribution workflow; English/Portuguese evaluation |
| A personal prototype | A maintainer-owned MIT project prepared for community contributions |

## Claims corrected before publication

The original proposal contained estimated iPhone memory limits, throughput, thermal behavior, and percentages attributing quality to retrieval. These estimates were not measurements of this application and are not carried forward as guarantees.

RAG does not eliminate hallucinations, a citation does not prove support, and exact vector search does not guarantee retrieval of the correct evidence. A small model may or may not solve an exercise even when the relevant principles are available. The current evaluation plan measures these separately.

The original discussion also drew inspiration from a small-model training experiment. That observation does not establish that a smaller pretrained model is best for this application. Default model selection will use the project's own quality and resource measurements.

## Current next step

The [foundation plan](plans/2026-10-22-foundation.md) is implemented. Next, build a reviewed evaluation corpus and qualify a local runtime. Then deliver the CLI import → retrieve → answer workflow before expanding the interface and supported content formats.
