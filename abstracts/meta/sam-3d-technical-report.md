# SAM 3D: 3Dfy Anything in Images

Models: SAM 3D Objects / Body

[Source summaries](../README.md) · [中文索引](../README_CN.md)

[Original PDF](../../pdfs/meta/technical-reports/sam-3d-technical-report--arxiv-v2.pdf#page=1) · [Official source](https://arxiv.org/abs/2511.16624)

PDF pages: 1 · Source text cross-checked with two extractors; not manually verified.

## Unlabelled opening summary

We present SAM 3D, a generative model for visually grounded 3D object reconstruction, predicting geometry, texture, and layout from a single image. SAM 3D excels in natural images, where occlusion and scene clutter are common and visual recognition cues from context play a larger role. We achieve this with a human- and model-in-the-loop pipeline for annotating object shape, texture, and pose, providing visually grounded 3D reconstruction data at unprecedented scale. We learn from this data in a modern, multi-stage training framework that combines synthetic pretraining with real-world alignment, breaking the 3D “data barrier”. We obtain significant gains over recent work, with at least a 5 : 1 win rate in human preference tests on real-world objects and scenes. We will release our code and model weights, an online demo, and a new challenging benchmark for in-the-wild 3D object reconstruction.

## Core figures

[All figures and original captions](../../figures/meta/sam-3d-technical-report/README.md) · [中文](../../figures/meta/sam-3d-technical-report/README_CN.md)

### Architecture · Figure 2

Source page: 3 · [Original graphics PDF](../../figures/meta/sam-3d-technical-report/figure-01.pdf) · [High-resolution PNG](../../figures/meta/sam-3d-technical-report/figure-01.png)

![Architecture](../../figures/meta/sam-3d-technical-report/figure-01.png)

Figure 2 SAM 3D architecture. (top) SAM 3D first predicts coarse shape and layout with the Geometry model; (right)
the mixture of transformers architecture apply a two-stream approach with information sharing in the multi-modal
self-attention layer. (bottom) The voxels predicted by the Geometry model are passed to the Texture & Refinement
model, which adds higher resolution detail and textures.

### Results · Figure 8

Source page: 10 · [Original graphics PDF](../../figures/meta/sam-3d-technical-report/figure-02.pdf) · [High-resolution PNG](../../figures/meta/sam-3d-technical-report/figure-02.png)

![Results](../../figures/meta/sam-3d-technical-report/figure-02.png)

Figure 8 Preference comparison on scene-level and object-level reconstruction. Numbers indicate human preference rates.
Objects comparisons are done on textured meshes. SAM 3D is significantly preferred over others on all fronts.
