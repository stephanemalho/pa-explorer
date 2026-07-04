---
name: pa-explorer-add-migration
description: Use when a PA-Explorer SQLAlchemy model or database schema changes and an Alembic migration must be generated, reviewed, or applied.
---

# PA-Explorer Alembic Migration Adapter

This Codex skill adapts the repository-neutral Alembic workflow without
copying it.

1. Read `AGENTS.md`.
2. Read `docs/skills/add_migration.md` as the source of truth.
3. Read `.claude/rules/alembic-schema.md` before touching `app/models/**` or
   `alembic/**`.
4. If a model is new, verify that `app/models/__init__.py` imports it with
   `# noqa: F401`.
5. Generate migrations only through Alembic autogenerate, then review the
   generated file before applying it.
6. Never use `Base.metadata.create_all` in application code.
7. Never delete `pa_explorer.db` to bypass a migration issue.
8. Before reporting completion, use `pa-explorer-do-work`.
