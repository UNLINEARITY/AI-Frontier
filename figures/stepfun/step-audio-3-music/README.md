# StepAudio 3 Music Technical Report

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/stepfun/technical-reports/step-audio-3-music--arxiv-v1.pdf) · [Official source](https://arxiv.org/abs/2609.16034)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-music--arxiv-v1.pdf#page=1)

![Results](figure-01.png)

Figure 1: Relative performance across MuQ-MuLan, AudioBox-Aesthetics, and SongBench. Outer arcs identify the three
benchmark families. Scores are divided by the best observed score per metric (1.0), not a theoretical maximum; the radial axis is
truncated to 0.60–1.00. Purple denotes StepAudio 3 Music. Compare systems within each metric; polygon area is not an aggregate
score. Curves provide a visual approximation; exact scores are in table 3.

## Overview · Figure 2

Source page: 4 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/stepfun/technical-reports/step-audio-3-music--arxiv-v1.pdf#page=4)

![Overview](figure-02.png)

Figure 2: Overview of StepAudio 3 Music. Lyrics, a text prompt, and optional task-speciﬁc references are serialized for a
trainable Mixture-of-Experts autoregressive model. In ABC-CoT mode, the model ﬁrst produces an explicit arrangement plan and
then predicts a 50-Hz sequence from a 65536-entry single codebook. A separately trained renderer generates 50-Hz StepAudio VAE
latents with a ﬂow-matching DiT and decodes them into 48-kHz waveform audio. The renderer is held ﬁxed during autoregressive-
model training.
