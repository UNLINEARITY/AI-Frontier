# Kimi K3 Technical Report

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf) · [官方来源](https://github.com/MoonshotAI/Kimi-K3)

## 主要结果 · Figure 1

原文第1页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf#page=1)

![主要结果](figure-01.png)

Figure 1: Kimi K3 main results.

## 架构 · Figure 2

原文第3页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf#page=3)

![架构](figure-02.png)

Figure 2: The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.
Each block contains three Kimi Delta Attention (KDA) layers followed by one Gated MLA layer, with each attention layer paired
with a Stable LatentMoE feed-forward network. Attention Residuals (AttnRes) use learned pseudo-queries (w) to derive attention
weights (α) over the embedding and preceding block outputs, enabling selective information flow across depth. Top left: the Stable
LatentMoE module with shared and routed experts. Bottom left: the KDA module. Bottom right: the native vision pathway.
