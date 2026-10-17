# MAI-Code-1.1-Flash Model Card

[Official source](https://microsoft.ai/models/mai-code-1-flash/)

## Description

MAI-Code-1.1-Flash is a text-to-text and image-to-text coding model built for fast, efficient assistance in everyday developer workflows. The model is optimized to deliver high-quality coding help with low latency and low serving cost, making it well-suited for tasks such as agentic coding in real repositories, repository question answering, refactoring, and tool-using developer scenarios.

## Training, testing and validation

MAI-Code-1.1-Flash was trained end to end by Microsoft on carefully curated data using Microsoft infrastructure and data pipelines. The development pipeline spans pre-training, mid-training, supervised fine-tuning, and reinforcement learning, starting from MAI- Thinking-1's compressed 5B-active-parameter mid-training checkpoint. A lightweight supervised fine-tuning stage on curated instruction-following and agentic task data was applied on top of that mid-training checkpoint to establish reliable instruction- and format-following behavior.

p. 3

![Table](../../figures/microsoft/mai-code-1-1-flash-model-card/figure-01.png)

p. 5

![Table](../../figures/microsoft/mai-code-1-1-flash-model-card/figure-02.png)

p. 5
