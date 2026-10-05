# WeVisDoc: From Coverage to Capability for Robust End-to-End Document Parsing

Models: WeVisDoc-4B / 2B

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf#page=1) · [Official source](https://huggingface.co/tencent/WeVisDoc-4B)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

Document parsing converts document images into structured content and requires reliable performance across diverse layouts and acquisition conditions. Yet training corpora are bi- ased toward common document types and clean digital pages, while expanding coverage alone does not specify how to address a parser’s remaining weaknesses. We present WeVisDoc, a two-stage data-centric framework for robust end-to-end document parsing. Stage I broadens semantic, structural, and appearance coverage through heterogeneous data and structure- preserving degradation synthesis. Stage II uses a held-out probe to measure the Stage I parser’s residual errors within fixed visual–structural clusters. These diagnostics guide tar- geted data construction and reallocation of the target-token budget. WeVisDoc-4B achieves an Overall score of 95.38 on OmniDocBench v1.6 and a mean Overall score of 75.54 across the three PureDocBench tracks, ranking first among the compared end-to-end parsers in all four settings. Compared with Stage I, Stage II improves Overall scores for the 2B and 4B models on both benchmarks, with larger gains on the degraded PureDocBench tracks, including a 4.03-point gain for the 4B model on the Real Degraded track.

## Core figures

[All figures and original captions](../../figures/tencent/wevisdoc/README.md) · [中文](../../figures/tencent/wevisdoc/README_CN.md)

### Results · Figure 1

Source page: 1 · [Original graphics PDF](../../figures/tencent/wevisdoc/figure-01.pdf) · [High-resolution PNG](../../figures/tencent/wevisdoc/figure-01.png)

![Results](../../figures/tencent/wevisdoc/figure-01.png)

Figure 1 WeVisDoc-4B leads the compared end-to-end parsers across all four reported settings. Bars show
scores on OmniDocBench v1.6 and the three PureDocBench robustness tracks; WeVisDoc-2B delivers top-tier end-to-
end performance at half the parameter count.

### Architecture · Figure 2

Source page: 6 · [Original graphics PDF](../../figures/tencent/wevisdoc/figure-02.pdf) · [High-resolution PNG](../../figures/tencent/wevisdoc/figure-02.png)

![Architecture](../../figures/tencent/wevisdoc/figure-02.png)

Figure 2 Stage I data construction. Collected sources are normalized through multi-model labeling, while general
synthesis generates exact semantic and structural targets. Both data sources enter a shared clean pool. Appearance
augmentation is then applied according to the source to form the Stage I mixture.
