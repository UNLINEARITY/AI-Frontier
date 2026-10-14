# Hy4-preview

[Official source](https://github.com/Tencent-Hunyuan/Hy4-preview)

## Model Introduction

Hy4 preview is a new-generation Mixture-of-Experts (MoE) flagship model developed by the Tencent Hy Team. The model comprises 770B total parameters, of which 49B are activated per token. The backbone consists of 78 layers, where the first layer uses a standard dense FFN and the remaining 77 layers replace it with MoE, each containing 256 routed experts and 1 shared expert; every token activates the top-8 routed experts along with the shared expert. In addition to the backbone, 1 native MTP layer (10B total parameters, 0.7B activated) is built in for speculative decoding.

On the architecture side, inspired by DeepSeek and GLM, the attention module employs Gated DeepSeek Sparse Attention (Gated DSA) with IndexCache for cross-layer sparse index reuse. The residual pathway uses iHC (identity Hyper-Connections) to expand inter-layer information flow.

![Table](../../figures/tencent/hy4-preview/figure-01.png)
