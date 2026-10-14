# DeepSeek-OCR 2: Visual Causal Flow

[Official source](https://github.com/deepseek-ai/DeepSeek-OCR-2)

## Abstract

We present DeepSeek-OCR 2 to investigate the feasibility of a novel encoder—DeepEncoder V2—capable of dynamically reordering visual tokens upon image semantics. Conventional vision-language models (VLMs) invariably process visual tokens in a rigid raster-scan order (top-left to bottom-right) with fixed positional encoding when fed into LLMs. However, this contradicts human visual perception, which follows flexible yet semantically coherent scanning patterns driven by inherent logical structures. Particularly for images with complex layouts, human vision exhibits causally-informed sequential processing. Inspired by this cognitive mech- anism, DeepEncoder V2 is designed to endow the encoder with causal reasoning capabilities, enabling it to intelligently reorder visual tokens prior to LLM-based content interpretation. This work explores a novel paradigm: whether 2D image understanding can be effectively achieved through two-cascaded 1D causal reasoning structures, thereby offering a new architectural approach with the potential to achieve genuine 2D reasoning. Codes and model weights are publicly accessible at http://github.com/deepseek-ai/DeepSeek-OCR-2.

![Figure 1](../../figures/deepseek/deepseek-ocr-2-visual-causal-flow/figure-01.png)

Figure 1 | We substitute the CLIP component in DeepEncoder with an LLM-style architecture.
By customizing the attention mask, visual tokens utilize bidirectional attention while learnable
queries adopt causal attention. Each query token can thus attend to all visual tokens and
preceding queries, allowing progressive causal reordering over visual information.

p. 1

![Figure 5](../../figures/deepseek/deepseek-ocr-2-visual-causal-flow/figure-02.png)

Figure 5 | Attention mask architecture of DeepEncoder V2. Concatenation of bidirectional mask
(vision tokens, ViT-like) and causal triangular mask (flow tokens, LLM decoder-style).

p. 7
