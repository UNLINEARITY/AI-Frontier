# NVIDIA Nemotron 3 Super Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-super-technical-report.pdf) · [官方来源](https://research.nvidia.com/labs/nemotron/Nemotron-3/)

## 主要结果 · Figure 1

原文第2页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-super-technical-report.pdf#page=2)

![主要结果](figure-01.png)

Figure 1 | Accuracy and throughput comparisons of Nemotron 3 Super with GPT-OSS-120B and
Qwen3.5-122B. Nemotron 3 Super achieves comparable accuracies across popular benchmarks but
provides the highest inference throughput; on 8k input sequence lengths and 64k output sequence
lengths, Nemotron 3 Super provides up to 2.2× and 7.5× higher throughput than GPT-OSS-120B
and Qwen3.5-122B, respectively. We measured throughput on B200 GPUs with vLLM and TRT-LLM
and use the best out of the two frameworks for each model. For GPT-OSS-120B we use MXFP4
weights, MXFP8 activations, and FP8 KV-Cache; for Qwen3.5-122B we use BF16. We used the
OpenHands harness to evaluate SWE-Bench.

## 架构 · Figure 12

原文第18页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-super-technical-report.pdf#page=18)

![架构](figure-02.png)

Figure 12 | Overview of the post-training pipeline for Nemotron 3 Super.
