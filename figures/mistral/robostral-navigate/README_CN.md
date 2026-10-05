# Robostral Navigate

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/mistral/technical-reports/robostral-navigate--arxiv-v3.pdf) · [官方来源](https://arxiv.org/abs/2607.20785)

## 架构 · Figure 1

原文第3页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/mistral/technical-reports/robostral-navigate--arxiv-v3.pdf#page=3)

![架构](figure-01.png)

Figure 1: System Architecture. Given a natural language instruction and a stream of RGB observations, the
VLM predicts the next waypoint at 0.5 hertz via pointing, metric displacement and orientation upon arrival.
When the target lies outside the field of view, pointing is omitted. A diffusion policy takes the waypoint, the
context frame (frame at which the waypoint has been inferred) and the current frame to produce a dense trajectory
at 10 hertz. Finally, a motion-tracking controller turns this trajectory into high-frequency actuator torques.

## 架构 · Figure 5

原文第7页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/mistral/technical-reports/robostral-navigate--arxiv-v3.pdf#page=7)

![架构](figure-02.png)

Figure 5: Overview of our online reinforcement learning pipeline. The trainer orchestrates the prompt sampling,
physical simulator, and action generator (vLLM) in an asynchronous loop, updating the policy via CISPO using
the −max(2, dist_to_goal) reward signal upon episode termination.
