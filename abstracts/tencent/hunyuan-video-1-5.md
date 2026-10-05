# HunyuanVideo 1.5 Technical Report

Models: HunyuanVideo 1.5

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/tencent/technical-reports/hunyuan-video-1-5--arxiv-v2.pdf#page=1) · [Official source](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

We present HunyuanVideo 1.5, a lightweight yet powerful open-source video generation model that achieves state-of-the-art visual quality and motion coher- ence with only 8.3 billion parameters, enabling efficient inference on consumer- grade GPUs. This achievement is built upon several key components, including meticulous data curation, an advanced DiT architecture featuring selective and sliding tile attention (SSTA), enhanced bilingual understanding through glyph- aware text encoding, progressive pre-training and post-training, and an efficient video super-resolution network. Leveraging these designs, we developed a unified framework capable of high-quality text-to-video and image-to-video generation across multiple durations and resolutions. Extensive experiments demonstrate that this compact and proficient model establishes a new state-of-the-art among open-source video generation models. By releasing the code and model weights, we provide the community with a high-performance foundation that lowers the barrier to video creation and research, making advanced video generation ac- cessible to a broader audience. All open-source assets are publicly available at https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5.

## Core figures

[All figures and original captions](../../figures/tencent/hunyuan-video-1-5/README.md) · [中文](../../figures/tencent/hunyuan-video-1-5/README_CN.md)

### Architecture · Figure 1

Source page: 3 · [Original graphics PDF](../../figures/tencent/hunyuan-video-1-5/figure-01.pdf) · [High-resolution PNG](../../figures/tencent/hunyuan-video-1-5/figure-01.png)

![Architecture](../../figures/tencent/hunyuan-video-1-5/figure-01.png)

Figure 1: Caption Model Post-training Pipeline.

### Architecture · Figure 2

Source page: 4 · [Original graphics PDF](../../figures/tencent/hunyuan-video-1-5/figure-02.pdf) · [High-resolution PNG](../../figures/tencent/hunyuan-video-1-5/figure-02.png)

![Architecture](../../figures/tencent/hunyuan-video-1-5/figure-02.png)

Figure 2: Architecture of the Unified Diffusion Transformer.
