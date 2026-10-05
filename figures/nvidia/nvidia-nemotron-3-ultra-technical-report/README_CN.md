# NVIDIA Nemotron 3 Ultra Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf) · [官方来源](https://research.nvidia.com/labs/nemotron/Nemotron-3/)

## 主要结果 · Figure 1

原文第2页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf#page=2)

![主要结果](figure-01.png)

Figure 1 | Accuracy and throughput comparisons for Nemotron 3 Ultra. Our model achieves on-par
accuracy with other open LLMs while achieving significantly higher inference throughput on the
8K input / 64K output token setting. All throughput numbers are reported at max-throughput
using NVFP4 precision on GB200. For Nemotron 3 Ultra, throughput numbers are obtained from
TRT-LLM, while all other model numbers use vLLM. We run with and without speculative decoding,
where available, and choose the best numbers for each model.

## 架构 · Figure 9

原文第15页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf#page=15)

![架构](figure-02.png)

Figure 9 | Overview of the post-training pipeline for Nemotron 3 Ultra.
