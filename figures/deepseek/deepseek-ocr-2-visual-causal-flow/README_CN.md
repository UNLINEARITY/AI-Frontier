# DeepSeek-OCR 2: Visual Causal Flow

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/deepseek/technical-reports/deepseek-ocr-2-visual-causal-flow--arxiv-v1.pdf) · [官方来源](https://github.com/deepseek-ai/DeepSeek-OCR-2)

## 整体概览 · Figure 1

原文第1页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/deepseek/technical-reports/deepseek-ocr-2-visual-causal-flow--arxiv-v1.pdf#page=1)

![整体概览](figure-01.png)

Figure 1 | We substitute the CLIP component in DeepEncoder with an LLM-style architecture.
By customizing the attention mask, visual tokens utilize bidirectional attention while learnable
queries adopt causal attention. Each query token can thus attend to all visual tokens and
preceding queries, allowing progressive causal reordering over visual information.

## 架构 · Figure 5

原文第7页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/deepseek/technical-reports/deepseek-ocr-2-visual-causal-flow--arxiv-v1.pdf#page=7)

![架构](figure-02.png)

Figure 5 | Attention mask architecture of DeepEncoder V2. Concatenation of bidirectional mask
(vision tokens, ViT-like) and causal triangular mask (flow tokens, LLM decoder-style).
