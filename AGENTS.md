# AGENTS.md — PA-Explorer

Neutral entrypoint for every AI coding agent working on PA-Explorer.

PA-Explorer is a Python/FastAPI REST API for IBM Planning Analytics SaaS. This
repository contains application code, project documentation, learning notes,
agent workflows, and thin harness-specific adapters.

Do not treat any harness folder as the owner of project rules. Canonical
project knowledge lives in `docs/`.

## Architecture And Decisions

- Architecture decisions: `docs/learning/decisions.md`
- Python/FastAPI/SQLAlchemy concepts: `docs/learning/concepts.md`
- IBM Planning Analytics reference: `docs/learning/ibm_pa.md`
- Learning journal: `docs/learning/journal-perso/`
- Harness references: `docs/learning/harness/`
- Conversational AI learning context: `docs/context/conversational-ai/PROJECT_LEARNING_CONTEXT.md`

## Canonical Rules

Canonical project rules live in:

- `docs/agent-rules/architecture-layers.md`
- `docs/agent-rules/datetime-utc.md`
- `docs/agent-rules/ibm-pa-auth.md`
- `docs/agent-rules/no-test-workarounds.md`
- `docs/agent-rules/alembic-schema.md`

Harness-specific folders such as `.claude/`, `.codex/`, `.agents/`, and
`GEMINI.md` are adapters only. They must reference the neutral rules instead of
duplicating business, architecture, IBM PA, Alembic, testing, or datetime
knowledge.

## Operational Procedures

- Project setup, reset, seed, tests, and environment variables: `README.md`
- Completion checks: `docs/skills/do_work.md`
- Add an IBM PA endpoint: `docs/skills/add_ibm_pa_endpoint.md`
- Add an Alembic migration: `docs/skills/add_migration.md`
- Test a new service: `docs/skills/test_new_service.md`
- Debug IBM PA: `docs/skills/debug_ibm_pa.md`

Codex-compatible skill wrappers live in `.agents/skills/`.

## Harness Adapters

- Codex: `.codex/config.toml` and `.agents/skills/`
- Claude Code: `CLAUDE.md` and `.claude/`
- Gemini CLI: `GEMINI.md`

## Official Documentation

### OpenAI Codex

- AGENTS.md guide: https://developers.openai.com/codex/guides/agents-md
- Codex config basics: https://developers.openai.com/codex/config-basic
- Codex advanced config and project `.codex/config.toml`: https://developers.openai.com/codex/config-advanced
- Codex config reference: https://developers.openai.com/codex/config-reference
- Codex skills: https://developers.openai.com/codex/skills
- Codex subagents: https://developers.openai.com/codex/subagents
- Codex best practices: https://developers.openai.com/codex/learn/best-practices

### Claude Code

- Claude Code memory / `CLAUDE.md`: https://code.claude.com/docs/en/memory
- Claude Code settings: https://code.claude.com/docs/en/settings
- Claude Code hooks: https://code.claude.com/docs/en/hooks
- Claude Code skills: https://code.claude.com/docs/en/skills
- Claude Code subagents: https://code.claude.com/docs/en/sub-agents
- Claude Code common workflows: https://code.claude.com/docs/en/common-workflows

### Gemini CLI

- Gemini CLI docs: https://google-gemini.github.io/gemini-cli/docs/
- `GEMINI.md` context files: https://google-gemini.github.io/gemini-cli/docs/cli/gemini-md.html
- Gemini CLI commands: https://google-gemini.github.io/gemini-cli/docs/cli/commands.html
- Gemini CLI extensions: https://google-gemini.github.io/gemini-cli/docs/extensions/

## Task Routing

| Task type | Required reading |
|---|---|
| New IBM PA endpoint | `docs/skills/add_ibm_pa_endpoint.md`, `docs/agent-rules/ibm-pa-auth.md`, `docs/learning/ibm_pa.md` |
| SQLAlchemy model or schema change | `docs/skills/add_migration.md`, `docs/agent-rules/alembic-schema.md` |
| Date/time handling | `docs/agent-rules/datetime-utc.md` |
| Test creation or test modification | `docs/skills/test_new_service.md`, `docs/agent-rules/no-test-workarounds.md` |
| IBM PA debugging | `docs/skills/debug_ibm_pa.md`, `docs/learning/ibm_pa.md` |
| Architecture/refactor work | `docs/agent-rules/architecture-layers.md`, `docs/learning/decisions.md` |
| Completion/reporting | `docs/skills/do_work.md` |

## Agent Workflow

- Operating modes and parallel-agent rules: `docs/agent-workflows/operating-modes.md`
