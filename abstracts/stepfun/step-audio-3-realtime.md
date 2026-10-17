# StepAudio 3 Realtime Technical Report

[Official source](https://arxiv.org/abs/2609.14005)

## Abstract

Realtime spoken interaction demands deep reasoning, prompt responses, and ﬂuid turn-taking. We present StepAudio 3 Realtime, an audio-language foundation model organized around a continuous listen-converse-think-act loop. Deep Perception captures rich acoustic cues to interpret user intent, while Seamless Duplex models synchronized audio streams to handle pauses, backchannels, and interruptions naturally. Crucially, we resolve the tension between deep deliberation and latency via Think-While-Speaking, executing private reasoning in parallel with spoken delivery. In reasoning mode, StepAudio 3 reaches a 73.0 macro average on StepAudioChat. With Think-While-Speaking, it achieves dialogue and reasoning performance comparable to dedicated reasoning models while speaking in real time. Furthermore, an integrated Voice Agent handles asynchronous tool execution without disrupting the dialogue ﬂow. StepAudio 3 Realtime achieves top-tier performance across key dimensions: an exceptional 90.6 on the MMSU benchmark, 98.9 Overall on the Artiﬁcial Analysis Full-Duplex Bench, and a 56.0% macro task-success rate on τ -Voice.

## 3.1 System Architecture

StepAudio 3 Realtime uses a mixture-of-experts architecture. The audio frontend uses the Audio Transformer (AuT) encoder from Qwen3-Omni [8]. An adapter maps the encoder outputs into the representation space of the language model.

p. 3

![Figure 1](../../figures/stepfun/step-audio-3-realtime/figure-01.png)

Figure 1: Benchmark results for StepAudio 3 ASR Max and StepAudio 3 Realtime (blue), compared with baselines (gray). Lower is better for ASR error rates, and higher is better elsewhere. Dialogue averages eight dimensions, full duplex reports Overall, and τ-Voice averages three domains. See Tables 1 and 10.

p. 1

![Figure 3](../../figures/stepfun/step-audio-3-realtime/figure-02.png)

Figure 3: System architecture of StepAudio 3 Realtime. The LLM decoder receives audio representations through the audio encoder and adapter, together with a separate text input. User and model audio form the two full-duplex streams, with generator output returning to the model audio stream. Waveforms are schematic.

p. 4
