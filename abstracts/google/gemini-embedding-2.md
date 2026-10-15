# Gemini Embedding 2: A Native Multimodal Embedding Model from Gemini

[Official source](https://arxiv.org/abs/2605.27295)

We introduce Gemini Embedding 2, a native multimodal embedding model that allows embedding video, audio, image, and text modalities in a unified representation space. We leverage the multimodal capabilities of Gemini to produce embeddings for arbitrary combinations of interleaved inputs across all these modalities that generalize well across a wide variety of tasks. Applying large-scale contrastive learning in a multi-task multi-stage training setup, we achieve state-of-the-art performance on key embedding benchmarks including unimodal, cross-modal, and multimodal retrieval spanning a diverse set of tasks. We show that our embedding model demonstrates strong performance (with a score of 62.9 R@1 on MSCOCO, 68.8 NDCG@10 on Vatex, 69.9 on MTEB multilingual and 84.0 on MTEB Code) across a variety of tasks surpassing the performance of specialized models. These unified capabilities make Gemini Embedding 2 a promising candidate for downstream use cases such as RAG, recommendation and search. Furthermore, its robust zero-shot performance across distinct fields – from astronomy and bioscience to fine arts and the culinary arts – establishes it as a highly reliable, out-of-the-box representation even for specialized domains.

![Figure 1](../../figures/google/gemini-embedding-2/figure-01.png)

Figure 1 | Conceptual overview of the Gemini Embedding 2 workflow. The model natively processes heterogeneous inputs—text, images, video, audio, documents, and their combinations—mapping them into a single, unified high-dimensional vector space where cross-modal semantic relationships are preserved.

p. 2

![Figure 2](../../figures/google/gemini-embedding-2/figure-02.png)

Figure 2 | Gemini Embedding 2 shows strong performance across multimodal retrieval tasks spanning image, text, video, and document modalities. ∗MTEB number is reported for Voyage-3.5 since Voyage-3.5-multimodal does not report MTEB.

p. 3
