# Compétence : ajouter une migration Alembic

Ce skill décrit la procédure pour modifier un modèle SQLAlchemy et générer
la migration Alembic correspondante. À suivre systématiquement — ne jamais
modifier le schéma sans passer par Alembic.

→ Règle complète : `.claude/rules/alembic-schema.md`

---

## Procédure

### 1. Modifier le modèle SQLAlchemy

Effectuer la modification dans `app/models/[entité].py`.

### 2. Si nouveau modèle : enregistrer dans `app/models/__init__.py`

```python
from app.models.mon_entite import MonEntite  # noqa: F401
```

Alembic détecte les modèles depuis cet import. Un modèle absent sera ignoré
par `alembic revision --autogenerate`.

### 3. Générer la migration

```bash
alembic revision --autogenerate -m "description courte de la modification"
```

### 4. Relire le fichier généré

Ouvrir `alembic/versions/{hash}_{description}.py` et vérifier :

- La migration `upgrade()` correspond bien à la modification souhaitée
- La migration `downgrade()` est cohérente (SQLite ne supporte pas `ALTER COLUMN`,
  Alembic peut générer un no-op dans ce cas — acceptable en dev)
- Aucune table existante n'est recréée par erreur

**Si la migration autogénérée est vide** : le modèle n'est pas enregistré dans
`app/models/__init__.py` ou l'import n'est pas résolu. Vérifier avant de relancer.

### 5. Appliquer la migration

```bash
alembic upgrade head
```

### 6. Vérifier l'état

```bash
alembic current
```

Doit afficher le hash de la nouvelle révision sans mention `(head missing)`.

---

## Cas : base de données existante

Alembic compare le schéma SQLAlchemy déclaré avec l'état de `alembic_version`
en base. Ne jamais supprimer `pa_explorer.db` pour contourner une migration
difficile — corriger la migration autogénérée à la place.

Si la base doit être réinitialisée (dev uniquement) :

1. Supprimer `pa_explorer.db`
2. `alembic upgrade head`
3. `python scripts/seed_db.py`

---

## Référence

- `.claude/rules/alembic-schema.md` — règle scopée sur `app/models/**` et `alembic/**`
- `README.md` — section "Réinitialiser la base"
- `docs/learning/decisions.md` — D-001 (stack), D-015 (fixtures de test)
