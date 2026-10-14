---
name: af-validate
description: "Check AI Frontier data consistency, source/image provenance, reader links, and local Pages builds. Use before handing off updates or publishing authorized changes; validation does not itself publish."
---

# Validate AI Frontier

Read [AGENTS.md](../../../AGENTS.md). Use the read-only helper to catch metadata, provenance, image, link, and Git-boundary regressions:

```sh
python .agents/skills/af-validate/scripts/check_project.py
```

Default checks do not require PDFs or ignored web captures. Web records and native assets remain checked against their registered provenance; when captures exist, their bytes and visible source text are also verified. Add `--local-pdfs` only when the complete local catalog/crop set is intended to be present; otherwise restore the scoped sources needed for extraction. A clean clone's missing ignored PDFs are not corrupt public artifacts.

Regenerate only affected documents: source/model changes require the archive renderer; figure/reading changes require abstracts `--render-only`. Do not re-extract or export unchanged sources merely to update layout.

```sh
uv run --with-requirements requirements.txt python scripts/archive_reports.py render
uv run --with-requirements requirements-abstracts.txt python scripts/extract_abstracts.py --render-only
npm ci --prefix site --ignore-scripts
uv run --with-requirements requirements-pages.txt python scripts/build_pages.py --output .cache/pages-review
python .agents/skills/af-validate/scripts/check_project.py --site .cache/pages-review
```

Run the existing regression suite when changing scripts, schemas, or rendering behavior:

```sh
uv run --with-requirements requirements-pages.txt --with-requirements requirements-abstracts.txt --with-requirements requirements-figures.txt python -m unittest discover -s tests
```

Check actual browser behavior when UI changed: report/model card opens the unified document or official source, original captions/images load, language links correspond, light/dark/system themes work, mobile layouts have no horizontal overflow, and enlargement closes/restores focus. Respect reduced motion. A successful static build is not a browser test or proof of deployment.

For a local review, start `python -m http.server 8000 --bind 127.0.0.1 --directory .cache/pages-review`; reuse an existing matching service or choose another free port without killing unrelated processes. If tools cannot start or inspect the preview, give the artifact path and exact user command, and report which visual checks remain.

Only staged-file checks plus `git diff --cached --check` count as commit validation; a working-tree check is insufficient. Publishing needs separate user authorization and actual workflow/public URL verification. Finish with [af-handoff](../af-handoff/SKILL.md).
