# AI Frontier

[英文版](README.md)

![AI Frontier](assets/branding/ai-frontier-banner.png)

**持续追踪前沿 AI，从原始报告走向技术洞察。**

[在线浏览](https://unlinearity.github.io/AI-Frontier/cn/) · [前沿模型](LATEST_MODELS_CN.md) · [完整索引](catalog.csv)

一个帮助研究者、工程师和 AI 技术读者理解模型如何训练、评测与部署的开放研究资料库。覆盖语言与多模态模型、机器人与 VLA、具身推理以及世界模型。我们把散落在官网、模型仓库和 arXiv 的官方技术报告、模型卡与系统卡集中整理，并逐步推进可读原文、基于来源的技术分析与模型发布追踪。

**436 份报告 · 24 家厂商 · 2022 年起**

**当前已提供：**官方报告索引、可搜索且支持站内原文阅读与图片预览的双语网站，以及[前沿报告的概要原文与核心图片](abstracts/README_CN.md)。全文 Markdown、结构化分析与自动跟进是接下来的建设阶段。

**Star 收藏 AI Frontier，把原始资料留在手边，也关注它如何逐步成为技术研究入口。**

## 按类型找报告

想看技术实现、模型使用边界，还是产品部署安全？从对应类型开始。

| 类型 | 主要对象 | 重点 | 常见内容 | 报告数量 |
| --- | --- | --- | --- | ---: |
| [Technical Report](reports/technical-reports_CN.md) | 模型/训练方法 | 技术实现与实验 | 架构、数据、训练、后训练、推理、benchmark | 313 |
| [Model Card](reports/model-cards_CN.md) | 单个模型 | 模型说明与使用边界 | 能力、限制、适用场景、不适用场景、评测、安全信息 | 62 |
| [System Card](reports/system-cards_CN.md) | 完整产品/系统 | 风险、安全、部署表现 | red teaming、危险能力评估、越狱、安全 mitigations、部署限制 | 61 |

这是常见区分，文档内容可能交叉，也可能覆盖整个模型家族；分类以官方命名与文档主要用途为准。

## 按厂商浏览

点击厂商名称，查看报告与官方来源。每家厂商下按 Technical Report、Model Card、System Card 设独立子目录，目录按已记录的首次发布日期从新到旧排列。

点击数量可进入该厂商对应类型的目录，数量仅统计已收录报告。

| 厂商 | 技术报告 | 模型卡 | 系统卡 | 报告总数 |
| --- | ---: | ---: | ---: | ---: |
| [OpenAI](pdfs/openai/README_CN.md) | [6](pdfs/openai/technical-reports/README_CN.md) | [1](pdfs/openai/model-cards/README_CN.md) | [36](pdfs/openai/system-cards/README_CN.md) | 43 |
| [Anthropic](pdfs/anthropic/README_CN.md) | [0](pdfs/anthropic/technical-reports/README_CN.md) | [5](pdfs/anthropic/model-cards/README_CN.md) | [18](pdfs/anthropic/system-cards/README_CN.md) | 23 |
| [Google / DeepMind](pdfs/google/README_CN.md) | [48](pdfs/google/technical-reports/README_CN.md) | [34](pdfs/google/model-cards/README_CN.md) | [1](pdfs/google/system-cards/README_CN.md) | 83 |
| [Meta](pdfs/meta/README_CN.md) | [29](pdfs/meta/technical-reports/README_CN.md) | [0](pdfs/meta/model-cards/README_CN.md) | [2](pdfs/meta/system-cards/README_CN.md) | 31 |
| [xAI](pdfs/xai/README_CN.md) | [0](pdfs/xai/technical-reports/README_CN.md) | [7](pdfs/xai/model-cards/README_CN.md) | [1](pdfs/xai/system-cards/README_CN.md) | 8 |
| [Mistral AI](pdfs/mistral/README_CN.md) | [11](pdfs/mistral/technical-reports/README_CN.md) | [0](pdfs/mistral/model-cards/README_CN.md) | [0](pdfs/mistral/system-cards/README_CN.md) | 11 |
| [NVIDIA](pdfs/nvidia/README_CN.md) | [27](pdfs/nvidia/technical-reports/README_CN.md) | [0](pdfs/nvidia/model-cards/README_CN.md) | [0](pdfs/nvidia/system-cards/README_CN.md) | 27 |
| [DeepSeek](pdfs/deepseek/README_CN.md) | [23](pdfs/deepseek/technical-reports/README_CN.md) | [2](pdfs/deepseek/model-cards/README_CN.md) | [0](pdfs/deepseek/system-cards/README_CN.md) | 25 |
| [Alibaba / Qwen / Wan](pdfs/qwen/README_CN.md) | [40](pdfs/qwen/technical-reports/README_CN.md) | [0](pdfs/qwen/model-cards/README_CN.md) | [0](pdfs/qwen/system-cards/README_CN.md) | 40 |
| [Moonshot AI / Kimi](pdfs/moonshot/README_CN.md) | [10](pdfs/moonshot/technical-reports/README_CN.md) | [0](pdfs/moonshot/model-cards/README_CN.md) | [0](pdfs/moonshot/system-cards/README_CN.md) | 10 |
| [智谱 / Z.ai](pdfs/zai/README_CN.md) | [18](pdfs/zai/technical-reports/README_CN.md) | [0](pdfs/zai/model-cards/README_CN.md) | [0](pdfs/zai/system-cards/README_CN.md) | 18 |
| [MiniMax](pdfs/minimax/README_CN.md) | [6](pdfs/minimax/technical-reports/README_CN.md) | [0](pdfs/minimax/model-cards/README_CN.md) | [0](pdfs/minimax/system-cards/README_CN.md) | 6 |
| [StepFun](pdfs/stepfun/README_CN.md) | [18](pdfs/stepfun/technical-reports/README_CN.md) | [0](pdfs/stepfun/model-cards/README_CN.md) | [0](pdfs/stepfun/system-cards/README_CN.md) | 18 |
| [Tencent / Hunyuan](pdfs/tencent/README_CN.md) | [20](pdfs/tencent/technical-reports/README_CN.md) | [0](pdfs/tencent/model-cards/README_CN.md) | [0](pdfs/tencent/system-cards/README_CN.md) | 20 |
| [ByteDance / Seed](pdfs/bytedance/README_CN.md) | [14](pdfs/bytedance/technical-reports/README_CN.md) | [4](pdfs/bytedance/model-cards/README_CN.md) | [0](pdfs/bytedance/system-cards/README_CN.md) | 18 |
| [Cohere](pdfs/cohere/README_CN.md) | [8](pdfs/cohere/technical-reports/README_CN.md) | [0](pdfs/cohere/model-cards/README_CN.md) | [0](pdfs/cohere/system-cards/README_CN.md) | 8 |
| [Microsoft / Phi / MAI](pdfs/microsoft/README_CN.md) | [12](pdfs/microsoft/technical-reports/README_CN.md) | [8](pdfs/microsoft/model-cards/README_CN.md) | [0](pdfs/microsoft/system-cards/README_CN.md) | 20 |
| [Amazon / Nova](pdfs/amazon/README_CN.md) | [4](pdfs/amazon/technical-reports/README_CN.md) | [0](pdfs/amazon/model-cards/README_CN.md) | [3](pdfs/amazon/system-cards/README_CN.md) | 7 |
| [Physical Intelligence](pdfs/physical_intelligence/README_CN.md) | [12](pdfs/physical_intelligence/technical-reports/README_CN.md) | [1](pdfs/physical_intelligence/model-cards/README_CN.md) | [0](pdfs/physical_intelligence/system-cards/README_CN.md) | 13 |
| [Figure AI](pdfs/figure/README_CN.md) | [0](pdfs/figure/technical-reports/README_CN.md) | [0](pdfs/figure/model-cards/README_CN.md) | [0](pdfs/figure/system-cards/README_CN.md) | 0 |
| [Skild AI](pdfs/skild/README_CN.md) | [0](pdfs/skild/technical-reports/README_CN.md) | [0](pdfs/skild/model-cards/README_CN.md) | [0](pdfs/skild/system-cards/README_CN.md) | 0 |
| [AgiBot](pdfs/agibot/README_CN.md) | [5](pdfs/agibot/technical-reports/README_CN.md) | [0](pdfs/agibot/model-cards/README_CN.md) | [0](pdfs/agibot/system-cards/README_CN.md) | 5 |
| [Galaxea AI](pdfs/galaxea/README_CN.md) | [2](pdfs/galaxea/technical-reports/README_CN.md) | [0](pdfs/galaxea/model-cards/README_CN.md) | [0](pdfs/galaxea/system-cards/README_CN.md) | 2 |
| [Generalist AI](pdfs/generalist/README_CN.md) | [0](pdfs/generalist/technical-reports/README_CN.md) | [0](pdfs/generalist/model-cards/README_CN.md) | [0](pdfs/generalist/system-cards/README_CN.md) | 0 |

## 为什么值得持续关注？

- **直接读原文。** 官方报告与来源集中整理，减少在官网、仓库和论文页面之间来回查找。
- **横向看技术。** 对照不同厂商披露的训练方法、评测结果与安全信息，为自己的研究和判断找到依据。
- **回看演进。** 首次发布与修订日期分别记录，报告更新时保留已有归档版本，方便追溯变化。

[完整索引](catalog.csv) 提供日期、版本、来源及文件校验信息；[覆盖范围与待补清单](GAPS.md) 公开记录遗漏、未确认日期和待核对范围。

## 一起把资料库补齐

发现遗漏报告、新修订版本或失效链接？欢迎通过 Issue 或 Pull Request 提供报告标题、厂商和官方来源。一条可靠的线索，就能帮助更多人找到原始材料。

如果它帮你省下了一次搜索，欢迎 **Star**，也可以分享给正在读 AI 论文的朋友。

## 从原始资料走向技术洞察

原始报告是基础。我们希望逐步建立一条研究路径，帮助读者跟进发布、核对技术证据、理解模型发生了什么变化。

| 阶段 | 帮助你做什么 | 状态 |
| --- | --- | --- |
| 原始资料 | 查找官方报告、来源链接、日期与归档版本 | 已提供 |
| 可读原文 | 阅读概要原文，查看核心图片；继续推进全文 Markdown | 概要与图片已提供 |
| 技术分析 | 结合原文出处，研究架构、数据、训练、后训练、推理与评测细节 | 计划中 |
| 持续跟进 | 通过自动监测与更新记录，追踪新模型发布及报告修订 | 计划中 |

双语网站提供报告搜索与筛选。来源和前沿模型清单由人工核对与维护。

## 收录范围与版权

收录 2022 年起模型及模型家族的官方技术报告、模型卡与系统卡，来源包括厂商官网、官方仓库和作者提交的 arXiv 论文。资料库仍在补齐，不代表已穷尽所有历史报告。arXiv 条目以首次提交日作为已记录的首次发布日期，未知日期不作推测。

原始报告请通过官方来源获取，版权及使用条款归原权利人所有，本仓库不另行授权这些报告。
