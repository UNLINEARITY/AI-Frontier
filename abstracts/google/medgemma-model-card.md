# MedGemma

[Official source](https://developers.google.com/health-ai-developer-foundations/medgemma/model-card-v1)

## Description

MedGemma is a collection of Gemma 3 variants that are trained for performance on medical text and image comprehension. Developers can use MedGemma to accelerate building healthcare-based AI applications. MedGemma currently comes in three variants: a 4B multimodal version and 27B text-only and multimodal versions.

Both MedGemma multimodal versions utilize a SigLIP image encoder that has been specifically pre-trained on a variety of de-identified medical data, including chest X-rays, dermatology images, ophthalmology images, and histopathology slides. Their LLM components are trained on a diverse set of medical data, including medical text, medical question-answer pairs, FHIR-based electronic health record data (27B multimodal only), radiology images, histopathology patches, ophthalmology images, and dermatology images.
