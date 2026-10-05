# StepAudio 3 Gen Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf) · [Official source](https://arxiv.org/abs/2609.12945)

## Architecture · Figure 1

Source page: 4 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf#page=4)

![Architecture](figure-01.png)

Figure 1: Overview of the StepAudio 3 Gen architecture. At each audio frame, the LLM predicts c0, and the RVQ Code
Predictor conditions on the LLM hidden state and c0 to predict c1, . . . , c15. All sixteen codes form the full RVQ frame
used for waveform decoding. ⊕denotes element-wise addition: at audio positions, the RVQ Adaptor output is added to
the corresponding token embedding (§2.2).

## Results · Figure 2

Source page: 12 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-gen--arxiv-v1.pdf#page=12)

![Results](figure-02.png)

Figure 2: Human evaluation on the Chinese human-likeness test set.
