# Gemma 4 Technical Report

[Official source](https://arxiv.org/abs/2607.02770)

We introduce Gemma 4, a new generation of open-weight, natively multimodal language models in the Gemma model family. Designed to advance compute efficiency and reasoning, the Gemma 4 model suite features dense and Mixture-of-Experts architectures, ranging from 2.3B to 31B parameters. Alongside improved vision and audio encoders for all model sizes, we propose a unified, encoder-free architecture for our 12B model, which ingests raw audio and image patches. Furthermore, we integrate a thinking mode, enabling Gemma models to generate reasoning traces prior to responding. We improve inference speed, memory, and compute efficiency, as well as long-context abilities through critical design choices. Gemma 4 establishes a leap in performance across STEM, multimodal, and long-context benchmarks, and rivals larger, frontier open models in human-rated tasks.

![Figure 1](../../figures/google/gemma-4-technical-report/figure-01.png)

Figure 1 | The autoregressive MTP drafter (blue blocks on the right) is fed activations and KV cache from the main model (gray blocks).

p. 3
