# MAI-Image-2.6 / MAI-Image-2.6-Flash Model Card

[Official source](https://microsoft.ai/models/mai-image-2-6/)

## Model Overview

MAI-Image-2.6 is a diffusion-based generative model designed for both text-to-image synthesis and controllable image-to-image editing. It operates by progressively transforming random noise into a coherent image that aligns with a given text prompt. This approach leverages a flow-matching loss to learn a continuous transformation between the noise distribution and the data distribution, ensuring stable and efficient training.

MAI-Image-2.6 was rebuilt from the ground up for multimodal editing workflows, with stronger visual context understanding and coherence. It reasons across objects, scene structure, lighting, scale, and spatial positioning to produce consistent edits — even from ambiguous prompts. The model gracefully handles multiple constraints at once, including layout preservation, object changes, text updates, and contextual adaptation.

It supports reliable object removal, replacement, attribute changes, inpainting, and image enhancement without destabilizing composition or layout. The model also maintains strong visual consistency across iterative edits.

This combination of flow-matching objectives and diffusion inference enables the model to produce high-quality, diverse images that maintain strong alignment with the input text, making it suitable for creative generation, design tasks, production editing workflows, and multimodal applications.

## Training, Testing, and Validation Datasets

The training dataset consists of paired images and text descriptions, where each caption provides a detailed account of the visual content. The data spans a broad, general-purpose domain including everyday objects, natural scenes, people, and abstract concepts, making it suitable for open-domain text-to-image generation and image editing. The dataset combines visual data (images) with natural language text, enabling multimodal learning.

p. 4
