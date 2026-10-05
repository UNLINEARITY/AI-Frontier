# MAI-Thinking-1: Building a Hill-Climbing Machine

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf) · [Official source](https://microsoft.ai/models/mai-thinking-1/)

## Architecture · Figure 2

Source page: 5 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf#page=5)

![Architecture](figure-01.png)

Figure 2. Overview of the MAI-Base-1 architecture. Left: the overall layout of the Transformer body, where we
interleave high-sparsity MoE layers with small dense FFNs, and global attention with local attention. Right: The
MoE layer, in which 8 of 512 experts are activated per token in a compressed latent space.

## Results · Figure 15

Source page: 35 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf#page=35)

![Results](figure-02.png)

Figure 15. Performance on AIME 2025 (left) and a hard subset of LiveCodeBench v6 (right) during our STEM
climb. Self-distillation is indicated through ⋆markers; different pre- and mid-trained model versions are shown
in different colors. Maximum output length throughout training is indicated at the bottom. Self-distillation is an
effective way of resetting numerics after a collapse (visible through sudden drops in performance) and changing
the base policy during our run. As we made infrastructure and algorithmic improvements throughout our climb,
self-distillation because of run collapses became less frequent.
