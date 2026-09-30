# AI Frontier: maintenance guide

This document describes repository implementation and maintenance for agents and contributors. The root `README.md` is the English public entry point; `README_CN.md` is its separate Chinese edition. Do not mix languages within either edition. Lead with reader value, show verified collection counts, provide direct report links, and invite readers to star or contribute. Keep claims grounded in what is available. Keep setup commands, downloader behavior, and implementation details here.

## Current scope

Archive original, official AI model PDFs from 2022 onward, grouped by publisher. Accepted document types are `technical_report`, `model_card`, and `system_card`. Include reports on models or model families; do not substitute unrelated method papers, news posts, or marketing material for a missing model report.

The current stage is PDF collection and indexing. OCR, technical-detail extraction, automatic discovery, and GitHub Pages publication are future work, not implemented features.

Use ordinary Git. Do not enable Git LFS. A PDF larger than 100 MiB is recorded as `oversized` with its official link; do not compress, split, or rewrite the publisher's original file to fit the limit.

## Repository layout

| Path | Purpose |
| --- | --- |
| `sources.json` | Curated source inputs, edited after checking the report identity and official provenance |
| `catalog.csv` | Download results and historical archives, including sources, dates, versions, hashes, sizes, page counts, and gaps |
| `pdfs/<vendor>/` | Original PDFs and generated publisher directories |
| `coverage-notes.md` | Manually maintained coverage boundaries and follow-up areas, included in `GAPS.md` |
| `README.md` | Generated English public introduction, selected report links, and publisher summary |
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

`fetch` also writes the catalog and renders Markdown. `render` rewrites both root README editions, all publisher READMEs, and `GAPS.md`. Change public README wording in `render()` in `scripts/archive_reports.py`, then run `render`; editing only the generated files will be overwritten. Update both editions together and preserve their language-switch links. `agent.md` is maintained manually.

## Source curation

Supported publisher identifiers are `openai`, `anthropic`, `google`, `meta`, `xai`, `mistral`, `nvidia`, `deepseek`, `qwen`, `moonshot`, `zai`, and `minimax`.

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

Prefer publisher websites, official repositories, and author-submitted arXiv papers. Confirm the PDF title and model identity, not just its filename. Do not guess CDN paths or archive an unrelated PDF linked from a model-card page.

For arXiv records, check official metadata and use a versioned URL such as `https://arxiv.org/pdf/<id>vN` with a matching explicit version label, such as `arxiv-vN`. At initial collection, select the latest verified revision; retain previously archived revisions when updating. The first submission date is the catalog's first publication date for arXiv entries, not necessarily the earliest appearance across all channels.

Keep first publication, source revision, and retrieval time separate. A page's "Updated" date is not proof of first publication. Preserve month-only precision and leave unconfirmed dates empty. Record HTML-only cards as gaps; do not manufacture a PDF from HTML or Markdown. A failed search at one official entry point does not establish that no PDF exists elsewhere.

## Download and preservation behavior

The downloader processes up to four sources concurrently and retries failed requests. It checks the PDF header, enforces the size limit, parses page counts using `pypdf` in lenient mode, and records SHA-256. Original bytes are preserved; parsing warnings in a publisher's file do not justify rewriting it.

For pinned arXiv PDFs, fallback endpoints must show the requested arXiv ID and revision in the first two pages. The script does not automatically discover newer papers or revisions; update the curated input after checking official sources.

Files are stored as `pdfs/<vendor>/<slug>--<version>.pdf`. When the target filename already exists with different bytes, a hash suffix is added rather than overwriting the older file. Catalog maintenance retains historical archived entries. A failed refresh retains the previous archived result and records the refresh error in its notes.

Without `--refresh`, `fetch` reuses existing indexed PDFs after validating their hash and page count. Use `--refresh` when checking whether a registered URL has changed.

Catalog statuses are:

- `archived`: downloaded PDF with a local path and verification metadata.
- `missing_pdf`: no corresponding PDF URL registered after source review.
- `oversized`: PDF exceeds the ordinary Git single-file limit; official link retained.
- `failed`: download, version, or PDF inspection failed.

Unarchived entries are deliberate catalog results. A successful `fetch` process does not imply complete coverage or that every download succeeded; review catalog statuses and `GAPS.md`.

## Update workflow and validation

1. Check official source pages and repositories. Verify report identity, revision, dates, and PDF URL.
2. Update `sources.json` and, where coverage boundaries change, `coverage-notes.md`.
3. Run `fetch`, scoped by publisher when useful; use `--refresh` for changed content at an existing URL.
4. Review failures, oversized entries, unknown dates, and the titles of newly downloaded PDFs.
5. Run `verify`. It checks PDF parsing, checksums, sizes, page counts, duplicate bytes under different paths, and PDFs missing from the catalog. Empty archives fail verification. Recorded gaps alone do not make verification fail.
6. When changing downloader code, run the regression checks. When changing rendering or public documentation, run `render` and inspect generated Markdown, local links, and counts. PDF integrity verification does not check Markdown links or establish report identity.

Keep public copy accurate: do not claim exhaustive coverage, continuous automatic updates, available OCR, or a deployed Pages site before those exist. Preserve publisher copyright and terms; the repository does not relicense PDFs. Future Pages publishing should build a browsing interface from the catalog and link to the archived documents.
