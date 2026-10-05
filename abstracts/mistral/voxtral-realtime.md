# Voxtral Realtime

Models: Voxtral Realtime

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/mistral/technical-reports/voxtral-realtime--arxiv-v3.pdf#page=1) · [Official source](https://arxiv.org/abs/2602.11298)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

We introduce Voxtral Realtime, a natively streaming automatic speech recognition model that matches offline transcription quality at sub-second latency. Unlike approaches that adapt offline models through chunking or sliding windows, Voxtral Realtime is trained end-to-end for streaming, with explicit alignment between audio and text streams. Our architecture builds on the Delayed Streams Modeling framework, introducing a new causal audio encoder and Ada RMS-Norm for improved delay conditioning. We scale pretraining to a large-scale dataset spanning 13 languages. At a delay of 480ms, Voxtral Realtime achieves performance on par with Whisper, the most widely deployed offline transcription system. We release the model weights under the Apache 2.0 license.

## Core figures

[All figures and original captions](../../figures/mistral/voxtral-realtime/README.md) · [中文](../../figures/mistral/voxtral-realtime/README_CN.md)

### Results · Figure 1

Source page: 1 · [Original graphics PDF](../../figures/mistral/voxtral-realtime/figure-01.pdf) · [High-resolution PNG](../../figures/mistral/voxtral-realtime/figure-01.png)

![Results](../../figures/mistral/voxtral-realtime/figure-01.png)

Figure 1: Voxtral Realtime approaches offline accuracy at sub-second latency. Macro-average word error-
rate (WER) vs. delay on the FLEURS multilingual benchmark for realtime and offline models. Lower is better.
At 480 ms delay, Voxtral Realtime is competitive with Scribe v2 Realtime, the leading realtime API model,
as well as Whisper, the most popular open-source offline model. It surpasses both baselines at 960 ms delay,
approaching the performance of Voxtral Mini Transcribe V2, a state-of-the-art offline transcription model.

### Architecture · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/mistral/voxtral-realtime/figure-02.pdf) · [High-resolution PNG](../../figures/mistral/voxtral-realtime/figure-02.png)

![Architecture](../../figures/mistral/voxtral-realtime/figure-02.png)

Figure 2: Voxtral Realtime architecture and decoding scheme for a target delay τ = 80 ms. Voxtral
Realtime consists of a causal audio encoder to embed the input audio stream, an MLP adapter layer to temporally
downsample the audio embeddings, and a text decoder to auto-regressively generate the output text stream. The
downsampled audio embeddings from the adapter and the embeddings of previously generated tokens have the
same frame-rate of 12.5Hz, with each frame representing 80ms of audio. These are summed and processed by
the text decoder, which predicts one token per frame. The decoder emits a padding token [P] while waiting
for sufficient acoustic evidence. Once a word is acoustically complete and the target delay τ has elapsed, a
word-boundary token [W] is emitted to initiate generation, followed by the corresponding subword tokens.
