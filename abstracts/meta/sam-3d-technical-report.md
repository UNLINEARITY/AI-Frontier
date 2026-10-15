# SAM 3D: 3Dfy Anything in Images

[Official source](https://arxiv.org/abs/2511.16624)

We present SAM 3D, a generative model for visually grounded 3D object reconstruction, predicting geometry, texture, and layout from a single image. SAM 3D excels in natural images, where occlusion and scene clutter are common and visual recognition cues from context play a larger role. We achieve this with a human- and model-in-the-loop pipeline for annotating object shape, texture, and pose, providing visually grounded 3D reconstruction data at unprecedented scale. We learn from this data in a modern, multi-stage training framework that combines synthetic pretraining with real-world alignment, breaking the 3D “data barrier”. We obtain significant gains over recent work, with at least a 5 : 1 win rate in human preference tests on real-world objects and scenes. We will release our code and model weights, an online demo, and a new challenging benchmark for in-the-wild 3D object reconstruction.

![Figure 2](../../figures/meta/sam-3d-technical-report/figure-01.png)

Figure 2 SAM 3D architecture. (top) SAM 3D first predicts coarse shape and layout with the Geometry model; (right) the mixture of transformers architecture apply a two-stream approach with information sharing in the multi-modal self-attention layer. (bottom) The voxels predicted by the Geometry model are passed to the Texture & Refinement model, which adds higher resolution detail and textures.

p. 3

![Figure 8](../../figures/meta/sam-3d-technical-report/figure-02.png)

Figure 8 Preference comparison on scene-level and object-level reconstruction. Numbers indicate human preference rates. Objects comparisons are done on textured meshes. SAM 3D is significantly preferred over others on all fronts.

p. 10
