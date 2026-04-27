# Codebase Tour — PA-Explorer

> Document généré le 26/04/2026 après exploration complète du projet.  
> Public cible : développeur qui revient sur le projet après une pause, ou nouvel arrivant.

---

## Architecture générale

PA-Explorer est une API REST construite sur **FastAPI**, un framework Python moderne qui génère automatiquement une documentation OpenAPI (Swagger). L'application suit une architecture en couches classique : la configuration est centralisée, la base de données est isolée dans son propre module, les routes sont regroupées par domaine fonctionnel, et les schémas de validation des données sont séparés des routes.

Le flux d'une requête entrante est le suivant : le serveur **Uvicorn** reçoit la requête HTTP, la transmet à l'application **FastAPI** définie dans `main.py`, qui la route vers le bon fichier dans `routers/`. Le router valide la réponse via un schéma dans `schemas/` avant de la renvoyer au client.

```
Requête HTTP
    │
    ▼
Uvicorn (serveur ASGI)
    │
    ▼
app/main.py  ←── app/config.py (variables d'env)
    │
    ▼
app/routers/health.py  ←── app/database.py
    │
    ▼
app/schemas/health.py (validation de la réponse)
    │
    ▼
Réponse JSON
```

---

## Rôle de chaque fichier Python

### `app/config.py` — Le cerveau de la configuration

Ce fichier définit une classe `Settings` qui hérite de `BaseSettings` (bibliothèque `pydantic-settings`). Au démarrage, Python lit automatiquement les fichiers `.env` puis `.env.local` et injecte les valeurs dans les attributs de la classe. Si une variable obligatoire est absente, l'application refuse de démarrer avec un message d'erreur explicite.

La ligne `settings = Settings()` crée une instance unique de cette configuration. Tous les autres fichiers importent ce singleton : `from app.config import settings`. C'est l'équivalent d'un store de configuration global.

Les trois variables IBM PA (`ibm_pa_base_url`, `ibm_pa_tenant_id`, `ibm_pa_api_key`) n'ont pas de valeur par défaut, ce qui les rend **obligatoires** — l'application ne démarrera pas sans elles.

### `app/database.py` — La couche de persistance

Ce fichier fait trois choses distinctes :

**1. Créer le moteur de connexion (`engine`)** — c'est l'objet SQLAlchemy qui sait comment parler à la base de données. Il est configuré depuis l'URL contenue dans `settings.database_url`. Actuellement cette URL pointe vers un fichier SQLite local (`pa_explorer.db`). Pour passer à PostgreSQL, il suffit de changer cette URL dans `.env.local`.

L'argument `check_same_thread: False` est spécifique à SQLite : sans lui, SQLite se plaindrait quand plusieurs threads tentent d'accéder à la base simultanément (ce que FastAPI fait naturellement).

**2. Définir la classe `Base`** — c'est la classe parente dont hériteront tous les futurs modèles ORM (tables de base de données). Elle est vide pour l'instant mais son existence est nécessaire pour que SQLAlchemy sache où chercher les tables à créer.

