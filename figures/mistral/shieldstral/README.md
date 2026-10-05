# Shieldstral

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf) · [Official source](https://arxiv.org/abs/2607.25857)

## Architecture · Figure 1

Source page: 2 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf#page=2)

![Architecture](figure-01.png)

Figure 1: Shieldstral architecture. An instruction, a natural-language query, and content (text, image, or both)
are composed into a structured prompt, then processed by the model in a single forward pass. The softmax-
normalised logits of the “yes” and “no” tokens yield a continuous safety score that is thresholded for binary
classification.

## Safety evaluation · Figure 5

Source page: 11 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/mistral/technical-reports/shieldstral--arxiv-v2.pdf#page=11)

![Safety evaluation](figure-02.png)

Figure 5: F1 scores (%) on safety classification benchmarks. PolyGuard and RTPLX are multilingual datasets.
Qwen3Guard results are averaged over strict (controversial=unsafe) and loose (controversial=safe) mappings.
ShieldGemma and Shieldstral use a threshold of 0.5. GPT-OSS-Safeguard-20B uses reasoning_effort=high.
Nemotron-3.5-Safety uses reasoning_effort=none for default categories.
