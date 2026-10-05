# Qwen3-Coder-Next Technical Report

Models: Qwen3-Coder-Next

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/qwen/technical-reports/qwen3-coder-next-technical-report--arxiv-v1.pdf#page=1) · [Official source](https://github.com/QwenLM/Qwen3-Coder)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

We present Qwen3-Coder-Next, an open-weight language model specialized for coding agents. Qwen3-Coder-Next is an 80-billion-parameter model that activates only 3 billion parameters during inference, enabling strong coding capability with efficient inference. In this work, we explore how far strong training recipes can push the capability lim- its of models with small parameter footprints. To achieve this, we perform agentic training through large-scale synthesis of verifiable coding tasks paired with executable environments, allowing learning directly from environment feedback via mid-training and reinforcement learning. Across agent-centric benchmarks including SWE-Bench and Terminal-Bench, Qwen3-Coder-Next achieves competitive performance relative to its active parameter count. We release both base and instruction-tuned open-weight versions to support research and real-world coding agent development.

## Core figures

[All figures and original captions](../../figures/qwen/qwen3-coder-next-technical-report/README.md) · [中文](../../figures/qwen/qwen3-coder-next-technical-report/README_CN.md)

### Results · Figure 1

Source page: 1 · [Original graphics PDF](../../figures/qwen/qwen3-coder-next-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/qwen/qwen3-coder-next-technical-report/figure-01.png)

![Results](../../figures/qwen/qwen3-coder-next-technical-report/figure-01.png)

Figure 1: Comparison of Qwen3-Coder-Next to other open-weight models on SWE-Bench Verified,
SWE-Bench Multilingual, SWE-Bench Pro, Terminal-Bench 2.0, and Aider.

### Architecture · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/qwen/qwen3-coder-next-technical-report/figure-02.pdf) · [High-resolution PNG](../../figures/qwen/qwen3-coder-next-technical-report/figure-02.png)

![Architecture](../../figures/qwen/qwen3-coder-next-technical-report/figure-02.png)

Figure 2: Our pipeline for synthesizing bugs to scale up the number of software engineering tasks.
