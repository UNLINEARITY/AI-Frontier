# System Card: Claude Sonnet 5.5

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/anthropic/system-cards/claude-sonnet-5-5-system-card.pdf) · [官方来源](https://www.anthropic.com/claude-sonnet-5-5-system-card)

## 主要结果 · Figure 2.3.2.A

原文第21页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/anthropic/system-cards/claude-sonnet-5-5-system-card.pdf#page=21)

![主要结果](figure-01.png)

[Figure 2.3.2.A] The Epoch Capabilities Index (ECI) synthesizes performance across many benchmarks into one
number per model. Our version of this metric, the Anthropic ECI (AECI), is powered by internal benchmark
results, so scores are not directly comparable to Epoch’s public ECI leaderboard. Gray dots are previous frontier
Claude models; colored dots are the most recent models. Thin black error bars are 95% CI over 100 IRT refits,
each on a random 80% subsample of benchmarks (global error). Thick violet error bars come from the same
resampled fits but measure each score’s movement relative to the three preceding releases for each model
(local error). The two lines compare different hypotheses for the frontier trend. Claude Sonnet 3.5 (June 2024)
anchors the ECI scale at 130, so it has no global CI (its local error bar reflects uncertainty in the models before
it). Scores of recent models on the new scale are reported for direct comparison.

## 主要结果 · Figure 8.4.A

原文第111页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/anthropic/system-cards/claude-sonnet-5-5-system-card.pdf#page=111)

![主要结果](figure-02.png)

[Figure 8.4.A] FrontierCode v1.1 Main score versus average output tokens per task across reasoning effort levels (low, medium, high, xhigh, and max; GPT-6 Astra also at none). Cognition ran the evaluation for every
model shown and reported the results; Claude models were run in Claude Code and GPT models were run in
Codex CLI. Cognition’s result files report token counts for every model and no cost for Claude Sonnet 5.5, so
the x-axis shows average output tokens per task on a logarithmic scale. Each Claude Sonnet 5.5 point is labeled
with its effort level; for every other model the labeled points are its lowest and highest effort levels and the level at which it scored highest (GPT-6 Astra also at low). Unlabeled points follow the line in order of effort. The
result files carry no uncertainty intervals, so none are shown; Cognition's published figures report error bars.
Note that the y-axis begins at 27%, not at zero, so differences between points are visually magnified.
