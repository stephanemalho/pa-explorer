# CLAUDE.md — PA-Explorer

API REST Python/FastAPI pour IBM Planning Analytics SaaS. POC
d'apprentissage Claude Code sur 8 semaines.

État actuel : Semaine 5 terminée — authentification magic link, 51 tests pytest,
Alembic configuré et migrations actives, seed via script dédié.

## Quand consulter chaque document

- **Décisions architecturales et leur justification** → `docs/learning/decisions.md`
- **Concepts Python, FastAPI, SQLAlchemy** → `docs/learning/concepts.md`
- **Notes sur Claude Code, commandes** → `docs/learning/harness/anthropic-notes.md`
- **Sources écosystème Anthropic** → `docs/learning/harness/anthropic.md`
- **IBM PA endpoints, auth, payloads** → `docs/learning/ibm_pa.md`
- **Ajouter un endpoint IBM PA** → `docs/skills/add_ibm_pa_endpoint.md`
- **Ajouter une migration Alembic** → `docs/skills/add_migration.md`
- **Vision multi-version V11 V12** → `docs/roadmap/multi_version_support.md`
- **Historique des sessions** → `docs/learning/journal-perso/README.md`
- **Manuel de prompts** → `docs/learning/prompts.md`
- **Procédures opérationnelles, commandes, variables d'env** → `README.md`
- **Contexte assistant pédagogique** → `docs/context/claude-desktop/CONTEXT_FOR_CLAUDE_AI.md`

## Mode de travail

Plan Mode pour les features architecturales. Mode direct pour les corrections
circonscrites. Conventional commits : `type(scope): description`.

Pour ajouter un endpoint IBM PA → `docs/skills/add_ibm_pa_endpoint.md`.
Avant de signaler la complétion → appliquer `docs/skills/do_work.md`.

## Multi-harness

Tout agent IA entre par `AGENTS.md` à la racine.
Les conventions du projet vivent dans `.claude/rules/` et `docs/learning/decisions.md`.
