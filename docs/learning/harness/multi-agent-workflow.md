---
topic: multi-agent-workflow
last_reviewed: 2026-07-04
source_policy: official-docs-first
staleness_limit_days: 30
---

# Multi-Agent Workflow Reference

## Purpose

This file defines how PA-Explorer coordinates multiple AI harnesses without
letting any harness become the canonical owner of project rules.

## Source Of Truth

- Project entrypoint: `AGENTS.md`
- Canonical project rules: `docs/agent-rules/`
- Neutral workflows: `docs/skills/`
- Harness references: `docs/learning/harness/`

## Official Docs

| Page | URL | When to consult |
| --- | --- | --- |
| Codex subagents | `https://developers.openai.com/codex/subagents` | Codex parallel agent behavior |
| Codex best practices | `https://developers.openai.com/codex/learn/best-practices` | Codex operational patterns |
| Claude Code subagents | `https://code.claude.com/docs/en/sub-agents` | Claude Code subagent behavior |
| Claude Code common workflows | `https://code.claude.com/docs/en/common-workflows` | Claude Code workflow patterns |
| Gemini CLI extensions | `https://google-gemini.github.io/gemini-cli/docs/extensions/` | Gemini extension behavior |

## Adapter Scope

Harness adapters may define how each tool loads context, starts subagents, or
executes local validation.

## Neutral Scope

Shared branch policy, worktree policy, validation expectations, and task
routing belong in `AGENTS.md`, `docs/agent-rules/`, and `docs/skills/`.

## Warning

Do not duplicate project rules here. Multi-agent work must keep each coding
agent in a separate branch and worktree, with human review before merge.

## Last Reviewed

2026-07-04
