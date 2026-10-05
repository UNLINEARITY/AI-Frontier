# MAI-Thinking-1: Building a Hill-Climbing Machine

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf) · [官方来源](https://microsoft.ai/models/mai-thinking-1/)

## 架构 · Figure 2

原文第5页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf#page=5)

![架构](figure-01.png)

Figure 2. Overview of the MAI-Base-1 architecture. Left: the overall layout of the Transformer body, where we
interleave high-sparsity MoE layers with small dense FFNs, and global attention with local attention. Right: The
MoE layer, in which 8 of 512 experts are activated per token in a compressed latent space.

## 主要结果 · Figure 15

原文第35页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/microsoft/technical-reports/mai-thinking-1-technical-report.pdf#page=35)

![主要结果](figure-02.png)

Figure 15. Performance on AIME 2025 (left) and a hard subset of LiveCodeBench v6 (right) during our STEM
climb. Self-distillation is indicated through ⋆markers; different pre- and mid-trained model versions are shown
in different colors. Maximum output length throughout training is indicated at the bottom. Self-distillation is an
effective way of resetting numerics after a collapse (visible through sudden drops in performance) and changing
the base policy during our run. As we made infrastructure and algorithmic improvements throughout our climb,
self-distillation because of run collapses became less frequent.
