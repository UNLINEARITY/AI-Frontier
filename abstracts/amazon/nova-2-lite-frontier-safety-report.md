# Evaluating Nova 2.0 Lite model under Amazon's Frontier Model Safety Framework

Models: Nova 2 Lite / Pro Preview

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/amazon/system-cards/nova-2-lite-frontier-safety-report--arxiv-v1.pdf#page=1) · [Official source](https://arxiv.org/abs/2601.19134)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Abstract

Amazon published its Frontier Model Safety Framework (FMSF) as part of the Paris AI summit, following which we presented a report on Amazon’s Premier model [7]. In this report, we present an evaluation of Nova 2.0 Lite. Nova 2.0 Lite was made generally available from amongst the Nova 2.0 series and is one of its most capable reasoning models. The model processes text, images, and video with a context length of up to 1M tokens, enabling analysis of large codebases, documents, and videos in a single prompt. We present a comprehensive evaluation of Nova 2.0 Lite’s critical risk profile under the FMSF [1]. Evaluations target three high-risk domains–Chemical, Biological, Radiological and Nuclear (CBRN), Offensive Cyber Operations, and Automated AI R&D–and combine automated benchmarks, expert red-teaming, and uplift studies to determine whether the model exceeds release thresholds. We summarize our methodology and report core findings. We will continue to enhance our safety evaluation and mitigation pipelines as new risks and capabilities associated with frontier models are identified.

## Core figures

[All figures and original captions](../../figures/amazon/nova-2-lite-frontier-safety-report/README.md) · [中文](../../figures/amazon/nova-2-lite-frontier-safety-report/README_CN.md)

### Safety Evaluation · Figure 1

Source page: 2 · [Original graphics PDF](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-01.pdf) · [High-resolution PNG](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-01.png)

![Safety Evaluation](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-01.png)

Figure 1: CBRN automated benchmark results comparing models across four datasets. For Nova 2.0 Lite, we present
the best result among all the reasoning modes (low’,’medium’, and ‘high’).

### Safety Evaluation · Figure 2

Source page: 4 · [Original graphics PDF](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-02.pdf) · [High-resolution PNG](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-02.png)

![Safety Evaluation](../../figures/amazon/nova-2-lite-frontier-safety-report/figure-02.png)

Figure 2: Offensive Cyber Security Knowledge Benchmarks comparing Nova 2.0 Lite against previous generation
baselines. For Nova 2.0 Lite, we present the best result among all the reasoning modes (‘low’, ‘medium’, and ‘high’).
