# DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/deepseek/technical-reports/deepseek-v4-1-flash-technical-report--arxiv-v1.pdf) · [Official source](https://arxiv.org/abs/2609.19969)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/deepseek/technical-reports/deepseek-v4-1-flash-technical-report--arxiv-v1.pdf#page=1)

![Results](figure-01.png)

Figure 1 | (a) Performance of DeepSeek-V4.1-Flash and its counterparts on agentic benchmarks.
(b) Global KV cache size per token (in bytes) across generations of DeepSeek models, highlight-
ing DeepSeek’s sustained efforts to reduce context memory requirements. DeepSeek-V4.1-Flash
achieves approximately 4-fold and 437-fold reductions in per-token global KV cache size relative
to DeepSeek-V4-Flash and DeepSeek-V1, respectively.

## Architecture · Figure 3

Source page: 7 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/deepseek/technical-reports/deepseek-v4-1-flash-technical-report--arxiv-v1.pdf#page=7)

![Architecture](figure-02.png)

Figure 3 | Overall architecture of DeepSeek-V4.1-Flash. The 40-layer network is divided into
a causal encoder and a decoder, each with 20 layers. All feed-forward layers use standard
DeepSeekMoE. The first two encoder layers use sliding window attention (SWA); the rest use
Compressed Sparse Attention 2 (CSA2), with CSA2(ratio, mode) specifying the compression
ratio and mode. The model also uses Single-Pass mHC, Engram, DSpark, and a Hierarchical
Sparse Indexer.
