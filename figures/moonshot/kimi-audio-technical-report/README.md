# Kimi-Audio Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf) · [Official source](https://github.com/MoonshotAI/Kimi-Audio)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf#page=1)

![Results](figure-01.png)

Figure 1: Performance of Kimi-Audio and previous audio langauge models including Qwen2-Audio [11], Baichuan-
Audio [41], Step-Audio [28], and Qwen2.5-Omni [73] on various benchmarks.

## Architecture · Figure 2

Source page: 4 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf#page=4)

![Architecture](figure-02.png)

Figure 2: Overview of the Kimi-Audio model architecture: (1) an audio tokenizer that extracts discrete semantic tokens
and a Whisper encoder that generates continuous acoustic features; (2) an audio LLM that processes audio inputs and
generates text and/or audio outputs; (3) an audio detokenizer converts audio tokens into waveforms.
