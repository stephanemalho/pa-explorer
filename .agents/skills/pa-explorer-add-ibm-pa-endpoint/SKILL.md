---
name: pa-explorer-add-ibm-pa-endpoint
description: Use when adding a new IBM Planning Analytics endpoint or entity to PA-Explorer, such as cubes, dimensions, processes, views, or related TM1 objects.
---

# PA-Explorer IBM PA Endpoint Adapter

This Codex skill adapts the repository-neutral endpoint procedure without
copying it.

1. Read `AGENTS.md`.
2. Read `docs/skills/add_ibm_pa_endpoint.md` as the source of truth.
3. Read `docs/learning/ibm_pa.md` before choosing IBM PA URLs or fields.
4. Before writing code, inspect the current reference implementation in:
   - `app/clients/ibm_pa.py`
   - `app/services/server_service.py`
   - `app/models/server.py`
   - `app/schemas/server.py`
   - `app/routers/servers.py`
5. Apply the imported rules from `.claude/rules/`, especially:
   - `architecture-layers.md`
   - `datetime-utc.md`
   - `ibm-pa-auth.md`
   - `alembic-schema.md`
   - `no-test-workarounds.md`
6. If the endpoint introduces or changes schema, also use
   `pa-explorer-add-migration`.
7. If the endpoint needs new tests, also use `pa-explorer-test-new-service`.
8. Before reporting completion, use `pa-explorer-do-work`.
