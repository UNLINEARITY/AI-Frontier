# SAM 3D Body: Robust Full-Body Human Mesh Recovery

Models: SAM 3D Objects / Body

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/meta/technical-reports/sam-3d-body-technical-report--arxiv-v1.pdf#page=1) · [Official source](https://arxiv.org/abs/2602.15989)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Unlabelled opening summary

We introduce SAM 3D Body (3DB), a promptable model for single-image full-body 3D human mesh recovery (HMR) that demonstrates state-of-the-art performance, with strong generalization and consistent accuracy in diverse in-the-wild conditions. 3DB estimates the human pose of the body, feet, and hands. It is the first model to use a new parametric mesh representation, Momentum Human Rig (MHR), which decouples skeletal structure and surface shape. 3DB employs an encoder–decoder architecture and supports auxiliary prompts, including 2D keypoints and masks, enabling user- guided inference similar to the SAM family of models. We derive high-quality annotations from a multi-stage annotation pipeline that uses various combinations of manual keypoint annotation, differentiable optimization, multi-view geometry, and dense keypoint detection. Our data engine efficiently selects and processes data to ensure data diversity, collecting unusual poses and rare imaging conditions. We present a new evaluation dataset organized by pose and appearance categories, enabling nuanced analysis of model behavior. Our experiments demonstrate superior generalization and substantial improvements over prior methods in both qualitative user preference studies and traditional quantitative analysis. Both 3DB and MHR are open-source.

## Core figures

[All figures and original captions](../../figures/meta/sam-3d-body-technical-report/README.md) · [中文](../../figures/meta/sam-3d-body-technical-report/README_CN.md)

### Architecture · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/meta/sam-3d-body-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/meta/sam-3d-body-technical-report/figure-01.png)

![Architecture](../../figures/meta/sam-3d-body-technical-report/figure-01.png)

Figure 2 SAM 3D Body Model Architecture. We employ a promptable encoder–decoder architecture with a shared
image encoder and separate decoders for body and hand pose estimation.

### Results · Figure 8

Source page: 13 · [Original graphics PDF](../../figures/meta/sam-3d-body-technical-report/figure-02.pdf) · [High-resolution PNG](../../figures/meta/sam-3d-body-technical-report/figure-02.png)

![Results](../../figures/meta/sam-3d-body-technical-report/figure-02.png)

Figure 8 Comparison of 3DB win rate against baselines for human preference study. Win rate (%) and number of wins
out of 80.
