# StepAudio 3 Realtime Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf) · [官方来源](https://arxiv.org/abs/2609.14005)

## 主要结果 · Figure 1

原文第1页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf#page=1)

![主要结果](figure-01.png)

Figure 1: Benchmark results for StepAudio 3 ASR Max and StepAudio 3 Realtime (blue), compared with baselines (gray). Lower
is better for ASR error rates, and higher is better elsewhere. Dialogue averages eight dimensions, full duplex reports Overall, and
τ-Voice averages three domains. See Tables 1 and 10.

## 架构 · Figure 3

原文第4页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf#page=4)

![架构](figure-02.png)

Figure 3: System architecture of StepAudio 3 Realtime. The LLM decoder receives audio representations through the audio
encoder and adapter, together with a separate text input. User and model audio form the two full-duplex streams, with generator
output returning to the model audio stream. Waveforms are schematic.
