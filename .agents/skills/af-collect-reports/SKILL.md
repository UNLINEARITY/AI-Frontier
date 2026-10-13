---
name: af-collect-reports
description: "Register and download verified official model reports into AI Frontier local-only PDF storage, or restore source PDFs in a fresh clone. Use for report collection and source revisions."
---

# Collect Official Reports

Read [AGENTS.md](../../../AGENTS.md) for shared project boundaries.

Read the source fields, document classification, and download behavior in [agent.md](../../../agent.md). Source registration belongs in `sources.json`; file provenance belongs in `catalog.csv`. All PDFs, including cropped figure PDFs, remain ignored and local-only.

1. Verify the report title/model, publisher, document type, first publication date, revision date, and official download/source URLs. Preserve unknown dates rather than guessing. Pin explicit arXiv revisions and retain earlier catalog records when updating.
2. Register the verified source with a stable publisher/slug, then collect only the requested registered records:
   ```sh
   uv run --with-requirements requirements.txt python .agents/skills/af-collect-reports/scripts/collect_reports.py --vendor VENDOR --slug SLUG
   ```
   Repeat `--slug` for additional reports. This wrapper uses the existing downloader and catalog preservation rules; add `--refresh` only for a registered source revision check. For an authorized whole-publisher batch, the original CLI remains available:
   ```sh
   uv run --with-requirements requirements.txt python scripts/archive_reports.py fetch --vendor VENDOR
   ```
   That CLI may download every registered source for the publisher on a fresh clone; do not silently widen a single-report request.
3. Verify changed/new local files against catalog hashes and page counts. Never modify an original PDF to pass validation. A failed URL or the downloader's current size cap does not establish that no official report exists.
4. When restoring already-extracted sources after cloning, use this skill's helper from the repository root:
   ```sh
   python .agents/skills/af-collect-reports/scripts/restore_pdfs.py
   python .agents/skills/af-collect-reports/scripts/restore_pdfs.py --vendor VENDOR --slug SLUG --download
   ```
   Without `--download` it only lists missing sources. With it, the helper restores the exact catalog bytes for the existing abstracts selection, validates SHA-256, and leaves metadata unchanged. Omit filters only when restoring the complete selected set is within scope. A changed or unavailable historical PDF is a reported gap, never silently substituted.

Do not force-add PDFs, enable LFS, link local PDF paths publicly, or rewrite history. `verify` checks the entire local catalog and therefore requires all catalog PDFs; do not run it as a source-presence check on an intentionally partial clone. Restore only sources needed for the task. Current summary/figure batch commands require their full selected source set; identify that prerequisite before extracting.

Hand verified source paths and hashes to [af-extract-summaries](../af-extract-summaries/SKILL.md). Public reading targets are abstracts documents or official sources.
