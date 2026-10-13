---
name: af-handoff
description: "Prepare a factual continuation handoff or an explicitly requested bilingual commit/log for AI Frontier changes. Use when another agent will continue, or when the user requests logs, commits, or publication."
---

# Hand Off AI Frontier Work

Read the authorization and publication boundaries in [AGENTS.md](../../../AGENTS.md). A handoff is not permission to commit, push, deploy, change repository metadata, or rewrite history.

Record a compact continuation note in `.cache/handoffs/` when useful. Include the task scope and review date; verified official URLs and decisions; changed inputs/generated layers; checks actually run; remaining gaps or source disagreements; local PDF prerequisites; preview URL/artifact path; current commit/worktree state; and any still-pending publication request. Label proposals and unfinished checks clearly. Do not copy credentials or huge extracted bodies. Ignore local caches/logs; they are not durable public facts. Important source evidence and coverage decisions belong in the existing tracked JSON/CSV notes.

When the user requests double logs and a commit:

- Write `log.md` and `git-log.md` locally, preserving prior entries, using exactly the same newest `## [YYYY-MM-DD] <title>` heading in both. The current user request authorizes these writes; do not demand a redundant confirmation.
- Record purpose, material changes and verified checks in `log.md`. Use a Conventional Commit English subject, followed by one English and one semantically matching Chinese paragraph in `git-log.md` and the actual commit. Public commit prose describes reader outcomes; keep diagnostics and machinery in the local log.
- Inspect the worktree and staged paths; stage only this task's project changes. Never stage PDFs, paired logs, caches, node_modules or branding prompts, including force-add. Run `git diff --cached --check` and report the actual commit hash.
- A commit request alone does not authorize a push. For an authorized Pages publication, push normally, monitor the correct workflow SHA, and verify actual English/Chinese URLs and image paths before claiming success. History rewriting/force pushing is a separate request, not routine update work.

In the user-facing result, lead with what readers can now access, mention checks and material gaps, and provide the usable local preview or live URL. Do not claim work performed by a tool or another agent without evidence. Leave unfinished tasks concrete enough for the next AI to resume without rediscovering the source/provenance state.
