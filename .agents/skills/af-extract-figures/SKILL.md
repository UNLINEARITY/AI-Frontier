---
name: af-extract-figures
description: "Locate, visually review, and export source-bound architecture, results, overview, or safety figures for AI Frontier summaries. Use for core figure extraction and crop repair, not logo creation."
---

# Extract Core Figures

Read [AGENTS.md](../../../AGENTS.md) for shared project boundaries.

Read the core figure section of [agent.md](../../../agent.md). Preserve selections in `figures/selections.json` and exported provenance in `figures/index.json`; public images are embedded directly in the corresponding abstracts Markdown.

1. Match the source SHA-256 and inspect rendered PDF pages. Native text, caption search, and drawing bounds help locate candidates; they do not replace visual source/crop review. Choose figures that explain the method or substantiate core results, and distinguish architecture from safety-evaluation charts.
2. Record actual 1-based physical page numbers and crop rectangles in top-left PDF points. Preserve full legends, axes, labels, arrows, annotations and relevant captions; do not infer boundaries from OCR alone. Copy captions from native source text where usable, including original figure numbers and symbols.
3. Update the source-bound selection record with `visual_review: true` only after actual visual review. Use `inspected_pages` and bilingual reasons for a genuine no-suitable-figure result. If review has not occurred, leave the task pending rather than claiming no figure exists. Follow the existing selection examples and exporter checks, including `caption_in_crop`/`caption_bbox` when needed.
4. Export using the existing batch tool:
   ```sh
   uv run --with-requirements requirements-figures.txt python scripts/extract_figures.py
   ```
   Official web-only records use verified native assets from `abstracts/web-sources.json`, not PDF crops. Preserve original asset URL/checksum/dimensions, actual captions versus alt text, visual review, and any explicit display-background transform. Interactive/video-only figures are not redrawn; examples are not labeled architecture/results. See the web source rules in `agent.md`.

   Selections must cover every report in `abstracts/index.json` exactly once. The command requires all selected local PDFs and recorded web snapshots/assets; stop to resolve missing sources or stale hashes rather than exporting unrelated/older figures.
5. Inspect the resulting PNGs, then regenerate unified reading Markdown:
   ```sh
   uv run --with-requirements requirements-abstracts.txt python scripts/extract_abstracts.py --render-only
   ```

Keep original PNGs at the existing 600-DPI/10,000-pixel export limits. Cropped PDFs preserve vector content locally and remain ignored. Do not redraw, enhance, or invent source figures. Higher rendering DPI does not add missing bitmap detail. Do not create an independent gallery or restore repository PDF download links. Use [af-validate](../af-validate/SKILL.md) for hashes, captions, references and local Pages checks.
