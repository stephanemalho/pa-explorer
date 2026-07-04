---
name: pa-explorer-debug-ibm-pa
description: Use when diagnosing IBM Planning Analytics responses, authentication failures, unexpected null fields, cache issues, raw_data mismatches, or endpoint runtime behavior.
---

# PA-Explorer IBM PA Debug Adapter

This Codex skill adapts the repository-neutral IBM PA diagnostic protocol
without copying it.

1. Read `AGENTS.md`.
2. Read `docs/skills/debug_ibm_pa.md` as the source of truth.
3. Read `docs/learning/ibm_pa.md` before making claims about IBM PA endpoint
   behavior.
4. Apply `.claude/rules/ibm-pa-auth.md`: IBM PA Basic Auth username is always
   the literal `apikey`.
5. Separate cache, mapping, and IBM PA runtime causes:
   - direct IBM PA call
   - `$metadata` inspection
   - `include_raw=true`
   - comparison between a working case and a failing case
6. For datetime-related cache failures, apply `.claude/rules/datetime-utc.md`.
7. Before reporting completion after any code change, use `pa-explorer-do-work`.
