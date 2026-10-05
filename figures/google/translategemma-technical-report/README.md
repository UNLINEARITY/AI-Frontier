# TranslateGemma Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/google/technical-reports/translategemma-technical-report--arxiv-v3.pdf) · [Official source](https://arxiv.org/abs/2601.09012)

## Architecture · Figure 2

Source page: 4 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/google/technical-reports/translategemma-technical-report--arxiv-v3.pdf#page=4)

![Architecture](figure-01.png)

Figure 2 | Illustration of how sequence-level and token-level rewards are additively combined during
advantage computation in RL. Note that advantage is computed from sequence-level rewards as
‘reward-to-go’, meaning that rewards are broadcast uniformly to every token.
