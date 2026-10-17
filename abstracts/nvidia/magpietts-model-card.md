# MagpieTTS Multilingual 357M v2607

[Official source](https://huggingface.co/nvidia/magpie_tts_multilingual_357m)

MagpieTTS is an end-to-end multilingual neural text-to-speech model that synthesizes speech using 5 English speaker voices — Aria, Jason, Leo, Sofia, and John Van Stan — across 12 languages: Arabic (ar), Chinese (zh), English (en), French (fr), German (de), Hindi (hi), Italian (it), Japanese (ja), Korean (ko), Portuguese (pt), Spanish (es), and Vietnamese (vi). The model adopts a transformer encoder–decoder architecture that autoregressively predicts discrete audio codec tokens, using multi-codebook prediction (typically 8 codebooks) with frame stacking (factor = 2) and a local transformer for fine-grained refinement of high-fidelity audio.
