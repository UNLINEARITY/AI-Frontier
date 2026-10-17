# ShieldGemma 2

[Official source](https://ai.google.dev/gemma/docs/shieldgemma/model_card_2)

## Description

ShieldGemma 2, built on Gemma 3, is a 4 billion (4B) parameter model that checks the safety of both synthetic and natural images against key categories to help you build robust datasets and models. With this addition to the Gemma family of models, researchers and developers can now minimize the risk of harmful content affecting their Generative-AI powered applications across key harm types.

We recommend using ShieldGemma 2 as an input filter to vision language models, or as an output filter of image generation systems. To train a robust image safety model, we curated training datasets of natural and synthetic images and instruction-tuned Gemma 3 to demonstrate strong performance. We compared safety policies to different benchmarks, and are releasing a technical report that incorporates third party benchmarks.
