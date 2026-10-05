# Phi-4-reasoning-vision-15B Technical Report

Models: Phi 4 Reasoning Vision

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/microsoft/technical-reports/phi-4-reasoning-vision--arxiv-v1.pdf#page=1) · [Official source](https://arxiv.org/abs/2603.03975)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Unlabelled opening summary

We present Phi-4-reasoning-vision-15B, a compact open-weight multimodal reasoning model, and share the motivations, design choices, experiments, and learnings that informed its development. Our goal is to contribute practical insight to the research community on building smaller, efficient multimodal reasoning models and to share the result of these learnings as an open-weight model that is good at com- mon vision and language tasks and excels at scientific and mathematical reasoning and understanding user interfaces. Our contributions include demonstrating that careful architecture choices and rigorous data curation enable smaller, open-weight multimodal models to achieve competitive performance with significantly less training and inference-time compute and tokens. The most substantial improvements come from systematic filtering, error correction, and synthetic augmentation—reinforcing that data qual- ity remains the primary lever for model performance. Systematic ablations show that high-resolution, dynamic-resolution encoders yield consistent improvements, as accurate perception is a prerequisite for high-quality reasoning. Finally, a hybrid mix of reasoning and non-reasoning data with explicit mode tokens allows a single model to deliver fast direct answers for simpler tasks and chain-of-thought reasoning for complex problems.

## Core figures

[All figures and original captions](../../figures/microsoft/phi-4-reasoning-vision/README.md) · [中文](../../figures/microsoft/phi-4-reasoning-vision/README_CN.md)

### Results · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/microsoft/phi-4-reasoning-vision/figure-01.pdf) · [High-resolution PNG](../../figures/microsoft/phi-4-reasoning-vision/figure-01.png)

![Results](../../figures/microsoft/phi-4-reasoning-vision/figure-01.png)

Figure 2: Phi-4-reasoning-vision-15B presents a compelling option compared to existing models, pushing the Pareto
frontier of the trade-off between accuracy and compute costs. We achieve competitive performance with much slower
models that require more time and tokens, and higher accuracy than similarly fast models. These values were computed
by averaging accuracy, time, and output token counts for a subset of 4 benchmarks: ChartQATEST, MathVistaMINI,
MMMUVAL, and ScreenSpot_v2.

### Architecture · Figure 3

Source page: 4 · [Original graphics PDF](../../figures/microsoft/phi-4-reasoning-vision/figure-02.pdf) · [High-resolution PNG](../../figures/microsoft/phi-4-reasoning-vision/figure-02.png)

![Architecture](../../figures/microsoft/phi-4-reasoning-vision/figure-02.png)

Figure 3: Overview of the Phi-4-reasoning-vision-15B mid-fusion architecture. Images are processed by a SigLIP-2 vision
encoder and projected into the language embedding space via a cross-modality projector (MLP). The resulting visual
“soft” tokens are interleaved with text tokens and fed into the Phi-4-Reasoning language model.
