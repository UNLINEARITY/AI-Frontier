---
name: af-extract-summaries
description: "Extract and cross-check original abstract or overview passages for selected AI Frontier reports and render their unified Markdown. Use for source summaries or refreshing abstracts navigation, not generated technical analysis."
---

# Extract Source Summaries

Read [AGENTS.md](../../../AGENTS.md) for shared project boundaries.

Read the source abstract and unified reading sections of [agent.md](../../../agent.md). `abstracts/index.json` retains extraction provenance; `abstracts/<vendor>/<slug>.md` is the only reader body and directly embeds core figures.

- Confirm each selected source PDF matches the catalog SHA-256. Restore missing exact sources with [af-collect-reports](../af-collect-reports/SKILL.md). A fresh clone can build Pages without PDFs, but cannot extract source text without restoring them.
- Use the existing native-text pipeline first:
  ```sh
  uv run --with-requirements requirements-abstracts.txt python scripts/extract_abstracts.py
  ```
  This command processes the complete current active report selection, not an individual vendor. Ensure its sources are present before running; use cached extracts and existing reviews rather than redoing manual work.
- Preserve original language, actual section heading, numbers, symbols, and source wording. An Introduction, Description, Overview, or unlabelled opening is not an author-labelled Abstract. Do not manufacture a summary when no passage is identified.
- Inspect extractor disagreements and source-page layout before accepting exceptional reading order. Reviews in `abstracts/reviews.json` are tied to the exact source and raw text. A source/parser change invalidates stale review evidence; never relabel unverified text as checked.
- If native extraction fails, use an available local OCR tool or an explicitly authorized OCR service. Keep method and evidence distinct; do not claim the existing native extractor performed OCR, invent a service credential, or treat OCR output as authoritative without comparing the source page.
- For navigation/layout changes alone, preserve extraction JSON and dates:
  ```sh
  uv run --with-requirements requirements-abstracts.txt python scripts/extract_abstracts.py --render-only
  ```

Public prose contains the title, official source, original passage, embedded images and original captions. Extractor diagnostics, review states, and missing-section explanations stay in JSON. Do not create another summary/image reading entrance. Finish with [af-validate](../af-validate/SKILL.md).
