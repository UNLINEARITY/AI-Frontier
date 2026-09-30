# AI Frontier

**读懂前沿 AI，从原始报告开始。**

[英文版](README.md) · [按厂商浏览](#按厂商浏览) · [完整索引](catalog.csv)

把散落在官网、模型仓库和 arXiv 的官方技术报告、模型卡与系统卡，整理成一份随时可查的资料库。为研究者、工程师和关心 AI 技术的人，保留理解模型如何训练、评测与发布的第一手材料。

**225 份原始 PDF · 12 家厂商 · 2022 年起**

**如果这份资料库对你有用，欢迎 Star 收藏，给下一次读报告留一个入口。**

## 从这些报告开始

直接打开下面的代表性报告，或进入厂商目录浏览更多资料。

[GPT-4](pdfs/openai/gpt-4-technical-report--arxiv-v6.pdf) · [DeepSeek-V3](pdfs/deepseek/deepseek-v3-technical-report--arxiv-v2.pdf) · [DeepSeek-R1](pdfs/deepseek/deepseek-r1-incentivizing-reasoning-capability-in-llms-via-reinforcement-learning--arxiv-v2.pdf) · [Llama 3](pdfs/meta/the-llama-3-herd-of-models--arxiv-v3.pdf) · [Qwen3](pdfs/qwen/qwen3-technical-report--arxiv-v1.pdf)

## 按厂商浏览

点击厂商名称，查看归档 PDF 与官方来源。目录按已记录的首次发布日期从新到旧排列。

| 厂商 | PDF 数量 |
| --- | ---: |
| [OpenAI](pdfs/openai/README.md) | 35 |
| [Anthropic](pdfs/anthropic/README.md) | 20 |
| [Google / DeepMind](pdfs/google/README.md) | 57 |
| [Meta](pdfs/meta/README.md) | 12 |
| [xAI](pdfs/xai/README.md) | 7 |
| [Mistral AI](pdfs/mistral/README.md) | 9 |
| [NVIDIA](pdfs/nvidia/README.md) | 10 |
| [DeepSeek](pdfs/deepseek/README.md) | 20 |
| [Alibaba / Qwen](pdfs/qwen/README.md) | 26 |
| [Moonshot AI / Kimi](pdfs/moonshot/README.md) | 10 |
| [智谱 / Z.ai](pdfs/zai/README.md) | 16 |
| [MiniMax](pdfs/minimax/README.md) | 3 |

## 为什么值得收藏？

- **直接读原文。** 原始 PDF 与官方来源集中整理，减少在官网、仓库和论文页面之间来回查找。
- **横向看技术。** 对照不同厂商披露的训练方法、评测结果与安全信息，为自己的研究和判断找到依据。
- **回看演进。** 首次发布与修订日期分别记录，报告更新时保留已有归档版本，方便追溯变化。

[完整索引](catalog.csv) 提供日期、版本、来源及文件校验信息；[覆盖范围与待补清单](GAPS.md) 公开记录遗漏、未确认日期和待核对范围。

## 一起把资料库补齐

发现遗漏报告、新修订版本或失效链接？欢迎通过 Issue 或 Pull Request 提供报告标题、厂商和官方来源。一条可靠的线索，就能帮助更多人找到原始材料。

如果它帮你省下了一次搜索，欢迎 **Star**，也可以分享给正在读 AI 论文的朋友。

## 接下来，我们想做到

先把原始资料留好，再逐步让它更容易阅读和研究：

- 转为便于阅读和处理的 Markdown，保留表格、公式与图片。
- 结构化提取每份报告实际披露的技术细节。
- 建立 GitHub Pages 页面，按厂商和发布时间浏览。

以上为后续计划；当前已提供原始 PDF 与报告索引。

## 收录范围与版权

收录 2022 年起模型及模型家族的官方技术报告、模型卡与系统卡，来源包括厂商官网、官方仓库和作者提交的 arXiv 论文。资料库仍在补齐，不代表已穷尽所有历史报告。arXiv 条目以首次提交日作为已记录的首次发布日期，未知日期不作推测。

PDF 保留发布者提供的原始内容，版权及使用条款归原权利人所有，本仓库不另行授权这些报告。

维护流程与实现说明见 [agent.md](agent.md)（英文）。
