# Sandbox des tâches autonomes (AFK)

Ce document définit le **périmètre sûr** dans lequel un agent peut travailler
sans supervision étape par étape (AFK — Away From Keyboard), typiquement sur les
tâches classées **AFK-candidate** dans `docs/agent-workflows/backlog.md`.

Principe : le travail autonome n'est sûr que **délimité**. L'agent ne doit
pouvoir ni casser l'état du dépôt, ni exfiltrer des secrets, ni sortir de son
périmètre de fichiers. Ce qui n'est pas explicitement autorisé reste soumis à
validation humaine.

---

## Périmètre de commandes

### Autorisé sans confirmation (sûr, nécessaire à la boucle)

- **Feedback loop** : `python -m pytest` (et variantes `venv/bin/python -m pytest`).
- **Lecture Alembic** : `alembic current`, `alembic check`.
- **Lint en lecture** : `ruff check`, `ruff format --check` (une fois ruff installé).
- **Git en lecture seule** : `git status`, `git diff`, `git log`, `git show`,
  `git branch`.

### Interdit en autonomie (jamais sans humain)

- **Historique / remote destructif** : `git push`, `git reset --hard`,
  `git clean`, `git commit` sans feu vert (cf. `docs/agent-rules/git-workflow.md`).
- **Suppression récursive** : `rm -r`, `rm -rf`.
- **Schéma destructif** : `alembic downgrade`, suppression de `pa_explorer.db`
  (cf. `docs/agent-rules/alembic-schema.md`).
- **Lecture de secrets** : `.env`, `.env.*`, `secrets/**`.

---

## Périmètre de fichiers

Pour les tâches AFK actuelles (T-01, T-02 — tests uniquement) :

- **Modifiable** : `tests/**`.
- **Modifiable si la tâche l'exige** (T-03 et au-delà, en HITL) : `app/**`.
- **Hors périmètre en autonomie** : `docs/agent-rules/**` (règles canoniques),
  `alembic/versions/**` (migrations générées), `.env*`, `secrets/**`,
  `.claude/**`, `.codex/**`.

Ce périmètre fichiers est appliqué par la **revue humaine du diff** avant merge,
pas seulement par la configuration : `.claude/settings.json` est partagé par
toutes les sessions (y compris HITL) et ne doit donc pas bloquer le travail
supervisé légitime hors périmètre.

---

## Garde-fous

Avant de cocher une tâche autonome, l'agent passe les vérifications bloquantes de
`docs/skills/do_work.md` — en particulier la suite `pytest -q` au vert, sans
contournement (cf. `docs/agent-rules/no-test-workarounds.md`).

En cas de doute ou de blocage (test rouge dont la cause n'est pas triviale,
besoin de sortir du périmètre, décision de design), l'agent **s'arrête et rend
la main** plutôt que de forcer.

---

## Application par harness

- **Claude Code** : `.claude/settings.json` (`permissions.allow` / `deny`)
  encode la partie « périmètre de commandes » de cette politique. La partie
  « périmètre de fichiers » reste appliquée par revue humaine.
- Les autres harness référencent ce document comme politique neutre.

---

## Lien avec le backlog

Premières tâches candidates à une session AFK : **T-01** et **T-02** (tests des
dépendances de sécurité) — risque faible, entièrement vérifiables par pytest.
Voir `docs/agent-workflows/backlog.md`.
