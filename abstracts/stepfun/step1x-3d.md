# Step1X-3D: Towards High-Fidelity and Controllable Generation of Textured 3D Assets

Models: Step1X-3D

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/stepfun/technical-reports/step1x-3d--arxiv-v1.pdf#page=1) · [Official source](https://github.com/stepfun-ai/Step1X-3D)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

While generative artificial intelligence has advanced significantly across text, image, audio, and video domains, 3D generation remains comparatively underdeveloped due to fundamental challenges such as data scarcity, algorithmic limitations, and ecosystem fragmentation. To this end, we present Step1X-3D, an open framework addressing these challenges through: (1) a rigorous data curation pipeline process- ing >5M assets to create a 2M high-quality dataset with standardized geometric and textural properties; (2) a two-stage 3D-native architecture combining a hybrid VAE-DiT geometry generator with an diffusion-based texture synthesis module; and (3) the full open-source release of models, training code, and adaptation mod- ules. For geometry generation, the hybrid VAE-DiT component produces TSDF representations by employing perceiver-based latent encoding with sharp edge sam- pling for detail preservation. The diffusion-based texture synthesis module then ensures cross-view consistency through geometric conditioning and latent-space synchronization. Benchmark results demonstrate state-of-the-art performance that exceeds existing open-source methods, while also achieving competitive quality with proprietary solutions. Notably, the framework uniquely bridges the 2D and 3D generation paradigms by supporting direct transfer of 2D control techniques (e.g., LoRA) to 3D synthesis. By simultaneously advancing data quality, algorithmic fidelity, and reproducibility, Step1X-3D aims to establish new standards for open research in controllable 3D asset generation.

## Core figures

[All figures and original captions](../../figures/stepfun/step1x-3d/README.md) · [中文](../../figures/stepfun/step1x-3d/README_CN.md)

### Architecture · Figure 4

Source page: 8 · [Original graphics PDF](../../figures/stepfun/step1x-3d/figure-01.pdf) · [High-resolution PNG](../../figures/stepfun/step1x-3d/figure-01.png)

![Architecture](../../figures/stepfun/step1x-3d/figure-01.png)

Figure 4: Step1X-3D geometry diffusion framework. The framework enables seamless integration
of diverse conditions, allowing fine-tuning for various downstream tasks.

### Results · Figure 10

Source page: 16 · [Original graphics PDF](../../figures/stepfun/step1x-3d/figure-02.pdf) · [High-resolution PNG](../../figures/stepfun/step1x-3d/figure-02.png)

![Results](../../figures/stepfun/step1x-3d/figure-02.png)

Figure 10: User study. Average user preference score
is reported.
