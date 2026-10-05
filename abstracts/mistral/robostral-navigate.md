# Robostral Navigate

Models: Robostral Navigate

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/mistral/technical-reports/robostral-navigate--arxiv-v3.pdf#page=2) · [Official source](https://arxiv.org/abs/2607.20785)

PDF pages: 2 · Source text cross-checked with two extractors; not manually verified.

## Abstract

Deploying navigation systems at scale requires a recipe that minimizes sensor assumptions, generalizes across robot embodiments, and trains efficiently. Yet, today’s best systems depend on depth sensors, multi-camera rigs, or pre-built maps, limiting the hardware they support and increasing deployment cost. We introduce Robostral Navigate, an 8B vision-language model built around this scalability objective. The model consumes only a stream of monocular RGB images—the most ubiquitous sensor across robotic platforms—and predicts waypoints by pointing to the next target location in the current camera view. Operating purely in image space, rather than robot-specific coordinates, makes the policy naturally robust to changes in camera intrinsics and scene scale, enabling deployment across wheeled, legged, and aerial robots without recalibration. We generate 2.4 million trajectories across 350k simulated scenes to reduce the reliance on real-world data collection and scale easily. We further introduce a prefix-caching training recipe that packs entire episodes into single training sequences, reducing training tokens by 22× and cutting training time from months to days. A tree-based attention mask prevents conditioning on previous ground-truth actions, encouraging visually grounded action prediction, and reinforcement learning is used to further improve exploration and recovery capabilities. On the Room-to-Room and Room-Across-Room in Continuous Environments (R2R-CE and RxR-CE) benchmarks, Robostral Navigate sets a new state of the art. On R2R-CE, it achieves a 77.4% success rate, surpassing the best monocular method by 10.5 points and the strongest depth- or multi-camera system by 5.3 points despite using only a single RGB camera. On RxR-CE, it reaches 75.1% success rate, outperforming all monocular baselines.

## Core figures

[All figures and original captions](../../figures/mistral/robostral-navigate/README.md) · [中文](../../figures/mistral/robostral-navigate/README_CN.md)

### Architecture · Figure 1

Source page: 3 · [Original graphics PDF](../../figures/mistral/robostral-navigate/figure-01.pdf) · [High-resolution PNG](../../figures/mistral/robostral-navigate/figure-01.png)

![Architecture](../../figures/mistral/robostral-navigate/figure-01.png)

Figure 1: System Architecture. Given a natural language instruction and a stream of RGB observations, the
VLM predicts the next waypoint at 0.5 hertz via pointing, metric displacement and orientation upon arrival.
When the target lies outside the field of view, pointing is omitted. A diffusion policy takes the waypoint, the
context frame (frame at which the waypoint has been inferred) and the current frame to produce a dense trajectory
at 10 hertz. Finally, a motion-tracking controller turns this trajectory into high-frequency actuator torques.

### Architecture · Figure 5

Source page: 7 · [Original graphics PDF](../../figures/mistral/robostral-navigate/figure-02.pdf) · [High-resolution PNG](../../figures/mistral/robostral-navigate/figure-02.png)

![Architecture](../../figures/mistral/robostral-navigate/figure-02.png)

Figure 5: Overview of our online reinforcement learning pipeline. The trainer orchestrates the prompt sampling,
physical simulator, and action generator (vLLM) in an asynchronous loop, updating the policy via CISPO using
the −max(2, dist_to_goal) reward signal upon episode termination.
