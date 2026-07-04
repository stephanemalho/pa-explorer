---
paths:
  - "app/models/**"
  - "app/services/**"
---

# Règle : datetimes toujours normalisés en UTC

SQLite ignore `DateTime(timezone=True)` : les datetimes lus depuis la base sont **naïfs** (sans tzinfo).

Avant toute comparaison avec `datetime.now(timezone.utc)`, normaliser :

```python
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
```

Champs concernés : `expires_at`, `used_at`, `cache_expires_at`, `last_used_at` — et tout futur
champ datetime introduit sur un nouveau modèle.
