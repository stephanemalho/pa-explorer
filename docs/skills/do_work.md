# Compétence : vérifications de qualité avant complétion (do_work)

Ce skill formalise les vérifications que l'agent doit effectuer
avant de signaler qu'une tâche de développement est terminée. Il
s'applique à toute modification du code applicatif.

---

## Section 1 — Quand appliquer ce skill

**Toujours appliquer** :

- À la fin de toute tâche qui modifie un ou plusieurs fichiers sous `app/`
- Après tout ajout ou modification d'une dépendance dans `requirements.txt`
- Avant tout commit git

**Ne pas appliquer** :

- Pour les tâches purement documentaires (fichiers sous `docs/`, `README.md`)
- Pour les modifications de fichiers de configuration non applicatifs
  (`.env.example`, `CLAUDE.md`, `pyproject.toml`)

---

## Section 2 — Vérifications bloquantes

Ces vérifications doivent toutes passer avant de signaler la complétion.

### B-1 : Pattern client → service → router sans fuite de couche

→ Règle complète : `.claude/rules/architecture-layers.md`

Vérifier :

- Aucun router ne contient de logique métier
- Aucun router ni service n'importe `httpx` directement
- Toute injection de dépendance utilise `Depends`

```bash
grep -r "import httpx" app/routers/ app/services/
grep -r "IBMPAClient(" app/routers/ app/services/
```

Ces commandes ne doivent retourner aucun résultat.

---

### B-2 : Normalisation UTC à la lecture SQLite

→ Règle complète : `.claude/rules/datetime-utc.md`

Avant toute comparaison avec `datetime.now(timezone.utc)`, vérifier que les champs
`expires_at`, `used_at`, `cache_expires_at`, `last_used_at` sont normalisés :

```python
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
```

---

### B-3 : Absence d'`async def` dans les couches applicatives

Stack synchrone par D-001. `async def` dans un handler, service ou client
provoque des comportements indéterminés avec SQLAlchemy synchrone.

```bash
grep -r "async def" app/routers/ app/services/ app/clients/
```

Doit retourner zéro résultat. Exception autorisée : `lifespan` dans `app/main.py`.

---

### B-4 : Cohérence modèle ↔ schéma Pydantic ↔ `_build_response`

Lors de tout ajout d'un champ sur un modèle SQLAlchemy, vérifier sa présence
dans les trois endroits :

1. Schéma Pydantic (`[Entité]Response` dans `app/schemas/`)
2. Fonction `_build_response` du router
3. Méthode `_refresh_from_ibm_pa` du service

Un champ absent d'un de ces trois endroits disparaît silencieusement sans erreur.

---

### B-5 : Authentification IBM PA — username littéral `"apikey"`

→ Règle complète : `.claude/rules/ibm-pa-auth.md`

```python
httpx.BasicAuth("apikey", api_key)  # correct
httpx.BasicAuth(user_email, api_key)  # faux — AuthorizedConnectionFailed
```

---

### B-6 : Dépendances installées

Après toute modification de `requirements.txt` :

```bash
pip install -r requirements.txt
```

---

### B-7 : Tests pytest

```bash
python -m pytest
```

Résultat attendu : zéro erreur.

---

### B-8 : Interdiction des contournements de tests

→ Règle complète : `.claude/rules/no-test-workarounds.md`

Si un test échoue pour un défaut d'architecture : diagnostiquer la racine,
formuler un diagnostic factuel, attendre validation explicite avant d'implémenter
toute modification. Un contournement appliqué sans validation est une violation de ce skill.

---

## Section 3 — Vérifications indicatives

Signaler en rapport de complétion si l'une d'elles échoue, sans bloquer.

### I-1 : Champ `raw_data` sur les modèles IBM PA

Tout modèle représentant une entité IBM PA doit avoir `raw_data: Mapped[Optional[str]]`
de type `Text`. Si absent sur un nouveau modèle, signaler.

### I-2 : Variables d'environnement dans `.env.example`

Toute variable ajoutée dans `app/config.py` doit avoir une entrée correspondante
dans `.env.example`.

### I-3 : Enregistrement dans `app/models/__init__.py`

→ Règle complète : `.claude/rules/alembic-schema.md`

Chaque nouveau modèle SQLAlchemy doit être importé dans `app/models/__init__.py`
avec `# noqa: F401`. Un modèle absent ne sera pas détecté par
`alembic revision --autogenerate`.

### I-4 : Configuration pydantic-settings avec `.env.local`

`SettingsConfigDict` dans `app/config.py` doit déclarer `env_file=(".env", ".env.local")`.

### I-5 : Smoke test de démarrage uvicorn

```bash
python -m uvicorn app.main:app
```

Attendre `Application startup complete`, puis Ctrl+C. Non bloquant car nécessite
`.env.local` valide.

---

## Section 4 — Actions mécaniques

Exécuter dans l'ordre. Ne pas passer à la suivante si la précédente échoue.

1. `pip install -r requirements.txt`
2. `python -m pytest`
3. Grep violations de couche (B-1, B-3)
4. `python -m uvicorn app.main:app` (si environnement disponible)

---

## Section 5 — Comportement en cas d'échec

### Tests pytest en échec

1. Identifier le test et son traceback
2. Localiser la cause dans le code modifié
3. Corriger avant de signaler la complétion
4. Si régression préexistante : signaler à l'utilisateur
   ("Ce test était déjà en échec avant mes modifications")

### Violation de couche détectée par grep

1. Identifier le fichier et la ligne
2. Proposer le refactoring minimal : logique métier dans un router → service ;
   appel HTTP dans un service → client IBM PA
3. Appliquer avant de signaler la complétion

### Datetime sans normalisation UTC

1. Identifier toutes les comparaisons de datetimes lus en base
2. Ajouter le pattern de normalisation à chaque point de lecture
3. Vérifier l'ensemble du service modifié (pas uniquement le cas détecté)

### Vérification indicative en échec

> Vérification indicative I-X non satisfaite : [écart]. Correction recommandée :
> [action]. Non bloquante pour la présente tâche.

---

## Références croisées

- `docs/skills/add_ibm_pa_endpoint.md` — procédure pour l'ajout d'un endpoint IBM PA
- `docs/learning/decisions.md` — décisions D-001 à D-015
- `.claude/rules/` — règles scopées chargées automatiquement
