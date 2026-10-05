# Voxtral TTS

[中文](README_CN.md) · [Core figures](../../README.md)

[Original PDF](../../../pdfs/mistral/technical-reports/voxtral-tts--arxiv-v2.pdf) · [Official source](https://arxiv.org/abs/2603.25551)

## Results · Figure 1

Source page: 1 · [PNG](figure-01.png) · [PDF with original graphics](figure-01.pdf)

[View source page](../../../pdfs/mistral/technical-reports/voxtral-tts--arxiv-v2.pdf#page=1)

![Results](figure-01.png)

Figure 1: Voxtral TTS is preferred to ElevenLabs Flash v2.5 in human evaluations. We plot the win rate for
Voxtral TTS against ElevenLabs Flash v2.5 in human evaluations across two categories. For flagship voices, we
use the default voices for each model and 77 unique text examples. In the voice cloning set-up, we provide a
short audio reference clip and 60 text prompts. In both categories, human annotators blindly rate which audio is
better between the two models. Voxtral TTS is preferred in 58.3 and 68.4% of instances.

## Architecture · Figure 2

Source page: 3 · [PNG](figure-02.png) · [PDF with original graphics](figure-02.pdf)

[View source page](../../../pdfs/mistral/technical-reports/voxtral-tts--arxiv-v2.pdf#page=3)

![Architecture](figure-02.png)

Figure 2: Architecture overview of Voxtral TTS. A voice reference ranging from 3s-30s is fed to the Voxtral
Codec encoder to obtain audio tokens at a frame rate of 12.5 Hz. Each audio frame (labeled A) consists of a
semantic token and acoustic tokens. The voice reference audio tokens along with the text prompt tokens (labeled
T) are fed to the decoder backbone. The decoder auto-regressively generates a sequence of semantic tokens
until it reaches a special End of Audio token (<EOA>). At each timestep, the semantic token from the decoder
backbone is fed to a flow-matching transformer, which is run multiple times to predict the acoustic tokens. The
semantic and acoustic tokens are fed to the Voxtral Codec decoder to obtain the generated waveform.
