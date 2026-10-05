# Nemotron 3 Nano Omni: Efficient and Open Multimodal Intelligence

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf) · [Official source](https://arxiv.org/abs/2604.24954)

## Architecture · Figure 1

Source page: 3 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf#page=3)

![Architecture](figure-01.png)

Figure 1 | Nemotron 3 Nano Omni architecture. For encoding images and videos we use dynamic
resolution. Additionally, videos use Conv3D and optionally Efficient Video Sampling for higher
throughput. Audio inputs are encoded using Parakeet v2 audio encoder. Visual, audio, and text
tokens are concatenated and fed to the LLM.

## Architecture · Figure 2

Source page: 4 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf#page=4)

![Architecture](figure-02.png)

Figure 2 | Staged training recipe for the v3 omni-modal model. The pipeline first performs vision
SFT, then joint omni SFT while progressively extending context length, followed by omni-modal RL
training.
