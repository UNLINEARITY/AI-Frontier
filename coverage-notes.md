核对日期：2026-09-30。范围为 2022 年起的模型报告、模型卡与系统卡。以下是本轮已检查的入口和仍需继续检查的范围，并非完整性声明。

| 厂商 | 本轮覆盖 | 后续补齐方向 |
| --- | --- | --- |
| OpenAI | [Deployment Safety](https://deploymentsafety.openai.com/)、历史官方系统卡及作者发布的 GPT-4、Whisper、InstructGPT、DALL-E 2、gpt-oss 报告 | 继续核对历史产品页及技术论文；Sora 原版目前登记 HTML 来源；DALL-E 3 系统卡超过单文件限制，仅保留链接 |
| Anthropic | [System Cards](https://www.anthropic.com/system-cards) 当前目录中的 PDF，以及 Claude 2、Claude 3、Claude 3.5 模型卡 | 持续检查目录新增与原链接修订；目录之外的专题报告尚未全面检查 |
| Google / DeepMind | [Model Cards](https://deepmind.google/models/model-cards) 的 PDF；Gemini、Gemma 及部分历史语言、视觉、音频模型报告 | 目录中的 HTML 卡片单独登记缺口；继续核对旧研究页面及其他模型家族 |
| Meta | OPT、Galactica、LLaMA / Llama 2 / Llama 3、Code Llama、Chameleon、Movie Gen、SeamlessM4T、MusicGen、SAM 系列作者报告 | 继续检查 [Llama 模型仓库](https://github.com/meta-llama/llama-models) 的 Llama 3.2、3.3、4 卡片，以及视觉、音频模型历史版本 |
| xAI | [Safety](https://x.ai/safety) 目录及 Grok 4.20 官方模型卡 | 补查旧 Grok 模型页面，并确认只有修订日期的卡片首次发布日期 |
| Mistral AI | Mistral 7B、Mixtral、Pixtral、Magistral、Voxtral、Ministral 3 等作者报告 | 继续检查 [官方模型文档](https://docs.mistral.ai/) 与历史发布页，尤其尚未登记的 HTML / Markdown 模型卡 |
| NVIDIA | Nemotron 4、Nemotron Nano 2、Nemotron 3 系列，以及 Cosmos 1 / 3 报告 | 继续核对 [Research](https://research.nvidia.com/) 的其他 Nemotron 与 Cosmos 版本及模态分支 |
| DeepSeek | LLM、Coder、Math、MoE、V2 / V3 / V3.2、R1、VL、Janus、Prover、OCR 系列的作者报告与 [官方仓库](https://github.com/deepseek-ai) PDF | 继续逐仓库核对版本；V3.2-Exp 与正式 V3.2 分开登记，避免以文件名推断身份 |
| Alibaba / Qwen | Qwen 主系列及 VL、Audio、Omni、TTS、ASR、Embedding、Image、Coder、Math、Guard、机器人相关报告 | 继续检查 [官方仓库](https://github.com/QwenLM) 新增报告；Qwen3.8 在本轮检查的仓库中未找到报告 PDF |
| Moonshot AI / Kimi | Kimi k1.5、K2、K2.5、K3、Audio、VL、Dev、Linear、Kimina-Prover、Moonlight 官方报告 | 继续核对 [官方仓库](https://github.com/MoonshotAI) 历史版本与缺失日期；仓库修订日期不等于报告首次发布日 |
| 智谱 / Z.ai | GLM 主系列及视觉、语音、OCR，CogVLM、CogAgent、CogView、CogVideo、CodeGeeX 作者报告 | 继续检查 [官方仓库](https://github.com/zai-org) 的新模态报告，包括 GLM-Image / ASR；确认下载失败条目的替代官方入口 |
| MiniMax | MiniMax-01、M1、M3 的官方仓库所列作者报告 | [官方仓库](https://github.com/MiniMax-AI) 的 M2、M2.1、M2.5、M2.7、H3 未找到对应独立 PDF，后续继续核对官网与作者来源 |

arXiv 条目的首次发布日期取其官方元数据中的首次提交日，修订日期与归档版本另记；这不保证是所有发布渠道中最早出现的日期。官网目录只给出 Updated 时，仅填写修订日期。PDF 以原始字节保存，解析采用宽松模式；发布者原文件的结构警告不通过重写文件来消除。

维护时先确认报告身份与官方出处，再更新 `sources.json` 并执行下载、校验。HTML / Markdown 卡片不会转换成自制 PDF。新增发现、失败重试与历史覆盖扩展都需要持续维护，此仓库目前没有自动发现新报告的任务。
