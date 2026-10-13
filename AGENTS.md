# AI Frontier agent entry point

This is a project workflow for any AI assistant. Read the relevant `SKILL.md` directly if your tool does not discover repository skills. Instructions and maintenance documentation are English; public English and Chinese documents remain separate. The detailed data/command reference is [agent.md](agent.md).

## Choose the task

| Request | Skill |
| --- | --- |
| Continue a full frontier update or fill coverage gaps | [af-update](.agents/skills/af-update/SKILL.md) |
| Find new models, current flagships or discontinued releases | [af-track-models](.agents/skills/af-track-models/SKILL.md) |
| Register/download official reports or restore local sources | [af-collect-reports](.agents/skills/af-collect-reports/SKILL.md) |
| Extract original abstracts/overviews or refresh reading Markdown | [af-extract-summaries](.agents/skills/af-extract-summaries/SKILL.md) |
| Locate/export architecture, results or safety figures | [af-extract-figures](.agents/skills/af-extract-figures/SKILL.md) |
| Check metadata, links and local Pages builds | [af-validate](.agents/skills/af-validate/SKILL.md) |
| Prepare continuation notes or requested logs/commits | [af-handoff](.agents/skills/af-handoff/SKILL.md) |

Load only the skills needed for the request. A discovery task need not download reports, change the UI, or publish anything.

## Research scope

Cover language and multimodal frontier models alongside embodied AI from major labs and specialist robotics-model publishers. Embodied coverage includes robot policies/VLA, embodied reasoning/planning, and world models/simulation. Use the same discovery, collection, summary, figure, and validation skills; the embodied source/evaluation rules and official starting points are in [agent.md](agent.md#embodied-ai).

Treat robot hardware, datasets, benchmarks, simulators, and learned models as distinct objects. A hardware launch, dataset release, paper revision, or demonstration does not establish a new model release. Keep model-specific evidence and avoid ranking policies across incompatible embodiments or evaluation protocols.

## Project invariants

- `sources.json` registers verified official reports; `catalog.csv` records local source provenance; `model-coverage.json` records frontier/lifecycle decisions. Keep these roles distinct and preserve historical records. Supported publisher/task/type identifiers come from `scripts/archive_reports.py`.
- Verify release and lifecycle facts against current official sources. Latest release and strongest current model are separate decisions. Report updates are not model releases. Do not fabricate dates, sources, paper coverage or missing-publication claims.
- All original/cropped PDFs are local-only and ignored. Preserve their bytes, paths and hashes. Publish Markdown, PNG figures and official source links; never stage PDFs or create repository PDF links. A fresh clone can build Pages without PDFs; extraction needs restored exact sources.
- `abstracts/<vendor>/<slug>.md` is the single reader document: original-language passage followed by directly embedded figures and original captions. Do not create separate summary/figure entrances, duplicate galleries or public extraction diagnostics. Website cards open that document; unavailable summaries lead to official sources.
- `abstracts/index.json`, `abstracts/reviews.json`, `figures/selections.json` and `figures/index.json` retain source-bound evidence. Checkums and actual visual review matter; OCR/model output does not establish accuracy by itself.
- Change generators when changing generated documents. Maintain paired public language editions and corresponding links. Keep the existing branding/assets and directory layout unless the task requires changing them. Never hardcode current report/model counts into workflow instructions.
- Stay within user-authorized work. A request to update/build does not by itself authorize committing, pushing, deploying, changing external metadata, or rewriting history. Continue to those actions when explicitly requested; do not ask again for already-granted authorization. Never stage `log.md`, `git-log.md`, `.cache/`, `node_modules/` or internal branding prompts.
- Inspect existing work before editing. Preserve unrelated changes. Delegate only when authorized; parallel researchers return evidence, while a coordinator serializes shared data edits and generators.

## First checks

From the repository root, inspect `git status --short`, then run:

```sh
python .agents/skills/af-validate/scripts/check_project.py
```

This read-only check works without PDF/parser dependencies. For the current schemas, full command options and extraction limitations, read the relevant section of `agent.md` and the selected skill. Record durable evidence in the existing data; use ignored `.cache/handoffs/` only for temporary continuation notes.
