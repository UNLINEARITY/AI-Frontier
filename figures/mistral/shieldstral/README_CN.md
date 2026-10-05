# Shieldstral

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf) · [官方来源](https://arxiv.org/abs/2607.25857)

## 架构 · Figure 1

原文第2页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf#page=2)

![架构](figure-01.png)

Figure 1: Shieldstral architecture. An instruction, a natural-language query, and content (text, image, or both)
are composed into a structured prompt, then processed by the model in a single forward pass. The softmax-
normalised logits of the “yes” and “no” tokens yield a continuous safety score that is thresholded for binary
classification.

## 安全评测 · Figure 5

原文第11页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf#page=11)

![安全评测](figure-02.png)

Figure 5: F1 scores (%) on safety classification benchmarks. PolyGuard and RTPLX are multilingual datasets.
Qwen3Guard results are averaged over strict (controversial=unsafe) and loose (controversial=safe) mappings.
ShieldGemma and Shieldstral use a threshold of 0.5. GPT-OSS-Safeguard-20B uses reasoning_effort=high.
Nemotron-3.5-Safety uses reasoning_effort=none for default categories.
