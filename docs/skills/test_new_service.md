# Compétence : tester un nouveau service

Ce skill décrit la procédure pour écrire les tests d'un nouveau service
ou d'un endpoint HTTP. Le cœur du skill est l'arbre de décision entre les
trois techniques de mock disponibles dans ce projet.

→ Fixtures réutilisables : `tests/fixtures/`
→ Décision D-015 : rationale de l'infrastructure de test

---

## Arbre de décision : quelle technique de mock ?

### Technique 1 — Fausse classe explicite

**Quand** : le service reçoit son client **par injection via le constructeur**.

```python
# tests/fakes.py
class FakeIBMPAClient:
    def get_cubes(self, server_name: str) -> list[dict]:
        return [{"Name": "TestCube", "DisplayName": "Test Cube"}]
```

**Règle** : respecter le contrat de la méthode (valeur de retour après traitement),
pas le contrat de l'API sous-jacente. Si le vrai client fait `return data["value"]`,
le faux client retourne aussi une liste directe, pas l'enveloppe OData.

S'applique à : `ServerService`, `CubeService`, `DimensionService`.

---

### Technique 2 — `unittest.mock.patch`

**Quand** : le code instancie son client **en interne** (sans point d'injection).

```python
from unittest.mock import patch

with patch("app.services.auth_service.IBMPAClient") as mock_class:
    mock_class.return_value.validate_credentials.return_value = True
    # ...
```

**Règle** : patcher là où l'objet est **utilisé**, pas là où il est défini.

- `return_value` pour simuler un retour normal
- `side_effect` pour simuler une exception

S'applique à : `AuthService.validate_ibm_pa_credentials` (exception D-014).

---

### Technique 3 — `dependency_overrides`

**Quand** : test d'un **endpoint HTTP complet** via `TestClient`.

```python
# Réutiliser la fixture `client` de tests/fixtures/database.py
# qui override get_db avec une base SQLite in-memory isolée
def test_my_endpoint(client):
    response = client.get("/api/v1/my-endpoint")
    assert response.status_code == 200
```

Pour les endpoints combinant DB et IBM PA : combiner `dependency_overrides`
(pour la DB via la fixture `client`) et `patch` (pour le client IBM PA).

---

## Structure recommandée d'un fichier de test de service

```python
# tests/test_[entité]_service.py
import pytest
from tests.fakes import FakeIBMPAClient

class Test[Entité]Service:
    def test_cache_hit_returns_cached_data(self, db_session):
        # setup : entité en base avec cache non expiré
        # act   : appel service
        # assert : résultat correct + aucun appel IBM PA

    def test_cache_miss_calls_ibm_pa(self, db_session):
        # setup : aucune entité en base
        # act   : appel service
        # assert : IBM PA appelé, résultat persisté en base
```

---

## Référence

- `tests/fixtures/database.py` — fixture `db_session`, `client`
- `tests/fixtures/auth.py` — fixtures d'authentification et de session
- `tests/fakes.py` — fausses implémentations des clients IBM PA
- `docs/learning/decisions.md` D-015 — choix de l'infrastructure de test
