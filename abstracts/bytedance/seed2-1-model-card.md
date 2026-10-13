# Seed2.1 Model Card: Agentic Intelligence for Productivity

[Official source](https://seed.bytedance.com/en/seed_model_portfolio)

## Introduction

As ByteDance’s flagship model family, Seed has been developed with a long-standing commitment to understanding users’ real needs, supporting a wide range of work and life scenarios, and empowering users to think, create, and work with greater confidence.

Through the previous cycle of user feedback and model iteration, the Seed team has developed a deeper understanding of what truly matters for LLM-based agents as productivity tools. Their core value does not lie in scaling interactions alone, but in creating genuine productivity value for each individual user. A capable agent should not merely respond to prompts; it should help users navigate complex decisions, complete demanding tasks, and produce reliable outcomes in real workflows.

Seed2.1 marks a critical turning point for the Seed model family. For the first time, complex needs from daily life, professional productivity, and frontier exploration have been placed at the center of our model development priorities, ahead of traffic-driven general usage alone. This shift has led to substantial improvements in both intelligence and reliability, enabling Seed2.1 to better serve as a trusted partner across real-world scenarios.

In this release, we introduce two Seed2.1 model variants: Seed2.1 Turbo and Seed2.1 Pro. Seed2.1 Turbo is designed for efficient, high-throughput product scenarios, while Seed2.1 Pro targets stronger reasoning, agentic execution, and complex productivity workflows. Together, they form a practical model family for both everyday user assistance and demanding professional tasks.

As model capabilities continue to evolve, we observe two important changes in how they should be evaluated. First, model evaluation is moving beyond static benchmarks and becoming increasingly tied to real user experience. Second, model performance is becoming more deeply integrated with the harness, tools, and product environment in which the model operates. In other words, the value of an agent should be measured not only by isolated capability scores, but also by whether it can perform reliably in the actual product workflows that users depend on.

To address these changes, the Seed team adopted a product-driven development and evaluation methodology for Seed2.1:

![Figure 5](../../figures/bytedance/seed2-1-model-card/figure-01.png)

Figure 5 Efficiency of the Generalist Computer-Use Agent (CUA) setting on OSWorld. For each model, the arrow
points from the GUI-only operating point (open marker) to the Generalist CUA setting (filled marker), in which the
agent may also issue commands and call tools. Both models move up and to the left: higher success rate with fewer
steps per task.

p. 13

![Figure 16](../../figures/bytedance/seed2-1-model-card/figure-02.png)

Figure 16 Seed-for-Seed development loop. Seed2.1 participates in evaluation, data, training, and infrastructure loops
through long-horizon execution and continuous target-driven iteration.

p. 28
