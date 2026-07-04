# Claude Code Rule Adapters

Canonical PA-Explorer project rules live in `docs/agent-rules/`.

This folder exists only for Claude Code loading and path-scoping behavior.
Files in this folder must import or reference the neutral rule files instead of
duplicating business, architecture, IBM PA, Alembic, testing, or datetime rules.

No project rule should exist only in `.claude/rules/`.
