# StepAudio 3 Gen Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf) · [官方来源](https://arxiv.org/abs/2609.12945)

## 架构 · Figure 1

原文第4页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf#page=4)

![架构](figure-01.png)

Figure 1: Overview of the StepAudio 3 Gen architecture. At each audio frame, the LLM predicts c0, and the RVQ Code
Predictor conditions on the LLM hidden state and c0 to predict c1, . . . , c15. All sixteen codes form the full RVQ frame
used for waveform decoding. ⊕denotes element-wise addition: at audio positions, the RVQ Adaptor output is added to
the corresponding token embedding (§2.2).

## 主要结果 · Figure 2

原文第12页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf#page=12)

![主要结果](figure-02.png)

Figure 2: Human evaluation on the Chinese human-likeness test set.
