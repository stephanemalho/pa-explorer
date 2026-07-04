---
topic: claude-code
last_reviewed: 2026-07-04
source_policy: official-docs-first
staleness_limit_days: 30
---

# Claude Code Harness Reference

## Purpose

This file records official sources and local boundaries for using Claude Code
on PA-Explorer.

## Source Of Truth

- Project entrypoint: `AGENTS.md`
- Canonical project rules: `docs/agent-rules/`
- Neutral workflows: `docs/skills/`
- Claude adapter: `CLAUDE.md`
- Claude-specific folder: `.claude/`

## Official Docs

| Page | URL | When to consult |
| --- | --- | --- |
| Memory and `CLAUDE.md` | `https://code.claude.com/docs/en/memory` | `CLAUDE.md`, memory, and rule loading behavior |
| Settings | `https://code.claude.com/docs/en/settings` | `.claude/settings.json` and local settings behavior |
| Hooks | `https://code.claude.com/docs/en/hooks` | Claude-specific lifecycle automation |
| Skills | `https://code.claude.com/docs/en/skills` | Claude-specific skill behavior |
| Subagents | `https://code.claude.com/docs/en/sub-agents` | Claude Code subagent setup |
| Common workflows | `https://code.claude.com/docs/en/common-workflows` | Day-to-day Claude Code operation |

## Adapter Scope

Claude-specific files may define Claude loading behavior, path-scoped adapters,
local settings templates, hooks, and subagents.

## Neutral Scope

Business, architecture, IBM PA, Alembic, testing, datetime, and validation rules
belong in `docs/agent-rules/` and `docs/skills/`.

## Warning

Do not duplicate project rules here. `.claude/rules/` preserves Claude Code
path scoping only and must reference `docs/agent-rules/`.

## Last Reviewed

2026-07-04
