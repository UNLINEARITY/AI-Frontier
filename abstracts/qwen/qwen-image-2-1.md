# Qwen-Image-2.1

[Official source](https://github.com/QwenLM/Qwen-Image-2.1)

Qwen-Image-2.1 is a single-stream DiT with the following design: Transformer: 32 layers, 7B parameters, single-stream architecture with block-causal attention ((q_idx >= kv_idx) or same_image_block). Text uses token-level causal mask; images use chunk-level bidirectional mask.
