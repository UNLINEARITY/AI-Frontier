# Qwen-Audio-3.0-ASR Technical Report

Models: Qwen-Audio-3.0-ASR

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/qwen/technical-reports/qwen-audio-3-0-asr--arxiv-v2.pdf#page=1) · [Official source](https://arxiv.org/abs/2609.07549)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

In recent years, automatic speech recognition (ASR) has witnessed transformative advancements driven by three complementary paradigms: data scaling, model scaling, and deep integration with large language models (LLMs). However, bridg- ing the gap between academic benchmark performance and real-world production utility remains a persistent challenge, particularly in handling diverse regional dialects, dynamic entities and hotwords, long-range contextual information, and disfluent spontaneous speech. In this report, we present Qwen-Audio-3.0-ASR, a Mixture-of-Experts (MoE) LLM-based ASR system designed to address these production demands through a unified, instruction-following framework. The model is built upon the Qwen backbone, and is trained on tens of millions of hours of large-scale speech data. Qwen-Audio-3.0-ASR supports transcription across 30 languages and 16 Chinese dialectal varieties spanning eight major di- alect regions. Beyond multilingual and dialectal recognition, the model provides production-oriented capabilities including industry-domain entity recognition, hi- erarchical hotword customization, native single-pass transcription polishing, and long-audio contextual modeling. We further develop a dedicated streaming variant, Qwen-Audio-3.0-ASR-Streaming, for latency-sensitive applications. Extensive evaluations on Chinese, English, multilingual, and real-world industrial test sets demonstrate state-of-the-art or highly competitive recognition performance across a broad range of evaluation conditions, with strong performance relative to leading commercial and proprietary systems including GPT-4o Transcribe and Gemini 3.1 Pro.

## Core figures

[All figures and original captions](../../figures/qwen/qwen-audio-3-0-asr/README.md) · [中文](../../figures/qwen/qwen-audio-3-0-asr/README_CN.md)

### Overview · Figure 1

Source page: 2 · [Original graphics PDF](../../figures/qwen/qwen-audio-3-0-asr/figure-01.pdf) · [High-resolution PNG](../../figures/qwen/qwen-audio-3-0-asr/figure-01.png)

![Overview](../../figures/qwen/qwen-audio-3-0-asr/figure-01.png)

Figure 1: Overview of Qwen-Audio-3.0-ASR and its production-oriented capabilities. The system
supports multilingual and dialectal recognition, low-latency streaming, domain entity recognition,
long-audio contextual modeling, hierarchical hotword customization, and native single-pass tran-
scription polishing. The central ring highlights four system-level properties: instruction-controlled
decoding, context awareness, native single-pass generation, and low latency.

### Results · Figure 6

Source page: 14 · [Original graphics PDF](../../figures/qwen/qwen-audio-3-0-asr/figure-02.pdf) · [High-resolution PNG](../../figures/qwen/qwen-audio-3-0-asr/figure-02.png)

![Results](../../figures/qwen/qwen-audio-3-0-asr/figure-02.png)

Figure 6: Character error rate (CER, %) on an internal evaluation suite covering 16 Chinese dialects
under the ASR and AST settings described in Section 5.2. We compare Doubao-ASR, Tencent
Hy-ASR-3.0-preview, and Qwen-Audio-3.0-ASR. Lower values indicate better performance.
