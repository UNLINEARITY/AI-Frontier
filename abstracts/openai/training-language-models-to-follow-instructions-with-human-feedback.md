# Training language models to follow instructions with human feedback

[Official source](https://arxiv.org/abs/2203.02155)

## Abstract

Making language models bigger does not inherently make them better at following a user’s intent. For example, large language models can generate outputs that are untruthful, toxic, or simply not helpful to the user. In other words, these models are not aligned with their users. In this paper, we show an avenue for aligning language models with user intent on a wide range of tasks by ﬁne-tuning with human feedback. Starting with a set of labeler-written prompts and prompts submitted through the OpenAI API, we collect a dataset of labeler demonstrations of the desired model behavior, which we use to ﬁne-tune GPT-3 using supervised learning. We then collect a dataset of rankings of model outputs, which we use to further ﬁne-tune this supervised model using reinforcement learning from human feedback. We call the resulting models InstructGPT. In human evaluations on our prompt distribution, outputs from the 1.3B parameter InstructGPT model are preferred to outputs from the 175B GPT-3, despite having 100x fewer parameters. Moreover, InstructGPT models show improvements in truthfulness and reductions in toxic output generation while having minimal performance regressions on public NLP datasets. Even though InstructGPT still makes simple mistakes, our results show that ﬁne-tuning with human feedback is a promising direction for aligning language models with human intent.

![Figure 2](../../figures/openai/training-language-models-to-follow-instructions-with-human-feedback/figure-01.png)

Figure 2: A diagram illustrating the three steps of our method: (1) supervised ﬁne-tuning (SFT), (2) reward model (RM) training, and (3) reinforcement learning via proximal policy optimization (PPO) on this reward model. Blue arrows indicate that this data is used to train one of our models. In Step 2, boxes A-D are samples from our models that get ranked by labelers. See Section 3 for more details on our method.

p. 3
