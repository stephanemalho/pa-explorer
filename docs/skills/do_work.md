# Compétence : vérifications de qualité avant complétion (do_work)

Ce skill formalise les vérifications que Claude Code doit effectuer
avant de signaler qu'une tâche de développement est terminée. Il
s'applique à toute modification du code applicatif et ne remplace pas
les tests métier — il en est le prérequis.

---

## Section 1 — Quand appliquer ce skill

Appliquer ce skill systématiquement dans les cas suivants.

**Toujours appliquer**:

- À la fin de toute tâche qui modifie un ou plusieurs fichiers sous `app/`
- Après tout ajout ou modification d'une dépendance dans `requirements.txt`
- Avant tout commit git

**Ne pas appliquer**:

- Pour les tâches purement documentaires qui ne modifient que des
  fichiers sous `docs/` ou `README.md`
- Pour les modifications de fichiers de configuration non applicatifs
  (`.env.example`, `CLAUDE.md`, `pyproject.toml`)

---

## Section 2 — Vérifications bloquantes

Ces vérifications doivent toutes passer avant de signaler la complétion.
Si l'une d'elles échoue, la tâche n'est pas considérée comme terminée.

### B-1 : Pattern client → service → router sans fuite de couche

**Source** : CLAUDE.md ("Pattern obligatoire").

Vérifier que :

- Aucun router ne contient de logique métier (calculs, requêtes SQL,
  décisions de cache)
- Aucun router ni aucun service n'importe ou n'instancie `httpx`
  directement — tous les appels HTTP passent par `app/clients/ibm_pa.py`
- Toute injection de dépendance utilise `Depends`, jamais une
  instanciation directe dans le corps d'un handler

Commandes de vérification :

```powershell
grep -r "import httpx" app/routers/ app/services/
grep -r "IBMPAClient(" app/routers/ app/services/
```

Ces commandes ne doivent retourner aucun résultat.

---

### B-2 : Normalisation UTC à la lecture SQLite

