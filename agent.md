# AI Frontier: maintenance guide

This document describes repository implementation and maintenance for agents and contributors. The root `README.md` is the English public entry point; `README_CN.md` is its separate Chinese edition. Do not mix languages within either edition. Lead with reader value, show verified collection counts, provide complete publisher and document-type navigation, and invite readers to star or contribute. Do not feature a selective shortlist of models or publishers. Keep claims grounded in what is available. Keep setup commands, downloader behavior, and implementation details here.

Every publisher and document-type directory has an English `README.md` and a separate Chinese `README_CN.md`. Keep navigation, explanations, headings, table labels, empty-category messages, and metadata notes in the edition's language. Both editions list the same report records and preserve original report titles. Language-switch links target the sibling edition; home, publisher, category, and type-guide links stay in the current language. Cross-publisher indexes likewise have English `<type>.md` and Chinese `<type>_CN.md` editions.

## Brand and public positioning

The project name is **AI Frontier**. Its purpose is to help readers follow frontier AI from original reports to technical insight. The long-term scope covers source preservation, readable Markdown, source-grounded technical analysis, and ongoing release and revision tracking. Delivered capabilities include the original PDF archive, curated indexes, a bilingual Pages browser, source summaries, and selected core figures. Full-document conversion, technical analysis, and automated tracking remain planned.

`.github/brand.json` is the shared source for the name, English and Chinese taglines, GitHub description, and repository topics. The renderer reads the name and taglines from it. Keep the GitHub description and topics aligned with that file when updating repository metadata through `gh`.

Lead public copy with reader value and verified evidence, then offer complete publisher/type navigation and a concise invitation to star or contribute. Present the future workflow without claiming that OCR, technical analysis, real-time updates, or automated monitoring already exist. Topics describe the project's research domain and document types, rather than selecting a few publishers. Preserve the project banner in both public README editions. Generation prompts and internal image metadata stay local and ignored; third-party publisher marks are maintained separately under assets/vendors.

## Current scope

Archive original, official AI model PDFs from 2022 onward, grouped by publisher. Accepted document types are `technical_report`, `model_card`, and `system_card`. Include reports on models or model families; do not substitute unrelated method papers, news posts, or marketing material for a missing model report.

### Embodied AI

The research scope also covers embodied AI from both existing frontier labs and specialist publishers. Keep the current publisher/type directory layout and the single `abstracts/` reader layer. There is no separate robotics archive or gallery.

| Task identifier | Include | Boundary |
| --- | --- | --- |
| `robotics` | VLA, learned robot policies, manipulation, navigation, locomotion, whole-body control | A robot hardware generation is not a model version; identify the policy and embodiment separately |
| `navigation` | Learned robot navigation models and policies | Navigation stacks, maps and benchmarks are not independently model releases |
| `manipulation` | Learned grasping, dexterous and bimanual manipulation | Keep specialist policies separate from general VLA successor claims |
| `virtual_agent` | Agents acting in games and other virtual environments | Do not imply physical robot deployment from virtual evaluation |
| `embodied_reasoning` | Spatial reasoning, task planning, grounding, recovery, human–robot interaction | Require explicit embodied tasks/evidence; general VLM capability alone is insufficient |
| `world` | Learned world models, action-conditioned prediction, embodied world simulators | Video generation alone does not imply a world model; conventional simulators are not learned model releases |

Official specialist starting points (not a complete inventory):

