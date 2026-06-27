# CLAUDE.md — PA-Explorer

API REST Python/FastAPI pour IBM Planning Analytics SaaS. POC 
d'apprentissage Claude Code sur 8 semaines.

État actuel : Semaine 5, authentification par magic link terminée,
Alembic configuré et migrations actives, seed via script dédié.

## Architecture stricte

Pattern obligatoire : client → service → router. Injection toujours 
via Depends. Pas de logique métier dans les routers, pas d'appels 
HTTP hors des clients.

Structure des dossiers : `app/clients/` `app/services/` `app/models/` 
`app/schemas/` `app/routers/` `app/security/`.

## Quand consulter chaque document

- **Décisions architecturales et leur justification** → `docs/learning/decisions.md`
- **Concepts Python, FastAPI, SQLAlchemy** → `docs/learning/concepts.md`
- **Comportements Claude Code, commandes** → `docs/learning/claude_code_concepts.md`
- **IBM PA endpoints, auth, payloads** → `docs/learning/ibm_pa.md`
- **Ajouter un nouvel endpoint IBM PA** → `docs/skills/add_ibm_pa_endpoint.md`
- **Vision multi-version V11 V12** → `docs/roadmap/multi_version_support.md`
- **Historique des sessions** → `docs/learning/journal.md`
- **Manuel de prompts** → `docs/learning/prompts.md`
- **Procédures opérationnelles, commandes, variables d'env** → `README.md`

## Pièges critiques à connaître

- SQLite ne stocke pas les timezones, normaliser en UTC à la lecture
- Modification du schéma SQLAlchemy → `alembic revision --autogenerate -m "..."` puis `alembic upgrade head`. Ne jamais supprimer `pa_explorer.db` sans réappliquer migration et seed.
- IBM PA Basic Auth : username doit être la chaîne littérale `"apikey"`
- uvicorn lancé via `python -m uvicorn` (pas dans le PATH système)

## Mode de travail

Plan Mode pour les features architecturales. Mode direct pour les 
corrections circonscrites. Conventional commits : `type(scope): description`.

Pour ajouter un endpoint IBM PA, consulter systématiquement le skill 
- **Ajouter un nouvel endpoint IBM PA** → `docs/skills/add_ibm_pa_endpoint.md`
 avant de proposer un plan.
- Avant de signaler la complétion d'une tâche qui modifie du code applicatif, 
consulter et appliquer `docs/skills/do_work.md`.