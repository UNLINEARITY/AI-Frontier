# SAM 3D: 3Dfy Anything in Images

[English](README.md) · [核心图片](../../README_CN.md)

[原始 PDF](../../../pdfs/meta/technical-reports/sam-3d-technical-report--arxiv-v2.pdf) · [官方来源](https://arxiv.org/abs/2511.16624)

## 架构 · Figure 2

原文第3页 · [PNG](figure-01.png) · [保留原始图形的 PDF](figure-01.pdf)

[查看原页](../../../pdfs/meta/technical-reports/sam-3d-technical-report--arxiv-v2.pdf#page=3)

![架构](figure-01.png)

Figure 2 SAM 3D architecture. (top) SAM 3D first predicts coarse shape and layout with the Geometry model; (right)
the mixture of transformers architecture apply a two-stream approach with information sharing in the multi-modal
self-attention layer. (bottom) The voxels predicted by the Geometry model are passed to the Texture & Refinement
model, which adds higher resolution detail and textures.

## 主要结果 · Figure 8

原文第10页 · [PNG](figure-02.png) · [保留原始图形的 PDF](figure-02.pdf)

[查看原页](../../../pdfs/meta/technical-reports/sam-3d-technical-report--arxiv-v2.pdf#page=10)

![主要结果](figure-02.png)

Figure 8 Preference comparison on scene-level and object-level reconstruction. Numbers indicate human preference rates.
Objects comparisons are done on textured meshes. SAM 3D is significantly preferred over others on all fronts.
