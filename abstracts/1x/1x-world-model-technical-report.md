# 1X World Model: Evaluating Bits, not Atoms

[Official source](https://www.1x.tech/discover/redwood-ai-world-model)

## Abstract

We share this supplementary technical progress report on the 1X World Model released at https://1x.tech/discover/redwood-ai-world-model. The 1X World Model (1XWM) is a generative video world model that predicts future robot observations and task-level state values. We train 1XWM to accurately forecast contacts and full-body manipulation given action commands, the first world model for a full-body humanoid. The 1X World Model achieves precise action controllability that enables us to compare different policies under identical observational conditions. We show that the accuracy of 1XWM as an evaluator scales with data from autonomous policy rollouts, and demonstrate high correlation between the world model and real world evaluation. We further show transfer in 1XWM prediction accuracy across different humanoid tasks. With 1XWM powering our evaluation engine, we can quickly iterate on checkpoint selection, architecture comparisons, and long-tail dataset curation.
