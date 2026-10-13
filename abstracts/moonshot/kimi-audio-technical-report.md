# Kimi-Audio Technical Report

[PDF](../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf#page=1) · [Official source](https://github.com/MoonshotAI/Kimi-Audio)

## Abstract

We present Kimi-Audio, an open-source audio foundation model that excels in audio understanding, generation, and conversation. We detail the practices in building Kimi-Audio, including model architecture, data curation, training recipe, inference deployment, and evaluation. Specifically, we leverage a 12.5Hz audio tokenizer, design a novel LLM-based architecture with continuous features as input and discrete tokens as output, and develop a chunk-wise streaming detokenizer based on flow matching. We curate a pre-training dataset that consists of more than 13 million hours of audio data covering a wide range of modalities including speech, sound, and music, and build a pipeline to construct high-quality and diverse post-training data. Initialized from a pre-trained LLM, Kimi-Audio is continual pre-trained on both audio and text data with several carefully designed tasks, and then fine-tuned to support a diverse of audio-related tasks. Extensive evaluation shows that Kimi-Audio achieves state-of-the-art performance on a range of audio benchmarks including speech recognition, audio understanding, audio question answering, and speech conversation. We release the codes, model checkpoints, as well as the evaluation toolkits in https://github.com/MoonshotAI/Kimi-Audio.

![Figure 1](../../figures/moonshot/kimi-audio-technical-report/figure-01.png)

Figure 1: Performance of Kimi-Audio and previous audio langauge models including Qwen2-Audio [11], Baichuan-
Audio [41], Step-Audio [28], and Qwen2.5-Omni [73] on various benchmarks.

[p. 1](../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf#page=1) · [PDF](../../figures/moonshot/kimi-audio-technical-report/figure-01.pdf)

![Figure 2](../../figures/moonshot/kimi-audio-technical-report/figure-02.png)

Figure 2: Overview of the Kimi-Audio model architecture: (1) an audio tokenizer that extracts discrete semantic tokens
and a Whisper encoder that generates continuous acoustic features; (2) an audio LLM that processes audio inputs and
generates text and/or audio outputs; (3) an audio detokenizer converts audio tokens into waveforms.

[p. 4](../../pdfs/moonshot/technical-reports/kimi-audio-technical-report--arxiv-v1.pdf#page=4) · [PDF](../../figures/moonshot/kimi-audio-technical-report/figure-02.pdf)
