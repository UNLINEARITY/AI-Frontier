# HunyuanVideo 1.5 Technical Report

[Official source](https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5)

## Abstract

We present HunyuanVideo 1.5, a lightweight yet powerful open-source video generation model that achieves state-of-the-art visual quality and motion coherence with only 8.3 billion parameters, enabling efficient inference on consumer-grade GPUs. This achievement is built upon several key components, including meticulous data curation, an advanced DiT architecture featuring selective and sliding tile attention (SSTA), enhanced bilingual understanding through glyph-aware text encoding, progressive pre-training and post-training, and an efficient video super-resolution network. Leveraging these designs, we developed a unified framework capable of high-quality text-to-video and image-to-video generation across multiple durations and resolutions. Extensive experiments demonstrate that this compact and proficient model establishes a new state-of-the-art among open-source video generation models. By releasing the code and model weights, we provide the community with a high-performance foundation that lowers the barrier to video creation and research, making advanced video generation accessible to a broader audience. All open-source assets are publicly available at https://github.com/Tencent-Hunyuan/HunyuanVideo-1.5.

![Figure 1](../../figures/tencent/hunyuan-video-1-5/figure-01.png)

Figure 1: Caption Model Post-training Pipeline.

p. 3

![Figure 2](../../figures/tencent/hunyuan-video-1-5/figure-02.png)

Figure 2: Architecture of the Unified Diffusion Transformer.

p. 4
