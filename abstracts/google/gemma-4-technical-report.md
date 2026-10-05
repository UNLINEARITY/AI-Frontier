# Gemma 4 Technical Report

Models: Gemma 4

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/google/technical-reports/gemma-4-technical-report--arxiv-v2.pdf#page=1) · [Official source](https://arxiv.org/abs/2607.02770)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Unlabelled opening summary

We introduce Gemma 4, a new generation of open-weight, natively multimodal language models in the Gemma model family. Designed to advance compute efficiency and reasoning, the Gemma 4 model suite features dense and Mixture-of-Experts architectures, ranging from 2.3B to 31B parameters. Alongside improved vision and audio encoders for all model sizes, we propose a unified, encoder-free architecture for our 12B model, which ingests raw audio and image patches. Furthermore, we integrate a thinking mode, enabling Gemma models to generate reasoning traces prior to responding. We improve inference speed, memory, and compute efficiency, as well as long-context abilities through critical design choices. Gemma 4 establishes a leap in performance across STEM, multimodal, and long-context benchmarks, and rivals larger, frontier open models in human-rated tasks.

## Core figures

[All figures and original captions](../../figures/google/gemma-4-technical-report/README.md) · [中文](../../figures/google/gemma-4-technical-report/README_CN.md)

### Architecture · Figure 1

Source page: 3 · [Original graphics PDF](../../figures/google/gemma-4-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/google/gemma-4-technical-report/figure-01.png)

![Architecture](../../figures/google/gemma-4-technical-report/figure-01.png)

Figure 1 | The autoregressive MTP drafter (blue
blocks on the right) is fed activations and KV
cache from the main model (gray blocks).
