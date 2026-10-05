# Kimi K3 Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf) · [Official source](https://github.com/MoonshotAI/Kimi-K3)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf#page=1)

![Results](figure-01.png)

Figure 1: Kimi K3 main results.

## Architecture · Figure 2

Source page: 3 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/moonshot/technical-reports/kimi-k3-technical-report.pdf#page=3)

![Architecture](figure-02.png)

Figure 2: The Kimi K3 architecture, organized around token, channel, and layer mixing, with a native vision pathway at the input.
Each block contains three Kimi Delta Attention (KDA) layers followed by one Gated MLA layer, with each attention layer paired
with a Stable LatentMoE feed-forward network. Attention Residuals (AttnRes) use learned pseudo-queries (w) to derive attention
weights (α) over the embedding and preceding block outputs, enabling selective information flow across depth. Top left: the Stable
LatentMoE module with shared and routed experts. Bottom left: the KDA module. Bottom right: the native vision pathway.
