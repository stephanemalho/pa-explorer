---
topic: codex
last_reviewed: 2026-07-04
source_policy: official-docs-first
staleness_limit_days: 30
---

# Codex Harness Reference

## Purpose

This file records official sources and local boundaries for using OpenAI Codex
on PA-Explorer.

## Source Of Truth

- Project entrypoint: `AGENTS.md`
- Canonical project rules: `docs/agent-rules/`
- Neutral workflows: `docs/skills/`
- Codex adapter: `.codex/config.toml`
- Codex skill wrappers: `.agents/skills/`

## Official Docs

| Page | URL | When to consult |
| --- | --- | --- |
| AGENTS.md guide | `https://developers.openai.com/codex/guides/agents-md` | Instruction discovery, precedence, and fallback filenames |
| Config basics | `https://developers.openai.com/codex/config-basic` | Config locations, precedence, common project settings |
| Advanced config | `https://developers.openai.com/codex/config-advanced` | Project `.codex/config.toml`, hooks, profiles, providers |
| Config reference | `https://developers.openai.com/codex/config-reference` | Exact supported configuration keys |
| Skills | `https://developers.openai.com/codex/skills` | Codex-compatible skill wrappers under `.agents/skills/` |
| Subagents | `https://developers.openai.com/codex/subagents` | Parallel Codex agents and custom agent files |
| Best practices | `https://developers.openai.com/codex/learn/best-practices` | Operational patterns before changing Codex workflow |

## Adapter Scope

Codex-specific files may define Codex loading behavior, config defaults,
subagent limits, hook references, and skill wrappers.

## Neutral Scope

Business, architecture, IBM PA, Alembic, testing, datetime, and validation rules
belong in `docs/agent-rules/` and `docs/skills/`.

## Warning

Do not duplicate project rules here. Check official docs before changing
Codex-specific configuration, hooks, subagents, or skills.

## Last Reviewed

2026-07-04
