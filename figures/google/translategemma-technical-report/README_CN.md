# TranslateGemma Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/google/technical-reports/translategemma-technical-report--arxiv-v3.pdf) · [官方来源](https://arxiv.org/abs/2601.09012)

## 架构 · Figure 2

原文第4页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/google/technical-reports/translategemma-technical-report--arxiv-v3.pdf#page=4)

![架构](figure-01.png)

Figure 2 | Illustration of how sequence-level and token-level rewards are additively combined during
advantage computation in RL. Note that advantage is computed from sequence-level rewards as
‘reward-to-go’, meaning that rewards are broadcast uniformly to every token.
