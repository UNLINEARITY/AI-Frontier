# North Small Translate: Advanced Cost-Effective Translation (Cohere CAT+)

Models: North Small Translate 1.0

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/cohere/technical-reports/north-small-translate--arxiv-v1.pdf#page=1) · [Official source](https://arxiv.org/abs/2609.13916)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

We present North Small Translate, an open- weight, LLM-based machine translation (MT) model with instruction-following capabilities built on the same foundation as Cohere’s Com- mand A+, a mixture-of-experts architecture with 25 billion active parameters out of 218 billion total parameters. North Small Translate is trained using difficulty sampling to obtain challenging documents and a five-step train- ing protocol combining supervised fine-tuning, direct preference optimization, and online rein- forcement learning. We prioritized throughput through a non-reasoning base model and sup- plemented with optional agentic capabilities to unlock translation quality gains. North Small Translate is trained to perform MT-related tasks, including post-editing and quality esti- mation, as well as related tasks such as general instruction following. The model achieves top MT performance across 50 languages in the class of models under 1T parameters, with no need to run expensive reasoning at inference time.
