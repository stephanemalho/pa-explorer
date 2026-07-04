---
name: pa-explorer-weekly-learning-journal
description: Use when creating or updating PA-Explorer weekly learning journal entries, chronology summaries, or learning documentation that must reflect actual git history and project files.
---

# PA-Explorer Weekly Learning Journal Adapter

Use this skill for chronology-sensitive learning documentation.

1. Read `AGENTS.md`.
2. Read `docs/learning/README.md` and `docs/learning/journal-perso/README.md`
   to understand the existing documentation structure.
3. Inspect the relevant existing week file under `docs/learning/journal-perso/`
   before editing or summarizing.
4. Reconstruct chronology from repository evidence first:
   - `git log --oneline --decorate --stat`
   - `git show --stat <commit>`
   - current files under `docs/learning/`
5. Preserve prior human and harness work. Do not rewrite history as if Codex
   performed work that came from another harness or from the user.
6. Distinguish observed facts, decisions, tests run, and interpretation.
7. If architecture decisions changed, update `docs/learning/decisions.md` only
   when the user explicitly asks for that decision work.
8. Before reporting completion, run the verification appropriate to the files
   changed. For code changes, use `pa-explorer-do-work`.
