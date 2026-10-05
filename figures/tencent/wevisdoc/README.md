# WeVisDoc: From Coverage to Capability for Robust End-to-End Document Parsing

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf) · [Official source](https://huggingface.co/tencent/WeVisDoc-4B)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf#page=1)

![Results](figure-01.png)

Figure 1 WeVisDoc-4B leads the compared end-to-end parsers across all four reported settings. Bars show
scores on OmniDocBench v1.6 and the three PureDocBench robustness tracks; WeVisDoc-2B delivers top-tier end-to-
end performance at half the parameter count.

## Architecture · Figure 2

Source page: 6 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/tencent/technical-reports/wevisdoc--arxiv-v1.pdf#page=6)

![Architecture](figure-02.png)

Figure 2 Stage I data construction. Collected sources are normalized through multi-model labeling, while general
synthesis generates exact semantic and structural targets. Both data sources enter a shared clean pool. Appearance
augmentation is then applied according to the source to form the Stage I mixture.
