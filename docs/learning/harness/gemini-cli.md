---
topic: gemini-cli
last_reviewed: 2026-07-04
source_policy: official-docs-first
staleness_limit_days: 30
---

# Gemini CLI Harness Reference

## Purpose

This file records official sources and local boundaries for using Gemini CLI on
PA-Explorer.

## Source Of Truth

- Project entrypoint: `AGENTS.md`
- Canonical project rules: `docs/agent-rules/`
- Neutral workflows: `docs/skills/`
- Gemini adapter: `GEMINI.md`

## Official Docs

| Page | URL | When to consult |
| --- | --- | --- |
| Gemini CLI docs | `https://google-gemini.github.io/gemini-cli/docs/` | General Gemini CLI behavior |
| `GEMINI.md` context files | `https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html` | Context file behavior and project instructions |
| Commands | `https://google-gemini.github.io/gemini-cli/docs/cli/commands.html` | Gemini CLI command behavior |
| Extensions | `https://google-gemini.github.io/gemini-cli/docs/extensions/` | Gemini CLI extension behavior |

## Adapter Scope

Gemini-specific files may define Gemini context entrypoints and future
extension hints.

## Neutral Scope

Business, architecture, IBM PA, Alembic, testing, datetime, and validation rules
belong in `docs/agent-rules/` and `docs/skills/`.

## Warning

Do not duplicate project rules here. `GEMINI.md` must point back to `AGENTS.md`
and the neutral docs.

## Last Reviewed

2026-07-04
