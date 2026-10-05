# On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf) · [官方来源](https://github.com/QwenLM/Qwen3.8-Flash-Next)

## 架构 · Figure 1

原文第2页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf#page=2)

![架构](figure-01.png)

Figure 1: Qwen3.8-Flash-Next architecture. Token mixing alternates three GDN layers with one QSA
layer per block of four. Every sublayer reads and writes through GR, which widens the residual stream
and gates the read elementwise. An n-gram embedding layer at Layer 2 scales capacity off the accelerator
via host-memory prefetching. The MTP module reuses QSA indices across speculative decoding steps.

## 主要结果 · Figure 5

原文第9页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf#page=9)

![主要结果](figure-02.png)

Figure 5: Architecture ablations of QSA on RULER. (a) QSA performance with different micro-block sizes;
“Keep x” indicates the number of IndexShare indexer layers retained for computation. (b) Performance
with different numbers of indexer query heads after dense distillation and sparse training.
