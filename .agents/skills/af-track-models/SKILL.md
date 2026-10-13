---
name: af-track-models
description: "Verify new AI model releases, current flagships, and retired models from official sources, then update AI Frontier model coverage. Use for frontier discovery and selection, not PDF extraction."
---

# Track Frontier Models

Read [AGENTS.md](../../../AGENTS.md) for shared project boundaries.

Read the source curation and frontier selection sections of [agent.md](../../../agent.md). Supported publishers and task categories are defined in [archive_reports.py](../../../scripts/archive_reports.py); use those identifiers.

- Start with `model-coverage.json`, `sources.json`, and the requested scope. Check official release posts, model catalogs, documentation, official repositories/model cards, and author-submitted arXiv records. Community indexes can identify leads; they are not final evidence for release, capability, lifecycle, or report identity.
- Distinguish model release dates from report updates, API aliases, previews, and access tiers. Record source URLs and concise evidence in the existing model/source notes. Check whether a release remains active and available; do not revive deprecated/discontinued models because a report still exists.
- `latest_categories` selects exactly one newest active entry per publisher/task. Clear superseded active latest slots when adding a successor. `frontier_categories` separately retains current flagship tiers and important families; the newest smaller/cheaper variant does not automatically replace a stronger flagship.
- Keep historical records and their provenance. Use `lifecycle` and official `lifecycle_source_url` for deprecations. Preserve distinctions between archived reports, family reports, web-only documentation, promised publications, and unconfirmed availability.
- Resolve `report_slugs` through `sources.json`. Do not attach another model's paper or imply every checkpoint is covered by a family report. Classify documents by the publisher's designation and primary purpose, using Technical Report, Model Card, or System Card.
- Advance the global `checked_at` only after a complete review of the inventory. For a partial review, retain it and record the scoped review date/evidence in the relevant notes and handoff.

Discovery-only output is a scoped list of additions, replacements, lifecycle changes, and unresolved report searches with official links. For an authorized repository update, edit the existing inputs and hand report collection to [af-collect-reports](../af-collect-reports/SKILL.md); do not directly edit generated frontier READMEs.
