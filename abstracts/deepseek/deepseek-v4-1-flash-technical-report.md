# DeepSeek-V4.1-Flash: Pushing the Limits of KV Cache Compression

Models: DeepSeek-V4.1-Flash

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/deepseek/technical-reports/deepseek-v4-1-flash-technical-report--arxiv-v1.pdf#page=1) · [Official source](https://arxiv.org/abs/2609.19969)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

The widespread adoption of long-horizon agents has made model workloads increasingly input- heavy. Although prior work has substantially reduced the cost of long-context computation, prefill remains computationally expensive, and large KV caches continue to strain HBM and SSD capacity and data-transfer bandwidth. Together, these compute, storage, and bandwidth demands constitute the primary bottleneck to further lowering deployment costs. To address this challenge, we introduce DeepSeek-V4.1-Flash, a multimodal Mixture-of-Experts (MoE) model with 552B backbone parameters and support for contexts of up to one million tokens. With its Causal Encoder-Decoder (CED) architecture, the model activates 16B parameters per token during decode but only 8B parameters during prefill, substantially improving cost efficiency for agentic workloads. To push the limits of KV cache compression, DeepSeek-V4.1- Flash combines cross-layer KV cache reuse in Compressed Sparse Attention 2 (CSA2) with FP4 KV caching. These designs reduce its global KV cache footprint (always in HBM) to 890 bytes per token, roughly 1/4 of the corresponding footprint of DeepSeek-V4-Flash. Further, through a dedicated deployment optimization known as SWA Bounded Replay, DeepSeek-V4.1-Flash reduces its persistent KV cache footprint (always on SSD or in host memory) to roughly 1/8 of that of DeepSeek-V4-Flash. Despite its much smaller KV cache footprint, the model delivers substantially better performance than the baseline. In addition, we streamline the DeepSeek-V4 architecture and introduce several efficient architectural extensions. We pretrain DeepSeek-V4.1- Flash on a multimodal corpus comprising 45T tokens and conduct comprehensive post-training, yielding strong performance across diverse text-based and multimodal agentic scenarios. Model checkpoints are available at https://huggingface.co/deepseek-ai/DeepSeek-V4.1-Flash.

Figure 1 | (a) Performance of DeepSeek-V4.1-Flash and its counterparts on agentic benchmarks. (b) Global KV cache size per token (in bytes) across generations of DeepSeek models, highlight- ing DeepSeek’s sustained efforts to reduce context memory requirements. DeepSeek-V4.1-Flash achieves approximately 4-fold and 437-fold reductions in per-token global KV cache size relative to DeepSeek-V4-Flash and DeepSeek-V1, respectively.

## Core figures

[All figures and original captions](../../figures/deepseek/deepseek-v4-1-flash-technical-report/README.md) · [中文](../../figures/deepseek/deepseek-v4-1-flash-technical-report/README_CN.md)

### Results · Figure 1

Source page: 1 · [Original graphics PDF](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-01.png)

![Results](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-01.png)

Figure 1 | (a) Performance of DeepSeek-V4.1-Flash and its counterparts on agentic benchmarks.
(b) Global KV cache size per token (in bytes) across generations of DeepSeek models, highlight-
ing DeepSeek’s sustained efforts to reduce context memory requirements. DeepSeek-V4.1-Flash
achieves approximately 4-fold and 437-fold reductions in per-token global KV cache size relative
to DeepSeek-V4-Flash and DeepSeek-V1, respectively.

### Architecture · Figure 3

Source page: 7 · [Original graphics PDF](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-02.pdf) · [High-resolution PNG](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-02.png)

![Architecture](../../figures/deepseek/deepseek-v4-1-flash-technical-report/figure-02.png)

Figure 3 | Overall architecture of DeepSeek-V4.1-Flash. The 40-layer network is divided into
a causal encoder and a decoder, each with 20 layers. All feed-forward layers use standard
DeepSeekMoE. The first two encoder layers use sliding window attention (SWA); the rest use
Compressed Sparse Attention 2 (CSA2), with CSA2(ratio, mode) specifying the compression
ratio and mode. The model also uses Single-Pass mHC, Engram, DSpark, and a Hierarchical
Sparse Indexer.