**3. Exposer deux utilitaires** — `get_db()` est un générateur qui ouvre une session de base de données, la yield au code appelant, puis la ferme proprement (même en cas d'erreur). `check_db_connection()` exécute un `SELECT 1` pour vérifier que la base répond — utilisé par le health check.

### `app/main.py` — Le point d'entrée de l'application

C'est ici que l'application FastAPI est instanciée et configurée. Le bloc `lifespan` est une fonction qui s'exécute au démarrage (`Base.metadata.create_all`) et à l'arrêt du serveur. `create_all` parcourt tous les modèles qui héritent de `Base` et crée les tables correspondantes dans la base si elles n'existent pas déjà.

La ligne `app.include_router(health.router, prefix="/api/v1")` monte le router du health check sous le préfixe `/api/v1`. Tous les futurs routers (cubes, dimensions, cellules IBM PA...) seront ajoutés de la même façon, chacun avec son propre fichier dans `routers/`.

### `app/routers/health.py` — L'endpoint de santé

Définit un seul endpoint : `GET /health`. À chaque appel, il vérifie l'état de la base de données via `check_db_connection()`, puis retourne un dictionnaire avec le statut global, le nom de l'app, la version, l'état de la base, et un timestamp UTC. Le paramètre `response_model=HealthResponse` indique à FastAPI le schéma attendu en sortie, ce qui alimente la documentation Swagger.

### `app/schemas/health.py` — Le contrat de réponse

Un modèle Pydantic simple qui décrit la structure de la réponse du health check. FastAPI utilise ce modèle pour deux choses : valider que la réponse du router est correcte, et générer le schéma JSON dans Swagger. Sans ce fichier, Swagger afficherait `"string"` à la place du schéma détaillé.

### `app/models/__init__.py` et `app/schemas/__init__.py`

Fichiers vides pour l'instant. Leur présence transforme les dossiers en packages Python importables. Les modèles ORM (tables de base de données) iront dans `models/`, les schémas Pydantic de requête/réponse iront dans `schemas/`.

---

## Analyse des choix techniques

**Pydantic-settings pour la configuration** — plutôt que de lire `os.environ` manuellement, pydantic-settings valide les types (un `bool` mal écrit sera refusé), documente les variables dans le code, et supporte plusieurs sources (`.env`, `.env.local`, variables système). C'est l'approche standard dans l'écosystème FastAPI.

**SQLAlchemy synchrone** — l'application utilise SQLAlchemy en mode synchrone (pas `async`). C'est un choix délibéré pour garder la complexité basse en phase de démarrage. La migration vers le mode async (avec `asyncpg` pour PostgreSQL) est possible sans changer l'interface publique.

**`create_all` au démarrage** — en développement, c'est pratique : les tables apparaissent automatiquement. En production avec PostgreSQL, cette approche sera remplacée par des migrations Alembic (outil de versionnement de schéma de base de données), sinon on ne peut pas modifier une table existante sans la recréer.

**Versionnement d'API dès le départ** — tous les endpoints sont sous `/api/v1/`. Quand une v2 sera nécessaire, les anciens clients continueront à fonctionner sur `/api/v1/` pendant la transition.

**`httpx` inclus mais pas encore utilisé** — il est présent car il sera le client HTTP pour appeler l'API IBM Planning Analytics. Il sert aussi de client de test asynchrone pour pytest.

**`lifespan` plutôt que `on_startup`** — FastAPI a déprécié les handlers `on_startup`/`on_shutdown` au profit du pattern `lifespan` (context manager async). Le code utilise déjà la bonne approche moderne.

---

## Questions ouvertes et zones d'ombre

**1. `pa_explorer.db` — à quoi ça sert ?**
C'est le fichier SQLite créé automatiquement au premier démarrage. SQLite est une base de données embarquée : pas de serveur séparé, tout est dans un fichier sur le disque. En dev c'est idéal. Ce fichier contiendra les futures tables (logs, cache de métadonnées IBM PA, etc.). Il est exclu du git par `.gitignore`.

**2. `httpx` est déclaré deux fois dans `requirements.txt`**
Une fois avec version épinglée (`httpx==0.28.1`) et une fois sans version en commentaire ligne 11. La ligne dupliquée est redondante et devrait être nettoyée.

**3. Aucune authentification sur les endpoints**
Pour l'instant tout est public. Avant de brancher l'API IBM PA, il faudra décider comment sécuriser les endpoints (API key, JWT, OAuth2...).

**4. Pas de configuration CORS**
Si un frontend web doit appeler cette API depuis un navigateur, FastAPI refusera les requêtes cross-origin. Il faudra ajouter `CORSMiddleware`.

**5. Pas de logging applicatif**
Uvicorn loggue les requêtes HTTP, mais il n'y a pas de logging Python pour tracer les événements métier (erreurs IBM PA, tentatives d'authentification, etc.).

**6. `check_db_connection()` ouvre une connexion à chaque health check**
Ce n'est pas un problème en dev, mais sur un système très sollicité, il vaudrait mieux utiliser un ping sur la connexion du pool existant plutôt qu'en ouvrir une nouvelle à chaque fois.

**7. Aucun test écrit**
`pytest` et `pytest-asyncio` sont dans les dépendances mais le dossier `tests/` n'existe pas encore. Un test minimal du health check serait un bon point de départ.

**8. Les credentials IBM PA ne sont pas validés au démarrage**
L'application démarre même si `IBM_PA_API_KEY` est invalide — on ne le saura qu'au premier appel réel à l'API IBM. Un check de connectivité au démarrage (optionnel) pourrait prévenir des surprises.

---

## Résumé de l'état actuel

| Composant | État |
|---|---|
| Structure de projet | Complète et extensible |
| Configuration `.env` / `.env.local` | Fonctionnelle, multi-fichiers |
| Base de données SQLite | Initialisée et connectée |
| Endpoint `GET /api/v1/health` | Fonctionnel, documenté Swagger |
| Client HTTP IBM PA | Non implémenté (`httpx` présent) |
| Authentification des endpoints | Non implémentée |
| Tests automatisés | Non écrits |
| Migrations DB (Alembic) | Non configurées |
