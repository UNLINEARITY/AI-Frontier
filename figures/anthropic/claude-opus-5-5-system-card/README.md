# Claude Opus 5.5 System Card

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/anthropic/system-cards/claude-opus-5-5-system-card.pdf) · [Official source](https://www.anthropic.com/claude-opus-5-5-system-card)

## Results · Figure 2.2.3.2.3.A

Source page: 31 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/anthropic/system-cards/claude-opus-5-5-system-card.pdf#page=31)

![Results](figure-01.png)

[Figure 2.2.3.2.3.A] Autonomous research on AAV packaging rate prediction. Trendlines describe the 90th
percentile of validation set performance across individual attempts (n = 48). We find that our more capable
models rapidly improve using only a small number of scorer calls. Naive ESM-2 achieves a Spearman correlation
of 0.28 (not shown, to preserve dynamic range of trendlines). Right: The cumulative fraction of attempts that
exceed the threshold value of 0.52 over the course of the session.​

## Results · Figure 2.3.4.1.A

Source page: 37 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/anthropic/system-cards/claude-opus-5-5-system-card.pdf#page=37)

![Results](figure-02.png)

[Figure 2.3.4.1.A] Claude Opus 5.5, Claude Mythos 5.1, and Claude Opus 5 score within noise of each other on
CoBench 2.1. Each bar is the percentage of 500 problems that a model solved in one attempt. Claude Opus 5
scores 53.2%, Claude Mythos 5.1 scores 53.4%, and Claude Opus 5.5 scores 55.8%. All three models were
sampled through the API, with the API safety filter off, on the same version of the evaluation code and the same
500 problems. The Claude Opus 5.5 run took place 13 days after the other two. One change to the environment
in that interval is estimated to be worth 0 to 1 point, and two others have not been measured. The three scores
are not statistically distinguishable (a paired test on the same 500 problems gives p ≈ 0.2). These scores are not
comparable with the CoBench scores in earlier system cards.
