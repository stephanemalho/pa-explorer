# Règle : Alembic gère le schéma

## Champ d'application

- `app/models/**`
- `alembic/**`

## Règle

Alembic est le seul propriétaire du schéma de base de données. `Base.metadata.create_all`
est interdit dans le code applicatif (autorisé uniquement dans `tests/fixtures/database.py`).

**Procédure obligatoire pour tout changement de schéma :**

1. Modifier le modèle SQLAlchemy dans `app/models/`
2. Si nouveau modèle : l'ajouter dans `app/models/__init__.py` (Alembic le détecte depuis là)
3. `alembic revision --autogenerate -m "description"`
4. Vérifier le fichier généré dans `alembic/versions/`
5. `alembic upgrade head`

Ne jamais supprimer `pa_explorer.db` sans réappliquer `alembic upgrade head` + `python scripts/seed_db.py`.
