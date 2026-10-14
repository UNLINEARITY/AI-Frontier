核对日期：2026-10-01（首轮：2026-09-30；本轮补查历史入口与更多厂商）。范围为 2022 年起的模型报告、模型卡与系统卡。以下是本轮已检查的入口和仍需继续检查的范围，并非完整性声明。

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
| Alibaba / Qwen / Wan | Qwen 主系列及各模态报告，并补入 Wan2.1、VACE、S2V、Animate / Animate 2、Dancer、Move 和 Tongyi DeepResearch | 继续检查 [官方仓库](https://github.com/QwenLM) 新增报告；Qwen3.8 通用家族独立报告仍未找到；Qwen3.8-Flash-Next 的独立架构报告已补收，二者不混同 |
| Moonshot AI / Kimi | Kimi k1.5、K2、K2.5、K3、Audio、VL、Dev、Linear、Kimina-Prover、Moonlight 官方报告 | 继续核对 [官方仓库](https://github.com/MoonshotAI) 历史版本与缺失日期；仓库修订日期不等于报告首次发布日 |
| 智谱 / Z.ai | GLM 主系列及视觉、语音、OCR，CogVLM、CogAgent、CogView、CogVideo、CodeGeeX 作者报告 | 继续检查 [官方仓库](https://github.com/zai-org) 的新模态报告，包括 GLM-Image / ASR；确认下载失败条目的替代官方入口 |
| MiniMax | MiniMax-01、M1、Sparse Attention，以及补查发现的 Speech、M2 系列家族报告和 VTP 模型报告 | M2、M2.5、M2.7 由一份家族报告明确覆盖，不重复保存；M2.1 独立报告与 H3 报告仍待核实，M3 入口保留所链接报告的原始题名 |
| StepFun | [官方仓库](https://github.com/stepfun-ai) 的 Step3、3.5 Flash、VL、DeepResearch，以及 Step-Audio / AQAA / 2 / 2.5 / R1 / R1.5 / EditX / 3 系列作者报告 | 继续核查 Step-3.7-Flash 的独立报告与模型卡；尚未发现单独 PDF 系统卡 |
| 腾讯 / Hunyuan | [官方仓库](https://github.com/Tencent-Hunyuan) 的 Large、A13B、MT、OCR、DiT、Image、Video、3D 模型报告 | 继续扩展历史版本、HunyuanWorld 与其他模态分支；仓库首次报告公告与后来的 arXiv 提交分开记录 |
| ByteDance / Seed | [官方模型目录](https://seed.bytedance.com/en/seed_model_portfolio) 的 Seed1.8 / 2.0 / 2.1 模型卡，以及 Thinking、VL、Diffusion、Seedream、Seedance、Seed3D 作者报告 | Seed-OSS 仓库报告入口仍标为 Coming Soon；官网 Transparency 的训练内容摘要属于监管文档，不自动归入三类模型报告 |
| Cohere | [官方研究目录](https://cohere.com/research/aya) 与 Command A、Aya / 23 / Expanse / Vision / Tiny Aya 作者报告 | 继续核查 Command A+、Reasoning、Vision 及 Embed / Rerank 的独立原始报告；模型页面或使用文档不替代 PDF |
| Microsoft / Phi / MAI | Phi-1、1.5、3、4、4-Mini、4-Reasoning、Reasoning-Vision，以及官方模型卡链接的 Mini-Flash 架构报告 | [Microsoft Research](https://www.microsoft.com/en-us/research/) 的其他模型家族尚未全面覆盖；不把 Phi-4-Mini 报告重复计为两个模态报告 |
| Amazon / Nova | [Amazon Science](https://www.amazon.science/) 的 Nova 家族、Nova Sonic、Nova 2 原始报告，以及 Nova Act 官方 AI Service Card | 技术报告与模型卡合并发布时归档一次；Premier HTML 卡片单独登记缺口；Nova Act Service Card 按完整服务的风险与部署范围归类为 System Card 并保留官方原始题名；继续核查其他系列 |

arXiv 条目的首次发布日期取其官方元数据中的首次提交日，修订日期与归档版本另记；这不保证是所有发布渠道中最早出现的日期。官网目录只给出 Updated 时，仅填写修订日期。PDF 以原始字节保存，解析采用宽松模式；发布者原文件的结构警告不通过重写文件来消除。

维护时先确认报告身份与官方出处，再更新 `sources.json` 并执行下载、校验。HTML / Markdown 卡片不会转换成自制 PDF。新增发现、失败重试与历史覆盖扩展都需要持续维护，此仓库目前没有自动发现新报告的任务。

## 本轮补查与范围边界（2026-10-01）

本轮按现有厂商分组核对当前目录、历史发布页、官方 GitHub / Hugging Face 仓库和作者提交的 arXiv 元数据，并新增此前未覆盖厂商。报告以原始题名、正式指定类型和公开来源登记，arXiv 首次提交与最新修订分别记录。该轮审计仍不构成全量覆盖声明。

Anthropic 当前系统卡目录之外发现 Claude 2.1 附录版模型卡；保留原先 14 页 Claude 2 原文并单独归档 16 页修订版。OpenAI 历史系统卡与 addendum 单独核查，DALL-E 3 技术论文和超限系统卡是不同文档。Meta 的 Llama 系列卡片以及部分 Google、Mistral、NVIDIA 卡片以 HTML / Markdown 发布，在缺口清单中登记对应来源。

Google 补查医疗、嵌入、翻译、视觉语言和机器人模型；Meta 补查 SAM / DINO / V-JEPA / Seamless / Llama Guard 等家族；NVIDIA 补查 Nemotron 分支、Cosmos-Reason、GR00T 与 Alpamayo。中国厂商补查 DeepSeek 原始 Prover 与 V4、Qwen 的图像 / GUI / ASR / Omni / 偏好模型，以及 MiniMax、Z.ai 的语音和视觉模型。Moonshot 在本轮已检查的官方仓库中未发现新的遗漏独立模型报告。

MiniMax M2、M2.5、M2.7 的旧版“未找到 PDF”记录由已验证家族报告替代；报告未明确讨论 M2.1，因此保留其独立报告缺口。家族覆盖不代表每次模型发布均有独立报告。DeepSeek-V4 的 arXiv 编号月份与官方首次提交历史不一致，按实际提交历史记录并保留异常说明。未将 Engram、MoBA、Attention Residuals 等独立方法论文自动视为新的产品模型报告。

Alibaba 的 Wan2.2 官方 Paper 入口链接 Wan2.1 家族报告，未重复归档为 Wan2.2 专属报告。Seed2.0 / 2.1 模型卡目录给出的模型发布日期未作为报告首次发布日期；尚未确认的文档日期留空。


## 最新模型逐项核查（2026-10-01）

最新模型覆盖现独立维护为 [英文页面](LATEST_MODELS.md) 与 [中文页面](LATEST_MODELS_CN.md)，按厂商列出近期主要模型与模态分支、官方入口、可读 PDF 与未解决的报告缺口。它是人工核查清单，尚非完整发布历史，也不是自动监测。

本轮从最新模型入口反查报告，补收 DeepSeek-V4.1-Flash 技术报告、DeepSeek V4 / V3.2 独立模型卡、Qwen3.8-Flash-Next 架构报告，以及 Hy-MT2、Hunyuan3D-Buffalo 1.0、WorldClaw 模型报告。DeepSeek 两份卡片封面都列出早于 Publication date 的 Updated date，保留发布者原文并在索引说明，不以模型发布日期代替报告日期。

GLM-5.3 / Flash、Step-3.7-Flash 与 MiniMax M3 / H3 / Music3 的官方网页或 Markdown 模型卡登记为 PDF 缺口。Seedance2.5、Seedream5.0Pro、SeedRealtime / SeedAudio1.0 的模型入口纳入核查，但本轮未找到对应原始 PDF；不以 Seedance2、Seedream4.5 或其他旧模型报告替代。MiniMax H3 官方发布文明确预告完整技术报告，登记为待发布，未将网页说明转换为 PDF。

已收录原文但报告日期未确认的 Gemini3.8、KimiK3、Seed2.1 等模型也从新页面直接链接。先检查报告身份和实际内容，再认定新发布版本是否被家族报告覆盖；无目录记录、未找到 PDF、厂商预告待发布是不同情况。

OpenAI 补收 GPT-5.6 的 August Updates 安全报告，与 7 月系统卡分别归档；更新日期不代表新增模型发布日期。Cohere 补收 North Small Translate 与 Command-A-Translate 技术报告，Command A+、North Mini Code / Micro Vision、Transcribe 系列及 Mistral Medium 3.5 的网页模型卡登记原始 PDF 缺口。Cohere Transcribe 的原始仓库文件需授权访问，未断言不可访问文件中没有 PDF。Embed5、Rerank4、Parse5 和 Grok 的图像、视频、语音分支已有官方模型入口，但独立报告仍待核实。

Meta 补收 Muse Spark 安全与准备度报告和 Muse Spark1.1 完整评估报告；Muse Spark1.3 / 1.2、Muse Code 及其他新模态分支仍逐项标注待核实，未把短篇评测方法附件计为核心模型报告。Microsoft 补入 MAI-Thinking-1 技术报告及 Transcribe2、Cyber1Flash、Image2.6、Voice2、Code1.1Flash 模型卡，厂商目录扩展为 Phi / MAI。NVIDIA 补收 Nemotron Labs Audex 技术报告；GR00T N1.7 的新版本独立报告不以旧 N1 报告替代。Amazon 补入 Nova2Lite 与 NovaPremier 的前沿安全报告；NovaAct 原始 AI Service Card 保持已归档。

## Embodied source and reader update (2026-10-14, scoped review)

Specialist coverage now includes Physical Intelligence, Figure, Skild, AgiBot, Galaxea and Generalist. Existing-lab coverage adds or restores the Qwen VLA/navigation/manipulation families, V-JEPA 2/2-AC and 2.1, Cosmos 3/Edge, GR-3 and specialist GR-RL, Rho/Rho-alpha, WorldPlay, SIMA 2, Genie 3 and GR00T N1.7. Navigation, manipulation and virtual-agent task labels remain distinct. This scoped update does not represent a new full-publisher lifecycle audit; the global review date is unchanged.

The π0.7, GE-Act 2.0, GE-Sim 2.0, GenieReasoner, G0.5 and Gemini Robotics 2 safety reports have now been downloaded and verified, together with the GR-3, GR-RL, Rho, WorldPlay and SIMA 2 reports. Their original-language passages and reviewed source figures are available in unified readers. π0.7 uses verified author-submitted arXiv 2604.15483v2 after the publisher PDF request failed; it is not claimed byte-identical to the inaccessible website PDF. Source first submissions, revisions and model announcements remain distinct. G0.5's cover uses the Galaxea prefix; Cosmos 3 explicitly discusses Edge, supporting the family-report link.

Helix 2.5, S1, GEN-1.5, Genie 3, GR00T N1.7 and Rho-alpha now have exact source-bound official-web passages. No standalone current-model PDF is claimed for these entries in the checked sources. Their native scientific or example images are included where captured and verified; GEN-1.5's scientific figures are interactive/video content, with no useful native static scientific image in the recorded snapshot. Video previews remain examples and image alt text is not relabeled as an author caption. Source tables supplement older figureless model/system-card readers; genuinely text-only reports retain source-bound empty figure records.

Hardware, datasets and benchmarks are not counted as model releases. V-JEPA 2.1 is a dense encoder, not an established replacement for the 2-AC action model. GR-RL is a resulting specialist policy/framework, not a verified general GR-3 successor; SIMA 2 is a virtual agent, not a physical robot policy. Vendor-internal results and incompatible robot/evaluation protocols do not establish a cross-lab ranking.

## Language and multimodal source refresh (2026-10-14)

Reviewed official current release/catalog sources across OpenAI, Anthropic, Google, Meta, xAI, Mistral, DeepSeek, Alibaba/Qwen/Wan, Moonshot, Z.ai, MiniMax, StepFun, Tencent, ByteDance, Cohere, Microsoft, Amazon and NVIDIA. This pass prioritizes current flagship/latest branches and source gaps; not every specialist entry received a new individual lifecycle audit. The global inventory `checked_at` remains unchanged; `updated_at` records the actual content-update date for reader-facing freshness.

Collected the October GPT-6 Sol/Luna system card, Claude Haiku 5.5 system card, Gemini 4 Argon model card and Safety & Security Report, and Nano Banana 2.1 model card. Their exact original PDF identities, dates, hashes and core figures are verified. October ChatGPT Sol/Luna is distinct from September API/Codex/Work versions; Astra and 6.1 Sol remain represented. Haiku's latest slot does not erase Opus, Sonnet or Fable/Mythos tiers. Argon's October 13 broad rollout updates the earlier limited-release entry. Safety-report scopes remain distinct from technical architecture reports.

Added Muse Wonder/Wonder Full, Mistral Large 4 Public Preview, EmbeddingGemma 2, and Nova 2.5 Sonic; clarified already-listed Step 5 Preview availability. Wonder's additional safety report and MiniMax H3's full technical report are still announced, not supplied by another family's paper. Mistral Large 4 weights are promised by end of October and Step 5 weights for October 15; neither promise is counted as released weights on October 14. Existing Microsoft, ByteDance and xAI branch inventories had no verified new successor in checked entry points. Cohere North 2 is a platform update; MAI Code 3-bit is a deployment/quantization format. Nemotron Ultra remains a flagship alongside the newer small Lightning family.

Captured exact official HTML overviews/model cards for important previously unreadable branches. Native source images are visually checked, original captions and alt text remain distinct, and WebP/JPEG assets retain their original checksum while decoded pixels are published losslessly as PNG. Mistral image deployment filenames were matched to the saved source HTML before export. Hy4's extremely large main image exceeded the decoder safety limit and remains excluded; its complete native benchmark appendix is retained. Text/table-only sources have original passages and official links, without invented figures.

Qwen Max's live Model Studio page is the reader source. The open Qwen3.8-2.4T-A95B card explicitly establishes Max lineage but is text-only/requires thinking, whereas the served Max has added vision/non-thinking/tools; no assumption of identical weights or exact 0902 snapshot coverage is made. Current official DeepSeek docs still list V4-Pro; community retirement claims do not establish current lifecycle. Kimi K2.8 Preview is an official coding-service rollout, and GLM FlashX a live family API endpoint, not independently verified standalone checkpoints.

## Embodied foundational-report expansion (2026-10-14)

A further scoped review adds 35 verified PDFs across Physical Intelligence, Google/DeepMind, Meta, NVIDIA, Microsoft-associated research, AgiBot, Galaxea, Tencent and ByteDance. Historical foundations include RT-1, RT-X, RT-H, RT-Trajectory, RoboCat, V-JEPA, Magma, FLOWER, Cosmos-Transfer1, the early GR policies, G0, GO-1/Colosseo and Genie Envisioner. Physical Intelligence coverage now distinguishes π0, π0.5, the π0.6 base model card, π*0.6, Hi Robot, FAST, Knowledge Insulation, MEM, inference-time/training-time RTC, RL Token and human-to-robot transfer. Nine previously archived foundational papers/cards also receive unified source readers. Historical report selection does not restore older models to the current frontier list.

AutoRT is a robot orchestration/data-collection system; SARA-RT, FAST, Knowledge Insulation and RTC are methods supporting policy development or execution, not independent base-model releases. RT-X, G0 and Colosseo combine model and dataset/platform contributions; the learned policies are distinguished from the datasets and hardware. FLOWER is primarily Intuitive Robots Lab/KIT work with a Microsoft Research coauthor and an official MSR publication listing. The human-transfer paper is PI-coauthored research with external collaborators. These affiliations do not imply exclusive vendor authorship.

Paper dates use verified source conventions, with latest arXiv revisions pinned separately. The RT-Trajectory PDF cover omits its project-name prefix; the RL Token paper title differs from its 'Precise Manipulation with Efficient Online RL' landing article. Archive titles now follow the actual downloaded PDF covers while preserving aliases, paths and hashes. The Cosmos-Transfer1 PDF cover date and arXiv v2 revision date differ; both are recorded without rewriting metadata history. Original overview text is independently extracted and its visible boundaries checked; captions are excluded from prose, and an interleaved figure does not truncate an Introduction sentence continued on the next page.

Tencent's current official repositories provide distinct Hy-Embodied-0.5-VLA, Hy-Embodied-VLM-1.0 and Hy-Embodied-RxBrain-1.0 branches. The VLA action policy remains distinct from the VLM/cognition models. VLM and RxBrain are preserved together; month-only RxBrain release evidence does not establish a latest-order tie-break against VLM-1.0. GR-Dexter is a verified separate ByteDance paper but the checked current Seed robotics portfolio lists GR-3 and GR-RL; no current flagship/weight-release claim is inferred for GR-Dexter.

Figure, Skild and Generalist historical technical pages were checked alongside their current Helix 2.5, S1 and GEN-1.5 sources. No report PDF link was found in the inspected official pages; their existing native web readers remain available. This is a scoped result, not a claim that no PDF exists anywhere. Hardware, simulation platforms, benchmark releases and article-only follow-ups are not counted as new model reports or checkpoints. Further institution/version gaps may remain; this expansion is not an exhaustive robotics bibliography.

NVIDIA DreamDojo and DreamGen were also verified and collected through official GEAR projects/repositories. DreamDojo is a mixed-collaboration learned robot world model with released code/checkpoints; DreamGen generates synthetic neural trajectories and trains downstream Diffusion Policy, π0 and GR00T N1 policies, not a new standalone policy. The DreamDojo PDF cover and displayed arXiv first-submission dates differ and are preserved separately.