**Source** : CLAUDE.md ("piège critique"), semaine 2 (bug HTTP 500),
semaine 4 (validation d'expiration des sessions).

SQLite ne stocke pas les informations de timezone malgré la déclaration
`DateTime(timezone=True)` dans SQLAlchemy. Toute comparaison d'un
`datetime` lu en base avec `datetime.now(timezone.utc)` sans normalisation
lève une `TypeError`.

Vérifier que chaque lecture d'un champ datetime en base est suivie du
pattern de normalisation :

```python
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
```

S'applique à tout champ `cache_expires_at`, `expires_at`, `last_used_at`,
`used_at`, et tout autre champ datetime introduit dans un nouveau modèle.

---

### B-3 : Absence d'`async def` dans les couches applicatives

**Source** : D-001 ("SQLAlchemy synchrone, FastAPI synchrone").

La stack est synchrone par décision architecturale définitive. Un
`async def` dans un handler, un service ou un client provoque des
comportements indéterminés avec SQLAlchemy synchrone.

Commande de vérification :

```powershell
grep -r "async def" app/routers/ app/services/ app/clients/
```

Cette commande ne doit retourner aucun résultat. La seule exception
autorisée est la fonction `lifespan` dans `app/main.py`, imposée par
FastAPI.

---

### B-4 : Cohérence modèle ↔ schéma Pydantic ↔ `_build_response`

**Source** : semaine 2 (champs `accepting_clients`, `href`, `is_v12`
présents en base mais absents de la réponse API),
`docs/skills/add_ibm_pa_endpoint.md` ("Double omission").

Lors de tout ajout d'un champ typé sur un modèle SQLAlchemy, vérifier
que ce champ apparaît dans les trois endroits suivants :

1. Le schéma Pydantic correspondant (`[Entité]Response` dans
   `app/schemas/`)
2. La fonction `_build_response` du router
3. La méthode `_refresh_from_ibm_pa` ou équivalente du service

Un champ absent de l'un de ces trois endroits ne génère aucune erreur
à l'exécution. Les données transitent jusqu'en base et s'arrêtent là
silencieusement.

---

### B-5 : Authentification IBM PA — username littéral "apikey"

**Source** : D-004, CLAUDE.md ("piège critique").

Vérifier que toute instanciation de `IBMPAClient` qui effectue du
Basic Auth utilise la chaîne littérale `"apikey"` comme username et
non l'email de l'utilisateur.

```python
httpx.BasicAuth("apikey", api_key)  # correct
httpx.BasicAuth(user_email, api_key)  # faux — AuthorizedConnectionFailed
```

---

### B-6 : Dépendances installées (A-1)

**Source** : semaine 4 (`ModuleNotFoundError: email-validator` après
ajout dans `requirements.txt` sans relancer `pip install`).

Après toute modification de `requirements.txt`, exécuter :

```powershell
pip install -r requirements.txt
```

Résultat attendu : pas d'erreur, confirmation que toutes les dépendances
sont satisfaites.

---

### B-7 : Tests pytest (A-3)

```powershell
python -m pytest
```

Résultat attendu : zéro test en erreur.

**Note** : en semaine 4, aucun test fonctionnel n'existe encore. Cette
vérification retourne "no tests ran" ou "0 passed" sans valeur de signal.
Elle deviendra effective dès la semaine 5 quand les premiers tests
métier seront écrits. Lancer la commande malgré tout pour s'assurer
qu'il n'y a pas d'erreur de collecte (import error, syntax error).

---

## Section 3 — Vérifications indicatives

Ces vérifications sont recommandées mais ne bloquent pas la complétion.
Si l'une d'elles échoue ou est absente, le signaler explicitement dans
le rapport de complétion, sans interrompre la livraison.

### I-1 : Champ `raw_data` sur les modèles métier

**Source** : D-008 ("schema-on-read").

Tout modèle SQLAlchemy représentant une entité IBM PA doit avoir un
champ `raw_data: Mapped[Optional[str]]` de type `Text` qui stocke le
JSON brut de la réponse IBM PA. Si ce champ est absent d'un nouveau
modèle, le signaler.

---

### I-2 : Variables d'environnement dans `.env.example`

**Source** : convention observée (semaines 1 et 4).

Toute variable ajoutée dans `app/config.py` doit avoir une entrée
correspondante dans `.env.example`, même avec une valeur vide ou un
placeholder commenté. Vérifier que le fichier est à jour après chaque
extension de `Settings`.

---

### I-3 : Imports de modèles dans `main.py`

**Source** : architecture observée (semaines 3 et 4).

Chaque nouveau modèle SQLAlchemy doit être importé dans `app/main.py`
avec un commentaire `# noqa: F401` pour que `Base.metadata.create_all`
crée la table au démarrage. Un modèle non importé ne génère aucune
erreur — sa table n'est simplement pas créée.

```python
from app.models import mon_entite  # noqa: F401 — enregistre MonEntite dans la metadata SQLAlchemy
```

---

### I-4 : Configuration `pydantic-settings` avec `.env.local`

**Source** : semaine 1 (credentials dans `.env.local` non chargées).

Vérifier que `SettingsConfigDict` dans `app/config.py` déclare bien
les deux fichiers :

```python
model_config = SettingsConfigDict(
    env_file=(".env", ".env.local"),
    ...
)
```

---

### I-5 : Smoke test de démarrage uvicorn (A-2)

```powershell
python -m uvicorn app.main:app
```

Lancer, attendre la ligne "Application startup complete", puis Ctrl+C.
Détecte les erreurs d'import, les variables d'environnement manquantes,
et les échecs d'initialisation du lifespan.

Ce test est recommandé après tout ajout de modèle, de router, ou de
dépendance. Il n'est pas bloquant parce qu'il nécessite un environnement
avec `.env.local` valide, qui peut ne pas être disponible dans tous
les contextes d'exécution.

---

### I-6 : Vérifications architecturales par grep (A-7)

Exécuter les commandes suivantes et signaler tout résultat inattendu.

```powershell
# Détecter async dans les couches applicatives (doit être vide)
grep -r "async def" app/routers/ app/services/ app/clients/

# Détecter httpx hors du client (doit être vide)
grep -r "import httpx" app/routers/ app/services/

# Détecter IBMPAClient instancié hors dépendance (doit être vide)
grep -r "IBMPAClient(" app/routers/ app/services/
```

Ces vérifications recoupent B-1 et B-3 mais sont utiles comme audit
rapide sur une base de code qui a grossi.

---

## Section 4 — Actions mécaniques à exécuter dans l'ordre

Exécuter ces commandes dans l'ordre indiqué. Ne pas passer à la
suivante si la précédente retourne une erreur.

### Étape 1 : Installer les dépendances

```powershell
pip install -r requirements.txt
```

Objectif : s'assurer que le venv est cohérent avec `requirements.txt`.
Résultat attendu : aucune erreur, message de confirmation pip.

---

### Étape 2 : Lancer les tests

```powershell
python -m pytest
```

Objectif : détecter toute régression sur les tests existants.
Résultat attendu : `X passed` sans erreur. En semaine 4, `no tests ran`
est acceptable.

---

### Étape 3 : Vérifications architecturales grep

```powershell
grep -r "async def" app/routers/ app/services/ app/clients/
grep -r "import httpx" app/routers/ app/services/
grep -r "IBMPAClient(" app/routers/ app/services/
```

Objectif : détecter les violations de couche.
Résultat attendu : aucune ligne retournée pour chaque commande.

---

### Étape 4 : Smoke test uvicorn (si environnement disponible)

```powershell
python -m uvicorn app.main:app
```

Objectif : valider le démarrage complet de l'application.
Résultat attendu : `Application startup complete` sans traceback.

---

### Actions préparées, disponibles à partir de la semaine 5

Les commandes suivantes seront ajoutées à cette procédure une fois
les outils installés et configurés.

**Formatage automatique — black ou ruff format :**:

```powershell
# À partir de la semaine 5, après pip install ruff
ruff format app/
```

**Linting — ruff check :**

```powershell
# À partir de la semaine 5, après pip install ruff
ruff check app/
```

**Type checking — mypy :**

```powershell
# À partir de la semaine 5 ou 6, après pip install mypy
python -m mypy app/
```

Ces trois outils seront ajoutés dans `requirements.txt` section dev
et intégrés dans des pre-commit hooks en semaine 5 ou 6.

---

## Section 5 — Comportement attendu en cas d'échec

### Règle principale

Si une vérification **bloquante** (Section 2) échoue, ne pas signaler
la complétion de la tâche. Expliquer ce qui a échoué de manière factuelle,
proposer une correction concrète.

---

### Si les tests pytest échouent

1. Identifier le test en échec et son traceback.
2. Localiser la cause dans le code modifié pendant la tâche.
3. Corriger la cause avant de signaler la complétion.
4. Si le test en échec est antérieur à la tâche en cours (régression
   préexistante), le signaler explicitement à l'utilisateur avec le
   contexte : "Ce test était déjà en échec avant mes modifications.
   Dois-je le corriger maintenant ou l'ignorer pour cette tâche ?"

---

### Si une violation de couche est détectée par grep

1. Identifier précisément le fichier et la ligne.
2. Proposer le refactoring minimal qui corrige la violation :
   - Logique métier dans un router → déplacer dans le service correspondant
   - Appel HTTP dans un service → déplacer dans le client IBM PA
   - Instanciation directe → remplacer par une dépendance `Depends`
3. Appliquer la correction avant de signaler la complétion.

---

### Si un champ datetime est sans normalisation UTC

1. Identifier toutes les comparaisons de datetimes lus depuis la base.
2. Ajouter le pattern de normalisation à chaque point de lecture.
3. Ne pas corriger uniquement le cas détecté — vérifier l'ensemble du
   service modifié pour d'autres occurrences du même oubli.

---

### Si le smoke test uvicorn échoue

1. Lire le traceback complet.
2. Selon l'erreur :
   - `ModuleNotFoundError` → dépendance manquante, relancer `pip install`
   - `ValidationError` (pydantic-settings) → variable d'environnement
     absente de `.env.local`, vérifier `.env.example` pour identifier
     la variable manquante
   - `OperationalError` SQLAlchemy → problème de schéma, supprimer
     `pa_explorer.db` et relancer
3. Signaler le type d'erreur et sa résolution à l'utilisateur si le
   contexte d'exécution ne permet pas la correction automatique.

---

### Si une vérification indicative (Section 3) échoue

Signaler l'écart dans le rapport de complétion avec le format suivant :

> Vérification indicative I-X non satisfaite : [description factuelle
> de l'écart]. Correction recommandée : [action concrète]. Cette
> vérification n'est pas bloquante pour la présente tâche.

Ne pas corriger automatiquement sans en avertir l'utilisateur, sauf
si la correction est triviale (un import manquant dans `main.py`, une
ligne dans `.env.example`).

---

## Références croisées

- `docs/skills/add_ibm_pa_endpoint.md` — procédure spécifique pour
  l'ajout d'un endpoint IBM PA, inclut ses propres pièges et validations
- `CLAUDE.md` à la racine — patterns d'architecture obligatoires et
  pièges critiques du projet
- `docs/learning/decisions.md` — décisions architecturales D-001 à
  D-013 avec leur justification et leur statut (définitif / révisable)

---

## Évolutions prévues

**Semaine 5 — Outils de formatage et linting**
Intégration de `ruff` (formatage + linting) dans `requirements.txt`
section dev. `ruff format app/` et `ruff check app/` seront ajoutés
aux étapes 2 et 3 de la Section 4.

**Semaine 5 — Pre-commit hooks**
Configuration de `pre-commit` pour exécuter automatiquement les
vérifications de ce skill à chaque `git commit`. Cela rendra les
vérifications bloquantes sans intervention manuelle.

**Semaine 5 — Tests pytest réels**
La vérification B-7 deviendra significative dès les premiers tests
métier écrits sur les services existants.

**Semaine 5 ou 6 — Migrations Alembic**
La vérification I-3 (imports de modèles dans `main.py`) sera partiellement
remplacée par une vérification Alembic qui détecte les modifications
de schéma non migrées. La suppression manuelle de `pa_explorer.db`
sera remplacée par `alembic upgrade head`.

**Semaine 5 ou 6 — Type checking mypy**
Ajout de `mypy` dans la procédure. Nécessite les stubs
`sqlalchemy[mypy]` pour une couverture complète.
