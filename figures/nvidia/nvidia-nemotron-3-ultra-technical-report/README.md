# NVIDIA Nemotron 3 Ultra Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf) · [Official source](https://research.nvidia.com/labs/nemotron/Nemotron-3/)

## Results · Figure 1

Source page: 2 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf#page=2)

![Results](figure-01.png)

Figure 1 | Accuracy and throughput comparisons for Nemotron 3 Ultra. Our model achieves on-par
accuracy with other open LLMs while achieving significantly higher inference throughput on the
8K input / 64K output token setting. All throughput numbers are reported at max-throughput
using NVFP4 precision on GB200. For Nemotron 3 Ultra, throughput numbers are obtained from
TRT-LLM, while all other model numbers use vLLM. We run with and without speculative decoding,
where available, and choose the best numbers for each model.

## Architecture · Figure 9

Source page: 15 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/nvidia/technical-reports/nvidia-nemotron-3-ultra-technical-report.pdf#page=15)

![Architecture](figure-02.png)

Figure 9 | Overview of the post-training pipeline for Nemotron 3 Ultra.
