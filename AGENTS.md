# AGENTS.md — PA-Explorer

Point d'entrée pour tout agent IA travaillant sur ce projet.

## Architecture et décisions

→ `docs/learning/decisions.md` — toutes les décisions D-001 à D-015

## Conventions obligatoires

→ `.claude/rules/` — chargé automatiquement par Claude Code
→ Pour les autres harness : lire les 5 fichiers dans `.claude/rules/` avant de toucher au code

## Procédures opérationnelles

→ `README.md` — démarrage, reset, seed, tests, variables d'environnement

## Compétences projet

→ `docs/skills/do_work.md` — vérifications obligatoires avant de signaler la complétion
→ `docs/skills/add_ibm_pa_endpoint.md` — ajouter un endpoint IBM PA
→ `docs/skills/add_migration.md` — modifier un modèle et générer la migration Alembic
→ `docs/skills/test_new_service.md` — tester un nouveau service (arbre de décision des mocks)
→ `docs/skills/debug_ibm_pa.md` — diagnostiquer un problème IBM PA

## Sources de référence

→ `docs/learning/ibm_pa.md` — IBM PA REST API, endpoints, sources officielles
→ `docs/learning/concepts.md` — stack Python/FastAPI/SQLAlchemy
→ `docs/learning/harness/` — notes et sources de référence par écosystème harness
→ `docs/context/claude-desktop/CONTEXT_FOR_CLAUDE_AI.md` — contexte pour l'assistant pédagogique
