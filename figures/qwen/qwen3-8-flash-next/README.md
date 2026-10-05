# On the Design of Qwen3.8-Next Architecture: Evaluation, Efficiency, and Training Stability

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf) · [Official source](https://github.com/QwenLM/Qwen3.8-Flash-Next)

## Architecture · Figure 1

Source page: 2 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf#page=2)

![Architecture](figure-01.png)

Figure 1: Qwen3.8-Flash-Next architecture. Token mixing alternates three GDN layers with one QSA
layer per block of four. Every sublayer reads and writes through GR, which widens the residual stream
and gates the read elementwise. An n-gram embedding layer at Layer 2 scales capacity off the accelerator
via host-memory prefetching. The MTP module reuses QSA indices across speculative decoding steps.

## Results · Figure 5

Source page: 9 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/qwen/technical-reports/qwen3-8-flash-next.pdf#page=9)

![Results](figure-02.png)

Figure 5: Architecture ablations of QSA on RULER. (a) QSA performance with different micro-block sizes;
“Keep x” indicates the number of IndexShare indexer layers retained for computation. (b) Performance
with different numbers of indexer query heads after dense distillation and sparse training.
