# Phi-4-reasoning-vision-15B Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/microsoft/technical-reports/phi-4-reasoning-vision--arxiv-v1.pdf) · [Official source](https://arxiv.org/abs/2603.03975)

## Results · Figure 2

Source page: 3 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/microsoft/technical-reports/phi-4-reasoning-vision--arxiv-v1.pdf#page=3)

![Results](figure-01.png)

Figure 2: Phi-4-reasoning-vision-15B presents a compelling option compared to existing models, pushing the Pareto
frontier of the trade-off between accuracy and compute costs. We achieve competitive performance with much slower
models that require more time and tokens, and higher accuracy than similarly fast models. These values were computed
by averaging accuracy, time, and output token counts for a subset of 4 benchmarks: ChartQATEST, MathVistaMINI,
MMMUVAL, and ScreenSpot_v2.

## Architecture · Figure 3

Source page: 4 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/microsoft/technical-reports/phi-4-reasoning-vision--arxiv-v1.pdf#page=4)

![Architecture](figure-02.png)

Figure 3: Overview of the Phi-4-reasoning-vision-15B mid-fusion architecture. Images are processed by a SigLIP-2 vision
encoder and projected into the language embedding space via a cross-modality projector (MLP). The resulting visual
“soft” tokens are interleaved with text tokens and fed into the Phi-4-Reasoning language model.
