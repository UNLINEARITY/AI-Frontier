# GLM-TTS Technical Report

Models: GLM-TTS

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/zai/technical-reports/glm-tts-technical-report--arxiv-v1.pdf#page=1) · [Official source](https://github.com/zai-org/GLM-TTS)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## ABSTRACT

This work proposes GLM-TTS, a production-level TTS system designed for ef- ficiency, controllability, and high-fidelity speech generation. GLM-TTS follows a two-stage architecture, consisting of a text-to-token autoregressive model and a token-to-waveform diffusion model. With only 100k hours of training data, GLM- TTS achieves state-of-the-art performance on multiple open-source benchmarks. To meet production requirements, GLM-TTS improves speech quality through an optimized speech tokenizer with fundamental frequency constraints and a GRPO- based multi-reward reinforcement learning framework that jointly optimizes pro- nunciation, speaker similarity, and expressive prosody. In parallel, the system en- ables efficient and controllable deployment via parameter-efficient LoRA-based voice customization and a hybrid phoneme–text input scheme that provides pre- cise pronunciation control. Our code is available at https://github.com/ zai-org/GLM-TTS. Real-time speech synthesis demos are provided via Z.ai (audio.z.ai), the Zhipu Qingyan app/web (chatglm.cn).

## Core figures

[All figures and original captions](../../figures/zai/glm-tts-technical-report/README.md) · [中文](../../figures/zai/glm-tts-technical-report/README_CN.md)

### Architecture · Figure 1

Source page: 1 · [Original graphics PDF](../../figures/zai/glm-tts-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/zai/glm-tts-technical-report/figure-01.png)

![Architecture](../../figures/zai/glm-tts-technical-report/figure-01.png)

Figure 1: Overall Architecture of GLM-TTS

### Architecture · Figure 3

Source page: 5 · [Original graphics PDF](../../figures/zai/glm-tts-technical-report/figure-02.pdf) · [High-resolution PNG](../../figures/zai/glm-tts-technical-report/figure-02.png)

![Architecture](../../figures/zai/glm-tts-technical-report/figure-02.png)

Figure 3: An overview of the GLM-TTS-GRPO framework.
