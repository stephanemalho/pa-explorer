# Règle : interdiction des contournements de tests (B-8)

## Champ d'application

- `tests/**`

## Règle

Si un test échoue, la réponse correcte est **diagnostiquer et proposer une correction architecturale**.

**Interdit :**

- Attraper une exception pour avaler silencieusement une erreur (`except ... pass`)
- Ajouter `if os.getenv("TESTING")` ou équivalent dans le code applicatif
- Marquer `pytest.skip()` sans explication documentée
- Ajouter `@pytest.mark.xfail` sans justification dans `docs/learning/decisions.md`

**Procédure obligatoire si un test échoue :**

1. Formuler le diagnostic de la cause racine
2. Proposer la correction à l'utilisateur
3. Attendre validation explicite avant d'implémenter

Un contournement non validé explicitement est une violation de `docs/skills/do_work.md` B-8.
