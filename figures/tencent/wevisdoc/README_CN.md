# WeVisDoc: From Coverage to Capability for Robust End-to-End Document Parsing

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf) · [官方来源](https://huggingface.co/tencent/WeVisDoc-4B)

## 主要结果 · Figure 1

原文第1页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf#page=1)

![主要结果](figure-01.png)

Figure 1 WeVisDoc-4B leads the compared end-to-end parsers across all four reported settings. Bars show
scores on OmniDocBench v1.6 and the three PureDocBench robustness tracks; WeVisDoc-2B delivers top-tier end-to-
end performance at half the parameter count.

## 架构 · Figure 2

原文第6页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf#page=6)

![架构](figure-02.png)

Figure 2 Stage I data construction. Collected sources are normalized through multi-model labeling, while general
synthesis generates exact semantic and structural targets. Both data sources enter a shared clean pool. Appearance
augmentation is then applied according to the source to form the Stage I mixture.