| Publisher identifier | Official discovery sources |
| --- | --- |
| `physical_intelligence` | [Research](https://www.pi.website/), [openpi](https://github.com/Physical-Intelligence/openpi) |
| `figure` | [Research/news](https://www.figure.ai/news), [Helix](https://www.figure.ai/helix) |
| `skild` | [Research blog](https://skild.ai/blogs) |
| `agibot` | [Official repositories](https://github.com/AgibotTech), model-specific author project pages linked there |
| `galaxea` | [GalaxeaVLA](https://github.com/OpenGalaxea/GalaxeaVLA), author project pages linked there |
| `generalist` | [Research blog](https://generalistai.com/blog), model-specific technical introductions |

Also review relevant families under existing publishers, including Gemini Robotics/RT/PaLM-E, GR00T/Cosmos, Qwen robotics, and other officially documented robot/world models. These are discovery leads, not assertions of current version or completeness. Extend the publisher vocabulary only after verifying the institution's official model/report provenance. Do not require or invent a publisher logo to add coverage.

Use `af-track-models` for identity, release, flagship, access, and lifecycle checks; `af-collect-reports` for formal source PDFs; and the existing extraction/validation skills for reader documents. Official technical HTML can establish a model entry without becoming a PDF Technical Report. Keep a verified but not downloaded PDF in `sources.json`; do not fabricate an archived catalog row or source hash. A failed download does not mean no paper exists. Record scoped review evidence/date in model notes; optional `reviewed_at` records that entry's review without advancing the global inventory date. Optional `release_date` is a verified model announcement date, never inferred from a paper revision.

Datasets and benchmarks may support a model report but are not frontier model entries. Training/simulation frameworks count only when a specific learned model is documented. Preserve the difference between a research demonstration, available API, released weights, and promised code. A newer paper revision or additional benchmark result does not create a successor model.

For future source-grounded technical analysis, record the embodiment, action representation/space, sensing/proprioception, control frequency and latency hardware, training data, adaptation regime, and real-world versus simulation protocol. Keep task/trial counts, success definitions, resets/human interventions, seen/unseen environments/objects, and zero-shot versus fine-tuned conditions attached to results. Separate execution evidence from video realism; retain reported failure/contact/safety limits. Describe provider claims as reported results rather than establishing a cross-lab ranking from incompatible tasks or selected demo videos. Do not add these analysis fields to public summaries until they have actually been extracted and verified.

Selected foundational and historical reports may set `reading_models` in the source registry to receive the same unified original overview and figure reader without becoming current frontier entries. These archive readers remain in the reading index; superseded frontier readers retained only for old URLs remain historical.

The current stage includes PDF collection, indexing, native source-summary extraction, and visually selected core-figure export. Full-document OCR, technical-detail analysis, and automatic discovery remain future work. A static GitHub Pages browser is implemented; deployment status must be verified separately.

All PDFs, including original reports and cropped figure PDFs, are local-only and ignored by Git. Public Markdown and Pages link to official sources and publish derived PNG figures; never create a link to a repository PDF. Use ordinary Git. Do not enable Git LFS. A PDF larger than 100 MiB is recorded as `oversized` with its official link; do not compress, split, or rewrite the publisher's original file to fit the limit.

## Repository layout

| Path | Purpose |
| --- | --- |
| `sources.json` | Curated source inputs, edited after checking the report identity and official provenance |
| `catalog.csv` | Download results and historical archives, including sources, dates, versions, hashes, sizes, page counts, and gaps |
| `pdfs/<vendor>/` | Publisher overview with links to all three document-type directories |
| `pdfs/<vendor>/<type>/` | Original PDFs and a generated index; type is `technical-reports`, `model-cards`, or `system-cards` |
| `reports/` | Generated English and Chinese cross-publisher indexes for Technical Reports, Model Cards, and System Cards |
| `.github/brand.json` | Shared project name, public taglines, GitHub description, and discovery topics |
| `coverage-notes.md` | Manually maintained coverage boundaries and follow-up areas, included in `GAPS.md` |
| `model-coverage.json` | Manually reviewed recent model families, official evidence, report slugs, and bilingual coverage notes |
| `model-history.json` | Canonical historical model identities, source-bound report associations, explicit coverage aliases and verified release-date evidence for the timeline |
| `LATEST_MODELS.md` / `LATEST_MODELS_CN.md` | Generated reader-facing current flagships and latest important models per publisher and task category, linking archived reports and official introductions |
| `README.md` | Generated English public introduction and complete publisher table with linked counts for all three document types and total PDFs |
| `README_CN.md` | Generated Chinese public edition with corresponding content and language navigation |
| `GAPS.md` | Generated list of unarchived entries, uncertain dates, refresh failures, and coverage notes |
| `scripts/archive_reports.py` | Fetching, PDF inspection, catalog maintenance, and Markdown rendering |
| `tests/test_archive_reports.py` | Regression checks for archive preservation and failure handling |
| `requirements.txt` | Pinned PDF parsing dependency |
| `.cache/` | Ignored local discovery material and logs; not an authoritative source |

## Setup and commands

Use Python 3.10 or later. Run commands from the repository root.

```sh
python -m pip install -r requirements.txt
python scripts/archive_reports.py fetch
python scripts/archive_reports.py verify
```

Alternatively, use uv without a separate install step:

```sh
uv run --with-requirements requirements.txt python scripts/archive_reports.py fetch
uv run --with-requirements requirements.txt python scripts/archive_reports.py verify
```

Additional operations:

```sh
# Process only one publisher's registered sources.
python scripts/archive_reports.py fetch --vendor deepseek

# Re-fetch registered URLs and preserve changed snapshots.
python scripts/archive_reports.py fetch --refresh

# Regenerate Markdown from the existing catalog, without downloading PDFs.
python scripts/archive_reports.py render

# Run downloader regression checks without network requests.
python -m unittest discover -s tests
```

`fetch` also writes the catalog and renders Markdown. `render` rewrites both root README editions, both language editions of all publisher and publisher/type READMEs, both editions of the document-type indexes in `reports/`, and `GAPS.md`. Each publisher always has all three type directories, including both language editions of indexes for categories with no reports yet. Change public README wording in `render()` in `scripts/archive_reports.py`, then run `render`; editing only the generated files will be overwritten. Update both editions together and preserve their language-switch links. `agent.md` is maintained manually.

## Source curation

Supported publisher identifiers and task labels are defined in `VENDORS` and `MODEL_CATEGORIES` in `scripts/archive_reports.py`. Reuse those identifiers rather than maintaining a second vocabulary here. Specialist embodied publishers use the same schemas and three report types as existing labs.

The historical `qwen` directory identifier groups Alibaba publisher reports, including Qwen, Wan, and Tongyi model families. Keep existing paths stable when broadening publisher coverage. A family report can replace a release-specific missing entry only when its contents support that release; preserve unresolved release details as a gap rather than assuming every intermediate checkpoint is documented.

Each source record uses these fields:

| Field | Convention |
| --- | --- |
| `vendor` | One of the supported identifiers |
| `title` | Verified report title; identify any descriptive alias in notes |
| `slug` | Stable lowercase filename stem using letters, digits, and hyphens; unique within its publisher |
| `document_type` | `technical_report`, `model_card`, or `system_card` |
| `published_date` | Confirmed first publication date, `YYYY-MM-DD` or `YYYY-MM`; empty when unknown |
| `source_updated_date` | Confirmed source revision date, separate from first publication; empty when unknown |
| `source_url` | Official landing page, official repository, or author-submitted arXiv abstract page |
| `pdf_url` | Verified PDF download URL; empty if no corresponding official PDF was found |
| `version` | Optional explicit revision label; otherwise the script assigns `snapshot-YYYY-MM-DD` in UTC |
| `notes` | Evidence, date precision, identity clarifications, and limits of the source search |
| `alternate_pdf_urls` | Optional verified alternate official download endpoints |
| `metadata_url` | Optional curation reference; not exported as a catalog column |
| `reading_models` | Optional nonempty list of verified model/policy names for an explicitly selected archive reader; does not change frontier or lifecycle selections |

Prefer publisher websites, official repositories, and author-submitted arXiv papers. Confirm the PDF title and model identity, not just its filename. Do not guess CDN paths or archive an unrelated PDF linked from a model-card page.

Distinguish document types by the publisher's designation and primary purpose. A Technical Report primarily explains a model or training method through implementation details and experiments. A Model Card describes a model's capabilities, limitations, intended uses, evaluations, and safety information. A System Card primarily describes product or system risks, safety evaluations, mitigations, and deployment constraints. These categories can overlap, and cards can cover model families; do not relabel a document solely because it contains benchmarks or safety sections. Public directories display readable type labels linked to their corresponding cross-publisher indexes; machine-readable identifiers remain in the source and catalog.

For arXiv records, check official metadata and use a versioned URL such as `https://arxiv.org/pdf/<id>vN` with a matching explicit version label, such as `arxiv-vN`. At initial collection, select the latest verified revision; retain previously archived revisions when updating. The first submission date is the catalog's first publication date for arXiv entries, not necessarily the earliest appearance across all channels.

Keep first publication, source revision, and retrieval time separate. A page's "Updated" date is not proof of first publication. Preserve month-only precision and leave unconfirmed dates empty. Record HTML-only cards as gaps; do not manufacture a PDF from HTML or Markdown. A failed search at one official entry point does not establish that no PDF exists elsewhere.

## Download and preservation behavior

The downloader processes up to four sources concurrently and retries failed requests. It checks the PDF header, enforces the size limit, parses page counts using `pypdf` in lenient mode, and records SHA-256. Original bytes are preserved; parsing warnings in a publisher's file do not justify rewriting it.

For pinned arXiv PDFs, fallback endpoints must show the requested arXiv ID and revision in the first two pages. The script does not automatically discover newer papers or revisions; update the curated input after checking official sources.

Files without an explicit publisher revision are stored as `pdfs/<vendor>/<type>/<slug>.pdf`. The `document_type` input selects `technical-reports`, `model-cards`, or `system-cards`. Retrieval-date snapshot labels remain in the catalog only and do not appear in filenames or publisher tables. Explicit revisions, such as arXiv versions, use `pdfs/<vendor>/<type>/<slug>--<version>.pdf`. When the target filename already exists with different bytes, a short hash suffix is added rather than overwriting the older file. Catalog maintenance retains historical archived entries. A failed refresh retains the previous archived result and records the refresh error in its notes. When moving or renaming archived PDFs, update catalog paths and regenerate all Markdown links; preserve PDF bytes, hashes, and date metadata.

Without `--refresh`, `fetch` reuses existing indexed PDFs after validating their hash and page count. Use `--refresh` when checking whether a registered URL has changed.

Catalog statuses are:

- `archived`: downloaded PDF with a local path and verification metadata.
- `missing_pdf`: no corresponding PDF URL registered after source review.
- `oversized`: PDF exceeds the ordinary Git single-file limit; official link retained.
- `failed`: download, version, or PDF inspection failed.

Unarchived entries are deliberate catalog results. A successful `fetch` process does not imply complete coverage or that every download succeeded; review catalog statuses and `GAPS.md`.

## Update workflow and validation

Review recent releases against `model-coverage.json`, not just existing report entries. A missing report entry does not establish that a model has no report. Keep all supported publishers represented when updating the review. Each model record has `vendor`, `model`, `source_url`, `status`, `report_slugs`, `note_en`, and `note_cn`; the document has a manual `checked_at` date. Status is `archived`, `family_report`, `web_only`, `pending`, or `unconfirmed`. `pending` requires an official promise of a forthcoming report; `web_only` means a web card was found but no corresponding PDF was located in the checked sources. Never infer that no report exists from a failed search. Report slugs resolve through `sources.json`; public report links must resolve to an existing abstracts document or the official source; local PDF paths are provenance data only.

`latest_categories` selects which model appears in each publisher/category slot of `LATEST_MODELS.md` and `LATEST_MODELS_CN.md`. Categories describe model tasks, not report types, tiers, or deployment licenses. Select the newest active model using official release evidence, not version numbers or report revision dates. A model may fill multiple task categories; jointly released variants may share one family row. Keep exactly one newest selection per publisher/category, and use separate records for unrelated modalities. `frontier_categories` additionally retains current flagship tiers and important active model families in the same categories; capability leadership is not determined by release date. Curate these additions against official current model inventories and model-specific evidence, retaining only the current generation of each important family rather than restoring every historical entry. `frontier_source_url` may point to the official introduction that establishes this role. Multiple active frontier models may coexist in a category; merge task labels for a model into one public row and continue to exclude deprecated or discontinued entries from both selections. Leave older records unselected for audit history. Set `lifecycle` to `deprecated` or `discontinued` with an official `lifecycle_source_url` when applicable; these models never appear in the frontier pages even if selected. Preserve their original PDFs and archive indexes.

The frontier pages are reader-facing entry points: publisher sections, category, model name, available original documents, and an official introduction. Keep audit notes, uncertainty diagnostics, status columns, download behavior, and implementation details out of these pages. When a new model has no verified original PDF, link its official page without substituting an older model report. Update both language editions and their navigation by running `render`. This remains manual release review, not automated monitoring or an exhaustive model inventory.

1. Check official source pages and repositories. Verify report identity, revision, dates, and PDF URL.
2. Update `sources.json` and, where coverage boundaries change, `coverage-notes.md`.
3. Run `fetch`, scoped by publisher when useful; use `--refresh` for changed content at an existing URL.
4. Review failures, oversized entries, unknown dates, and the titles of newly downloaded PDFs.
5. Run `verify`. It checks PDF parsing, checksums, sizes, page counts, duplicate bytes under different paths, and PDFs missing from the catalog. Empty archives fail verification. Recorded gaps alone do not make verification fail.
6. When changing downloader code, run the regression checks. When changing rendering or public documentation, run `render` and inspect generated Markdown, local links, and counts. PDF integrity verification does not check Markdown links or establish report identity.

Keep public copy accurate: do not claim exhaustive coverage, continuous automatic updates, available OCR, or a deployed Pages site before those exist. Preserve publisher copyright and terms; the repository does not relicense PDFs. The Pages browser is generated from the catalog and links to abstracts or official sources; do not copy the PDF archive into the Pages artifact.

## GitHub Pages browser

`site/` contains the bilingual HTML template, responsive CSS, and browser filtering script. `scripts/build_pages.py` reads the catalog, curated active frontier selections, sources, and brand data to generate separate English and Chinese pages. Build with `uv run --with-requirements requirements-pages.txt python scripts/build_pages.py`; the default output `.cache/pages/` is local-only. Preview with `python -m http.server 8000 --directory .cache/pages`.

The generated site includes only pages, styles, scripts, and the existing project banner. Local PDFs are never linked or copied; official introductions and source links remain available. No PDF, paired log, internal prompt, or discovery cache is copied into the site. Search, publisher shortcuts, task/type filters, date/title sorting, and reset controls run entirely in the browser. Query parameters preserve selections across language switches and shared links. Apply a saved light/dark/system theme before stylesheet rendering; store optional preferences locally and follow system changes in system mode. Theme choice persists across language changes. Respect reduced-motion preferences for theme, entry, card, hover, and scroll animations. Animate reordered visible cards without replaying the entry animation on every search keystroke. Frontiers follow the same active lifecycle and task selection rules as the Markdown editions.

The model timeline combines canonical identities in `model-history.json` with all records in `model-coverage.json`, including retired models. Explicit `coverage_aliases` reconcile aggregate rows and variant names; a safety report update is associated with its original model, not a new release. Each node uses a verified model `release_date`, never a report date. Historical entries retain `release_source_url` and concise `release_evidence`; undated identities remain available in the model directory's unconfirmed-date filter. The horizontal SVG axis uses proportional UTC calendar dates with zoom and pan; short vertical offsets only prevent collisions and do not group publishers or encode model capability. Nodes open the same bilingual unified readers as the other model cards, falling back to official sources. `q`, `from`, and `to` query parameters preserve the shared model search and visible UTC date range across language switches; legacy `model` searches remain accepted.

The homepage is the complete publisher chooser, including ALL. Each compact colour tile is an ordinary link into `models.html` / `cn/models.html`; with scripting, other tiles exit and the selected tile carries into the explorer header through an optional shared-element transition. The model timeline lives directly above the list on those pages. Entry from a publisher tile first shows the full timeline, highlights that publisher, then fits its date extent and removes the other points. Publisher, search, category, current-frontier scope and visible date window jointly filter the timeline and rows; unknown dates, if present, appear only in full view or the unconfirmed-date scope. The list updates from the visible window without reordering every animation frame. Original reports remain separate at `reports.html` / `cn/reports.html`. All indexes still open the same abstracts documents or official sources. Legacy homepage timeline/model URLs redirect to Models, while report-filter URLs redirect to Reports. A deliberate upward gesture past the explorer top, or its ordinary All publishers link, restores the complete home chooser; reports retain their previous-home-position return. `site/motion.js` ties content progress to view position in both directions, keeps statistics factual and backgrounds visible, and respects reduced motion. Storage, scripting and native transitions are optional; no-script links still reach the full static inventory.

`.github/workflows/pages.yml` builds and deploys on relevant changes to `main` or manual dispatch. Enable **Settings → Pages → Source → GitHub Actions** before the first deployment. The workflow performs a sparse checkout of build inputs and uploads only `_site/`. A configured workflow or local build is not proof of a live deployment; check the workflow result and the public site before advertising its URL.

## Source abstracts and overviews

`abstracts/` is a source-passage layer for currently selected frontier reports. `index.json` is the structured record; report Markdown retains original-language source text and the actual section heading. Separate English and Chinese indexes share the original passages. Do not call an Overview, Description, Introduction, or unlabelled opening paragraph an author-labelled Abstract. Missing PDFs and reports without an identified summary remain explicit.

Previously extracted PDF readers remain source-bound archive readers after their model leaves the current selection. `reader_scope: historical` preserves the reader URL for report-archive cards while excluding that document from the current abstracts navigation. Re-extraction still requires its exact catalog PDF; do not discard an existing reader merely because the latest model changed.

Run `uv run --with-requirements requirements-abstracts.txt python scripts/extract_abstracts.py`. The script deduplicates family reports, selects the current archived revision, checks the PDF SHA-256, and scans up to 12 pages with pinned pdfminer.six and pypdf versions. Native extracts and layout data are cached locally by source hash, extractor versions, and page limit. It never generates summaries or calls an LLM/OCR service. Use OCR only when native extraction is unusable, and keep that method and its review status explicit. Test with `uv run --with-requirements requirements-abstracts.txt python -m unittest discover -s tests`.

`cross_checked` means selected text agrees between independent extractors under documented comparison normalization; it does not mean human verification or guaranteed section semantics. Published prose normally only normalizes whitespace and preserves source characters; `raw_text` retains original line breaks. Comparison normalization expands Unicode ligatures and accounts for line-wrap hyphens without changing published text. Section selection excludes contents pages, captions, margin stamps, and small-print footnotes. Flag unmatched text or uncertain section endings; never silently repair numbers or symbols.

The independent comparison first checks literal glyph order after Unicode/whitespace normalization, then the existing line-wrap normalization. Word-positioned PDFs may introduce a newline after a genuine hyphen; literal agreement preserves that glyph instead of treating it as an invented mismatch. Numbers, signs and published prose are unchanged.

`abstracts/reviews.json` contains source-bound visual checks for exceptional extraction order. Reviews are tied to the exact PDF checksum, extractor, page, text offsets, and raw-text checksum. Alternate text must preserve the normalized character inventory, with reading order checked against the rendered source page. A changed source or extraction invalidates the review. Preserve the initial disagreement metadata and distinguish `source_reviewed` from automatically cross-checked output. This layer is not a full-document Markdown conversion or technical analysis; the public indexes and Pages cards link to source summaries and core figures.

When a page header or figure caption interrupts a prose paragraph, or extraction omits visibly present source words, record the exact correction under `passage_repairs` in the same reviews file. Bind every edit to the PDF checksum, input/output passage checksums, unique matched text and hashed source fragments/pages. Verify the rendered source before removing non-prose material or restoring words. `apply_passage_repairs` applies these reviewed edits after native/source-order extraction; preserve original `raw_text`, `source_fragments`, source hashes and independent extractor evidence. The corrected derived `text` gets a new checksum and explicit `passage_review`/`source_review` evidence. Markdown rendering must reject stale repairs; re-extract the affected exact PDFs to verify reproducibility. This exception permits verified source restoration, not rewriting or summarizing author prose.

Official web-only model introductions use `abstracts/web-sources.json` as their curated input and the same `abstracts/index.json` reader output. Records explicitly use `source_kind: html`, a null `source_pdf`/`document_type`, the capture URL/date/HTML checksum, exact visible paragraphs with locators, and an independent source review. They are not registered as invented PDF reports. Keep snapshots and original downloaded assets under ignored `.cache/web-overviews/`; extraction verifies their exact bytes and native visible text, excluding scripts and hidden accessibility helpers. A fresh clone builds from reviewed records and published PNGs without those captures. Re-extraction requires the recorded snapshots/assets; changed live pages need a new capture and review, not silently reused provenance.

Web assets retain their official URL, original asset checksum, native dimensions, visual review, caption-versus-alt distinction, and output checksum in the existing figure manifests. Copy native PNG bytes or encode decoded JPEG pixels losslessly as PNG. For transparent white-label assets, explicit source-appropriate background compositing is allowed for legibility and must be recorded as a display transform; preserve original bytes locally. Never redraw interactive charts, invent captions, or substitute a video poster for architecture/results. Where no useful native static figure was captured, retain the limitation in JSON and leave the official page accessible.

Decode native JPEG/WebP assets to PNG without upscaling; preserve the original input bytes and record the transform. Verify relative image URLs against their source origin and pin the exact asset referenced by the saved capture, including Next image original-path references. Do not substitute another CDN size or deployment filename just because the chart looks similar. Exclude assets beyond decoder safety limits; never disable those limits to force publication.


## Core figures

`figures/selections.json` records source-bound, visually checked regions for every currently selected report. `figures/index.json` records exports, physical page numbers, top-left PDF-point coordinates, source checksums, output checksums, original captions, roles and rendering resolution. Keep architecture, benchmark results, safety evaluations and examples distinct. A missing caption is not evidence that a page lacks figures. Never substitute an older model's illustration for a model without an archived report.

Run `uv run --with-requirements requirements-figures.txt python scripts/extract_figures.py`, then rerun `scripts/extract_abstracts.py` and the archive renderer to refresh reader navigation. Source selection requires actual rendered-page inspection; native text and drawing bounds aid localization. Local OCR is an optional independent check, not an authoritative caption transcription. OCR can miss small notes or confuse mathematical symbols. Do not claim that every figure was OCR-checked unless evidence exists.

Exports copy original PDF content into a clipped page and render PNGs at up to 600 DPI (10,000 pixels maximum on either axis). They preserve native vector geometry and original bitmaps without AI redrawing or enhancement. Raster source detail is not improved by rendering at higher DPI. No SVG is generated in batch: cropped PDF is the local-only vector-preserving master. Publishers retain the original rights and terms. Original source PDFs are never modified. Repeated exports use stable PDF serialization without regenerated document IDs, avoiding binary churn in Git.

A selection checksum mismatch, changed source PDF, invalid crop bounds, unsupported role, missing visual review, caption mismatch or truncation, duplicate region, clipped native text, or incomplete report coverage stops export. Review source pages and all exported crops before publishing. Explicit no-suitable-figure records preserve coverage without inventing illustrations. Paired local logs, discovery screenshots, and OCR diagnostics remain ignored.

### Unified reading pages

`abstracts/<vendor>/<slug>.md` is the only report reading source: title, official source link, the original opening passage, and directly embedded figures with source captions. Regenerate only the public Markdown with `python scripts/extract_abstracts.py --render-only`; this preserves extraction timestamps and original source records. Render each prose paragraph on one Markdown source line, separated by blank lines; collapse source-layout soft newlines in passages, figure lead-ins and original captions without changing wording. PDF text blocks and page breaks do not establish paragraph boundaries: visually confirmed continuations belong in `abstracts/reviews.json` under `paragraph_layouts`, bound to the source and passage checksums. The zero-based `join_after` indices identify extracted paragraph separators to replace with spaces; all unreviewed separators and official HTML paragraph boundaries remain intact. Changed source bytes or passage text invalidate a layout review. Keep titles, images and page references as separate Markdown blocks, and preserve the source text and checksums in JSON. Keep review status, extractor information, missing-section diagnostics, and image-selection reasons in JSON, outside public prose. Do not create separate summary/figure reading experiences. Existing figure README paths only point readers to the corresponding abstracts document; never duplicate the body there.

`scripts/build_readers.py` renders those same Markdown files through the pinned Marked package in `site/`. Install with `npm ci --prefix site --ignore-scripts`, then build with `uv run --with-requirements requirements-pages.txt python scripts/build_pages.py`. Generated URLs are `abstracts/<vendor>/<slug>.html` and their `cn/` equivalents; old `read/` URLs redirect to these pages. English and Chinese interfaces share the original-language body. Cards link directly to the document, without a separate summary button. If a document has not been extracted, link its official report or model page without fabricating a summary.

Preserve source SHA-256 checks, figure checksums, and the original 600 DPI PNG/cropped PDF files. Create shared 1800-pixel WebP previews for the website only; original PNG downloads stay in GitHub; cropped PDFs stay local. `shared.js` handles appearance and scrolling, and `reader.js` enlarges inline images without a separate gallery. Never commit or publish a local preview before user approval when requested.

## Project skills and cross-agent continuation

Start at [AGENTS.md](AGENTS.md) for the task router and repository-wide invariants. `.agents/skills/` contains seven versionable, plain-Markdown project skills; other AI tools can read their `SKILL.md` files directly when automatic discovery is unavailable. The skills reuse the existing inputs/generators and do not implement background monitoring. Do not put their instructions in public reader navigation.

`python .agents/skills/af-validate/scripts/check_project.py` checks metadata, source bindings, PNG hashes, embedded captions, public links, and Git boundaries without requiring PDFs or parser packages. Add `--site .cache/pages-review` for generated-site checks, or `--local-pdfs` only when the complete local source/crop set should exist. The checker does not replace native PDF parsing, actual visual crop review, browser QA, or official-source research.

`uv run --with-requirements requirements.txt python .agents/skills/af-collect-reports/scripts/collect_reports.py --vendor VENDOR --slug SLUG` downloads only named registered reports with the existing catalog/history rules, then renders indexes. Use repeatable `--slug` and optional `--refresh`; the original archive CLI remains publisher-wide.

`python .agents/skills/af-collect-reports/scripts/restore_pdfs.py` lists absent PDFs needed by the existing abstracts selection. Filters `--vendor` and repeatable `--slug` narrow it; `--download` explicitly restores only the exact catalog bytes using registered URLs. It never updates source metadata or overwrites a mismatched local file. If the official historical bytes are no longer available, report that gap and review the revision explicitly. Current extraction/export CLIs process their entire selected report set, so restore those prerequisites before running a full batch.

Store temporary continuation notes in ignored `.cache/handoffs/`; durable research evidence stays in the existing source/model/catalog notes. No skill invocation independently grants permission to commit, push, publish, or rewrite history.
