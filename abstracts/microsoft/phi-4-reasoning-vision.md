# Phi-4-reasoning-vision-15B Technical Report

[Official source](https://arxiv.org/abs/2603.03975)

We present Phi-4-reasoning-vision-15B, a compact open-weight multimodal reasoning model, and share the motivations, design choices, experiments, and learnings that informed its development. Our goal is to contribute practical insight to the research community on building smaller, efficient multimodal reasoning models and to share the result of these learnings as an open-weight model that is good at common vision and language tasks and excels at scientific and mathematical reasoning and understanding user interfaces. Our contributions include demonstrating that careful architecture choices and rigorous data curation enable smaller, open-weight multimodal models to achieve competitive performance with significantly less training and inference-time compute and tokens. The most substantial improvements come from systematic filtering, error correction, and synthetic augmentation—reinforcing that data quality remains the primary lever for model performance. Systematic ablations show that high-resolution, dynamic-resolution encoders yield consistent improvements, as accurate perception is a prerequisite for high-quality reasoning. Finally, a hybrid mix of reasoning and non-reasoning data with explicit mode tokens allows a single model to deliver fast direct answers for simpler tasks and chain-of-thought reasoning for complex problems.

![Figure 2](../../figures/microsoft/phi-4-reasoning-vision/figure-01.png)

Figure 2: Phi-4-reasoning-vision-15B presents a compelling option compared to existing models, pushing the Pareto frontier of the trade-off between accuracy and compute costs. We achieve competitive performance with much slower models that require more time and tokens, and higher accuracy than similarly fast models. These values were computed by averaging accuracy, time, and output token counts for a subset of 4 benchmarks: ChartQATEST, MathVistaMINI, MMMUVAL, and ScreenSpot_v2.

p. 3

![Figure 3](../../figures/microsoft/phi-4-reasoning-vision/figure-02.png)

Figure 3: Overview of the Phi-4-reasoning-vision-15B mid-fusion architecture. Images are processed by a SigLIP-2 vision encoder and projected into the language embedding space via a cross-modality projector (MLP). The resulting visual “soft” tokens are interleaved with text tokens and fed into the Phi-4-Reasoning language model.

p. 4
