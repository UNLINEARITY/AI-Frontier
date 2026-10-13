# Nemotron 3 Nano Omni: Efficient and Open Multimodal Intelligence

[PDF](../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf#page=1) · [Official source](https://arxiv.org/abs/2604.24954)

## Abstract.

We introduce Nemotron 3 Nano Omni, the latest model in the Nemotron multimodal series and the first to natively support audio inputs alongside text, images, and video. Nemotron 3 Nano Omni delivers consistent accuracy improvements over its predecessor, Nemotron Nano V2 VL, across all modalities, enabled by advances in architecture, training data and recipes. In particular, Nemotron 3 delivers leading results in real-world document understanding, long audio-video comprehension, and agentic computer use. Built on the highly efficient Nemotron 3 Nano 30B-A3B backbone, Nemotron 3 Nano Omni further incorporates innovative multimodal token-reduction techniques to deliver substantially lower inference latency and higher throughput than other models of similar size. We are releasing model checkpoints in BF16, FP8, and FP4 formats, along with portions of the training data and codebase to facilitate further research and development.

![Figure 1](../../figures/nvidia/nemotron-3-nano-omni/figure-01.png)

Figure 1 | Nemotron 3 Nano Omni architecture. For encoding images and videos we use dynamic
resolution. Additionally, videos use Conv3D and optionally Efficient Video Sampling for higher
throughput. Audio inputs are encoded using Parakeet v2 audio encoder. Visual, audio, and text
tokens are concatenated and fed to the LLM.

[p. 3](../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf#page=3) · [PDF](../../figures/nvidia/nemotron-3-nano-omni/figure-01.pdf)

![Figure 2](../../figures/nvidia/nemotron-3-nano-omni/figure-02.png)

Figure 2 | Staged training recipe for the v3 omni-modal model. The pipeline first performs vision
SFT, then joint omni SFT while progressively extending context length, followed by omni-modal RL
training.

[p. 4](../../pdfs/nvidia/technical-reports/nemotron-3-nano-omni--arxiv-v2.pdf#page=4) · [PDF](../../figures/nvidia/nemotron-3-nano-omni/figure-02.pdf)
