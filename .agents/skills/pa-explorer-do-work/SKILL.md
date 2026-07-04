---
name: pa-explorer-do-work
description: Apply before completing any PA-Explorer task, especially work touching app/, tests, requirements, migrations, or repository configuration.
---

# PA-Explorer Completion Adapter

This Codex skill adapts the repository-neutral PA-Explorer workflow without
copying it.

1. Read `AGENTS.md` first.
2. Read and apply `docs/skills/do_work.md` as the source of truth for completion
   checks.
3. Read the five files under `.claude/rules/` and apply them by the paths each
   rule declares.
4. Before reporting completion, run `venv/bin/python -m pytest -q`.
5. If pytest fails, follow B-8 in `docs/skills/do_work.md`: diagnose the root
   cause and do not add skips, xfails, test-only branches, or swallowed errors
   as a workaround.
6. Report the exact verification commands and results.
