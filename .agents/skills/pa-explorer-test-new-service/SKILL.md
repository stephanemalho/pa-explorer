---
name: pa-explorer-test-new-service
description: Use when adding or changing PA-Explorer service, endpoint, or IBM PA client tests, especially when choosing between fakes, patching, and dependency_overrides.
---

# PA-Explorer Test Service Adapter

This Codex skill adapts the repository-neutral testing procedure without
copying it.

1. Read `AGENTS.md`.
2. Read `docs/skills/test_new_service.md` as the source of truth.
3. Read `.claude/rules/no-test-workarounds.md` before editing `tests/**`.
4. Use the documented mock decision tree:
   - explicit fake class when the dependency is constructor-injected
   - `unittest.mock.patch` when code instantiates internally
   - `dependency_overrides` for full FastAPI endpoint tests
5. Reuse fixtures from `tests/fixtures/` instead of rebuilding local setup.
6. If a test fails, follow B-8 in `docs/skills/do_work.md`: diagnose the root
   cause and do not add skips, xfails, test-only branches, or swallowed errors
   without explicit validation.
7. Before reporting completion, use `pa-explorer-do-work`.
