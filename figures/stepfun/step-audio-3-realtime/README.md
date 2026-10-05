# StepAudio 3 Realtime Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf) · [Official source](https://arxiv.org/abs/2609.14005)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf#page=1)

![Results](figure-01.png)

Figure 1: Benchmark results for StepAudio 3 ASR Max and StepAudio 3 Realtime (blue), compared with baselines (gray). Lower
is better for ASR error rates, and higher is better elsewhere. Dialogue averages eight dimensions, full duplex reports Overall, and
τ-Voice averages three domains. See Tables 1 and 10.

## Architecture · Figure 3

Source page: 4 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-realtime--arxiv-v2.pdf#page=4)

![Architecture](figure-02.png)

Figure 3: System architecture of StepAudio 3 Realtime. The LLM decoder receives audio representations through the audio
encoder and adapter, together with a separate text input. User and model audio form the two full-duplex streams, with generator
output returning to the model audio stream. Waveforms are schematic.
