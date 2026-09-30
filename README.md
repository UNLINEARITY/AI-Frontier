# AI Frontier

**Read the reports behind frontier AI.**

[Chinese](README_CN.md) · [Browse reports](#browse-by-publisher) · [Full catalog](catalog.csv)

Official technical reports, model cards, and system cards from leading AI labs, collected in one place. A reference shelf for researchers, engineers, and anyone who wants to understand how models are built, evaluated, and released.

**225 original PDFs · 12 publishers · 2022 onward**

**Star this repo to keep the reports within reach.**

## Choose the right document

Looking for implementation details, model boundaries, or deployment safety? Start with the corresponding document type.

| Type | Main subject | Focus | Typical contents | PDFs |
| --- | --- | --- | --- | ---: |
| [Technical Report](reports/technical-reports.md) | Model / training method | Implementation and experiments | Architecture, data, training, post-training, inference, benchmarks | 135 |
| [Model Card](reports/model-cards.md) | Individual model | Model description and usage boundaries | Capabilities, limitations, intended and unsuitable uses, evaluations, safety information | 43 |
| [System Card](reports/system-cards.md) | Complete product / system | Risk, safety, and deployment behavior | Red teaming, dangerous capability evaluations, jailbreaks, safety mitigations, deployment restrictions | 47 |

These are typical distinctions, not rigid boundaries. Documents can overlap or cover a model family; classification follows the publisher's designation and the document's primary purpose.

## Browse by publisher

Pick a lab to find its archived reports and official source links. Each publisher has separate Technical Report, Model Card, and System Card folders. Each directory is ordered by recorded first publication date, newest first.

Click a count to open that publisher's collection for the document type. Counts include archived PDFs only.

| Publisher | Technical Reports | Model Cards | System Cards | Total PDFs |
| --- | ---: | ---: | ---: | ---: |
| [OpenAI](pdfs/openai/README.md) | [4](pdfs/openai/technical-reports/README.md) | [1](pdfs/openai/model-cards/README.md) | [30](pdfs/openai/system-cards/README.md) | 35 |
| [Anthropic](pdfs/anthropic/README.md) | [0](pdfs/anthropic/technical-reports/README.md) | [4](pdfs/anthropic/model-cards/README.md) | [16](pdfs/anthropic/system-cards/README.md) | 20 |
| [Google / DeepMind](pdfs/google/README.md) | [25](pdfs/google/technical-reports/README.md) | [32](pdfs/google/model-cards/README.md) | [0](pdfs/google/system-cards/README.md) | 57 |
| [Meta](pdfs/meta/README.md) | [12](pdfs/meta/technical-reports/README.md) | [0](pdfs/meta/model-cards/README.md) | [0](pdfs/meta/system-cards/README.md) | 12 |
| [xAI](pdfs/xai/README.md) | [0](pdfs/xai/technical-reports/README.md) | [6](pdfs/xai/model-cards/README.md) | [1](pdfs/xai/system-cards/README.md) | 7 |
| [Mistral AI](pdfs/mistral/README.md) | [9](pdfs/mistral/technical-reports/README.md) | [0](pdfs/mistral/model-cards/README.md) | [0](pdfs/mistral/system-cards/README.md) | 9 |
| [NVIDIA](pdfs/nvidia/README.md) | [10](pdfs/nvidia/technical-reports/README.md) | [0](pdfs/nvidia/model-cards/README.md) | [0](pdfs/nvidia/system-cards/README.md) | 10 |
| [DeepSeek](pdfs/deepseek/README.md) | [20](pdfs/deepseek/technical-reports/README.md) | [0](pdfs/deepseek/model-cards/README.md) | [0](pdfs/deepseek/system-cards/README.md) | 20 |
| [Alibaba / Qwen](pdfs/qwen/README.md) | [26](pdfs/qwen/technical-reports/README.md) | [0](pdfs/qwen/model-cards/README.md) | [0](pdfs/qwen/system-cards/README.md) | 26 |
| [Moonshot AI / Kimi](pdfs/moonshot/README.md) | [10](pdfs/moonshot/technical-reports/README.md) | [0](pdfs/moonshot/model-cards/README.md) | [0](pdfs/moonshot/system-cards/README.md) | 10 |
| [Z.ai / Zhipu AI](pdfs/zai/README.md) | [16](pdfs/zai/technical-reports/README.md) | [0](pdfs/zai/model-cards/README.md) | [0](pdfs/zai/system-cards/README.md) | 16 |
| [MiniMax](pdfs/minimax/README.md) | [3](pdfs/minimax/technical-reports/README.md) | [0](pdfs/minimax/model-cards/README.md) | [0](pdfs/minimax/system-cards/README.md) | 3 |

## Why keep this archive handy?

- **Go straight to the source.** Original publisher PDFs and official links, together in one index.
- **Compare across labs.** Find training methods, evaluation results, and safety disclosures across technical reports and model cards.
- **Trace what changed.** Publication dates and revisions are recorded separately; older archived versions are retained when reports are updated.

The [full catalog](catalog.csv) includes dates, versions, sources, and file verification details. Known omissions and uncertain dates are listed in [coverage and gaps](GAPS.md) (currently maintained in Chinese). Publisher and document-type directory READMEs are English-first bilingual; report titles and original PDFs retain their source language.

## Help build the reference shelf

Found a missing report, a newer revision, or a broken link? Open an issue or pull request with the report title, publisher, and official source. A single good source link helps make the collection more useful for everyone.

If this archive saves you a search, give it a **Star** or share it with someone reading AI papers.

## Where this is heading

The foundation is the original PDF archive. Planned next steps:

- Readable Markdown versions that preserve tables, formulas, and figures.
- Structured extraction of the technical details disclosed in each report.
- A GitHub Pages interface for browsing by publisher and publication date.

These are planned additions; the current collection provides PDFs and their index.

## Scope and attribution

This growing collection covers official model and model-family reports from 2022 onward, including technical reports, model cards, and system cards. Sources are publisher websites, official repositories, and author-submitted arXiv papers. Coverage is not yet exhaustive. For arXiv entries, the recorded first publication date is the first submission date; unknown dates are left unspecified.

PDFs are preserved as provided by their publishers. Copyrights and terms of use remain with the original rights holders; this repository does not relicense the reports.

Maintenance and implementation notes: [agent.md](agent.md).
