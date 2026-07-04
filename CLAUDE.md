@AGENTS.md

# Claude Code Adapter

Claude Code must treat `AGENTS.md` as the canonical project entrypoint.

Canonical project rules live in:

- `docs/agent-rules/`

Claude-specific files under `.claude/` are adapters only. Do not duplicate
business, architecture, IBM PA, Alembic, testing, or datetime rules in
`.claude/` unless the file explicitly explains why Claude needs a special
loading/scoping behavior.

Before changing Claude-specific configuration, check the official Claude Code docs:

- https://code.claude.com/docs/en/memory
- https://code.claude.com/docs/en/settings
- https://code.claude.com/docs/en/hooks
- https://code.claude.com/docs/en/skills
- https://code.claude.com/docs/en/sub-agents
- https://code.claude.com/docs/en/common-workflows

Important configuration rule:

- `.claude/settings.json` is for project settings that may be checked into source control.
- `.claude/settings.local.json` is for local machine-specific settings and must not be committed.
- If a local settings template is needed, use `.claude/settings.local.example.json`.
