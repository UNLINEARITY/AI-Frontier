---
name: af-update
description: "Coordinate a scoped AI Frontier model update through discovery, local report collection, source extraction, and validation. Use for end-to-end updates or filling frontier coverage gaps."
---

# Update AI Frontier

Read [AGENTS.md](../../../AGENTS.md) first. Use existing data and tools described in [agent.md](../../../agent.md); this skill coordinates work rather than maintaining another inventory.

1. Establish the requested publisher/model/category scope and inspect the worktree. Preserve unrelated changes. Select a review window from the existing evidence dates and current date; do not assume model version numbers imply release order.
2. Use [af-track-models](../af-track-models/SKILL.md) to verify official releases, active lifecycles, latest selections, and current flagship branches. If the request covers all publishers, account for every publisher in the existing inventory, including those with no changes.
3. For changed report sources, use [af-collect-reports](../af-collect-reports/SKILL.md). Missing or web-only reports remain gaps; an older family report may be attached only when its contents actually support the selected model.
4. Use [af-extract-summaries](../af-extract-summaries/SKILL.md) and [af-extract-figures](../af-extract-figures/SKILL.md) only when the source or frontier selection changes. A discovery-only request does not require downloading or extracting documents.
5. Use [af-validate](../af-validate/SKILL.md) to regenerate affected reader documents, build locally, and check data and links. Use [af-handoff](../af-handoff/SKILL.md) to report completed work, evidence, checks, and remaining gaps.

Do not mark a run complete merely because searches finished. Verify downstream source hashes and generated reader links when those layers changed. Do not claim continuous monitoring or schedule automation merely from creating these skills.

If delegation is authorized, assign publisher-scoped research tasks. Agents return evidence and proposed records; one coordinator merges shared JSON/CSV files and runs generators serially. Do not let parallel agents overwrite the shared catalog or selection manifests.
