# Visual assets

[简体中文](README_CN.md) · [Project home](../README.md)

Reusable assets for READMEs, GitHub Pages, and project introductions.

## Project identity

![AI Frontier horizontal banner](branding/ai-frontier-banner.png)

[Download the banner PNG](branding/ai-frontier-banner.png) · 2172 × 724 pixels

## Publisher and product icons

**18 publishers, 32 distinct brand and product marks, one SVG per mark.** All icons live in `vendors/`, with a default height of 256px and their original proportions. Vector paths scale without losing detail.

| Publisher | SVG files |
| --- | --- |
| OpenAI | [OpenAI](vendors/openai.svg) · [Codex](vendors/codex.svg) |
| Anthropic | [Anthropic](vendors/anthropic.svg) · [Claude](vendors/claude.svg) · [Claude Code](vendors/claude-code.svg) |
| Google / DeepMind | [Google](vendors/google.svg) · [DeepMind](vendors/deepmind.svg) · [Gemini](vendors/gemini.svg) · [Antigravity](vendors/antigravity.svg) · [Gemma](vendors/gemma.svg) |
| Meta | [Meta](vendors/meta.svg) |
| xAI | [xAI](vendors/xai.svg) · [Grok](vendors/grok.svg) |
| Mistral AI | [Mistral AI](vendors/mistral.svg) |
| NVIDIA | [NVIDIA](vendors/nvidia.svg) |
| DeepSeek | [DeepSeek](vendors/deepseek.svg) |
| Alibaba / Qwen | [Alibaba](vendors/alibaba.svg) · [Qwen](vendors/qwen.svg) |
| Moonshot AI / Kimi | [Moonshot AI](vendors/moonshot.svg) · [Kimi](vendors/kimi.svg) |
| Z.ai / Zhipu AI | [Z.ai](vendors/zai.svg) · [Zhipu AI](vendors/zhipu.svg) |
| MiniMax | [MiniMax](vendors/minimax.svg) |
| StepFun | [StepFun](vendors/stepfun.svg) |
| Tencent | [Tencent](vendors/tencent.svg) · [Hunyuan](vendors/hunyuan.svg) |
| ByteDance | [ByteDance](vendors/bytedance.svg) · [Doubao](vendors/doubao.svg) |
| Cohere | [Cohere](vendors/cohere.svg) |
| Microsoft | [Microsoft](vendors/microsoft.svg) |
| Amazon | [AWS](vendors/aws.svg) · [Nova](vendors/nova.svg) |

The Google DeepMind icon comes from its official website; the other SVGs come from the open-source community. See the [asset manifest](vendors/sources.json) for provenance and checksums. License notices are retained in [license 1](vendors/licenses/license-1.txt) and [license 2](vendors/licenses/license-2.txt).

Companies, products, and model families have distinct marks. Google, Gemini, and Antigravity each retain their own icon; the Amazon entry contains the AWS and Nova marks.

Use local paths and preserve brand colors and proportions. Third-party marks belong to their respective owners.

```html
<img src="assets/vendors/gemini.svg" alt="Gemini" width="96" height="96">
```
