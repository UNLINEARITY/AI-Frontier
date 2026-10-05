# Post-Training Language Models for Gold-Medal Performance in Coding Competitions

Models: Nemotron Labs 3 Competitive Coding 550B-A55B

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/nvidia/technical-reports/nemotron-3-competitive-coding--arxiv-v2.pdf#page=1) · [Official source](https://arxiv.org/abs/2609.02849)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract.

Competitive programming has become a key test of large language model reasoning, with international competitions such as IOI and ICPC representing its most challenging settings. We present an end-to-end specialization pipeline combining large-scale problem curation, synthetic reasoning traces, supervised fine-tuning (SFT), and reinforcement learning (RL). Using 22,000 curated problems, we train Nemotron-3-Nano-CC (30B-A3B) with SFT and RL and Nemotron-3-Ultra-CC (550B-A55B) with SFT alone. We further introduce GenCorrect, a feedback-driven test-time compute strategy that iteratively generates, evaluates, and refines diverse solutions. On IOI 2025, Nano-CC improves from 130 points to 291 after post-training and to 468 with GenCorrect, exceeding the gold threshold of 438.3 while Ultra-CC reaches 502. Guided by these results, we develop a competition-specific Ultra-CC system and evaluate it prospectively during IOI 2026. Under the same time, internet-access, and submission constraints as human contestants, it scores 535.4 out of 600, exceeding both the gold threshold of 361.12 and the top human score of 498.27. To our knowledge, this is the first AI system to outscore the highest-scoring human contestant on an IOI problem set.

## Core figures

[All figures and original captions](../../figures/nvidia/nemotron-3-competitive-coding/README.md) · [中文](../../figures/nvidia/nemotron-3-competitive-coding/README_CN.md)

### Results · Figure 1

Source page: 2 · [Original graphics PDF](../../figures/nvidia/nemotron-3-competitive-coding/figure-01.pdf) · [High-resolution PNG](../../figures/nvidia/nemotron-3-competitive-coding/figure-01.png)

![Results](../../figures/nvidia/nemotron-3-competitive-coding/figure-01.png)

Figure 1 | Performance of our pipeline and models on IOI 2025 and IOI 2026.

### Architecture · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/nvidia/nemotron-3-competitive-coding/figure-02.pdf) · [High-resolution PNG](../../figures/nvidia/nemotron-3-competitive-coding/figure-02.png)

![Architecture](../../figures/nvidia/nemotron-3-competitive-coding/figure-02.png)

Figure 2 | Our competitive-programming pipeline. Nemotron-3-Nano-CC undergoes supervised
fine-tuning and reinforcement learning, while Nemotron-3-Ultra-CC uses supervised fine-tuning only.
Both models use GenCorrect at inference time.
