# Notes de concepts techniques — PA-Explorer

Ce fichier synthétise les concepts techniques découverts au fil du parcours, 
organisés par domaine. Chaque concept est défini brièvement, puis illustré 
par un exemple tiré directement du projet PA-Explorer. Quand un concept est 
issu des notes de LEARNING.md, c'est indiqué. Quand l'explication complète 
le cadre général au-delà de ce qui est dans les sources du projet, c'est 
signalé comme connaissance générale.

---

## CLAUDE - Piège a connaitre 

### Inférence raisonnable

Claude Code a fait ce qu'on appelle de l'inférence raisonnable. Il a lu le contenu factuel de mon fichier, et il a complété avec des éléments qui sont logiques mais non sourcés. Les trois raisons pratiques sont vraies et défendables, mais ce sont les siennes, pas celles que j'avais documentées. Il a lu le document desisions.md et l'affirmation sur D-003 et D-008 est plausible mais elle prête une intention qui n'est pas explicite dans tes fichiers.
C'est exactement le type de comportement contre lequel on doit rester vigilant. Claude Code répond avec confiance et formate sa réponse de manière convaincante, ce qui peut donner l'impression que tout vient de tes documents. Mais une partie significative est de l'extrapolation.
C'est une leçon importante pour la suite de mon parcours. Un bon steering ne suffit pas à garantir que Claude Code restera strictement factuel. Le fichier CLAUDE.md et les fichiers learning donnent à Claude Code un cadre de référence, mais ils ne l'empêchent pas de combler les vides avec ses propres raisonnements quand il sent qu'une réponse plus complète serait attendue.

---

## Python et écosystème

### L'environnement virtuel (venv)

Un environnement virtuel est un dossier isolé qui contient une copie de 
l'interpréteur Python et un ensemble de packages indépendant du système. 
Cela permet à plusieurs projets coexistant sur la même machine d'avoir des 
versions de dépendances différentes sans conflit.

Dans PA-Explorer, le dossier `venv/` à la racine joue ce rôle. Il est créé 
avec `python -m venv venv` et activé avec `.\venv\Scripts\Activate.ps1` sous 
Windows. Une fois activé, `pip install -r requirements.txt` installe les 
packages dans cet environnement isolé plutôt que globalement. (Analogie 
JavaScript issue de LEARNING.md : `venv` ≈ `node_modules`.)

### Le fichier requirements.txt

`requirements.txt` liste les dépendances du projet avec leurs versions 
exactement épinglées. Épingler les versions garantit que deux développeurs 
ou deux environnements d'exécution installent exactement le même code. 
(Analogie JavaScript issue de LEARNING.md : `requirements.txt` ≈ `package.json`.)

Dans PA-Explorer, `requirements.txt` contient par exemple `fastapi==0.115.12` 
et `sqlalchemy==2.0.40`. Une ligne en double pour `httpx` a été supprimée en 
cours de semaine 2 — illustration du fait que `requirements.txt` est un fichier 
à maintenir activement.

### Les imports et la structure de packages

Un dossier devient un package Python importable en y plaçant un fichier 
`__init__.py`, même vide. Sans ce fichier, Python ne reconnaît pas le dossier 
comme un module.

Dans PA-Explorer, chaque sous-dossier de `app/` (`routers/`, `schemas/`, 
`models/`, `clients/`, `services/`) contient un `__init__.py` vide. Cela 
permet les imports du style `from app.routers import servers` dans `main.py`.

---

## FastAPI

### ASGI et Uvicorn

ASGI (Asynchronous Server Gateway Interface) est le protocole qui fait le 
lien entre un serveur HTTP et une application Python asynchrone. FastAPI est 
un framework ASGI. Uvicorn est le serveur qui implémente ce protocole et 
expose l'application sur un port réseau. (Connaissance générale — non expliqué 
dans LEARNING.md mais mentionné comme zone d'ombre dans la session du 26 avril.)

Dans PA-Explorer, la commande de lancement est `python -m uvicorn app.main:app --reload`. 
`app.main` désigne le module Python, `app` désigne l'objet FastAPI instancié 
dans ce module, et `--reload` active le rechargement automatique quand un 
fichier source est modifié. (Analogie JavaScript issue de LEARNING.md : 
`python -m uvicorn app.main:app --reload` ≈ `pnpm run dev`.)

### Les routers

Un router FastAPI (`APIRouter`) est un regroupement d'endpoints liés par un 
domaine fonctionnel. Il est instancié dans un module dédié, peuplé 
d'endpoints, puis monté dans l'application principale via `include_router`.

Dans PA-Explorer, `app/routers/health.py` contient l'endpoint `/health` et 
`app/routers/servers.py` contient les endpoints `/servers` et `/servers/refresh`. 
Dans `app/main.py`, les deux routers sont montés sous le même préfixe 
`/api/v1` :

```python
app.include_router(health.router, prefix="/api/v1")
app.include_router(servers.router, prefix="/api/v1")
```

Cette séparation permet d'ajouter un domaine `cubes` ou `dimensions` en 
créant simplement un nouveau fichier dans `routers/` sans toucher au reste.

### L'injection de dépendance avec Depends

`Depends` est le mécanisme par lequel FastAPI injecte des services dans les 
fonctions de route. Au lieu d'instancier un service à l'intérieur de la route, 
on déclare en paramètre ce dont la route a besoin. FastAPI se charge de 
l'instanciation et de la transmission. (Concept expliqué dans LEARNING.md, 
section semaine 2.)

Dans PA-Explorer, le router `servers.py` déclare deux fonctions fabriques :

```python
def get_ibm_pa_client() -> IBMPAClient: ...
def get_server_service(
    db: Session = Depends(get_db),
    client: IBMPAClient = Depends(get_ibm_pa_client),
) -> ServerService: ...
```

La route `list_servers` reçoit ensuite `service: ServerService = Depends(get_server_service)` 
en paramètre. La chaîne de dépendances est résolue automatiquement par FastAPI 
à chaque requête.

### response_model et la documentation Swagger

Le paramètre `response_model` sur un endpoint indique à FastAPI le schéma 
Pydantic attendu en sortie. FastAPI utilise ce schéma pour valider la réponse 
et pour générer automatiquement la documentation OpenAPI visible sur `/docs`.

Sans `response_model`, Swagger affiche `"string"` au lieu du schéma structuré. 
C'est le problème qui a été résolu en semaine 1 en ajoutant `HealthResponse` 
(issu de la correction documentée dans la session du 22 avril), puis en 
semaine 2 avec `ServersListResponse`.

---

## SQLAlchemy

### Les modèles ORM

Un modèle SQLAlchemy est une classe Python qui représente une table de base 
de données. Chaque attribut de classe correspond à une colonne. SQLAlchemy 
génère automatiquement les requêtes SQL à partir des opérations sur ces objets.

Dans PA-Explorer, `app/models/server.py` définit la classe `Server` qui hérite 
de `Base`. La syntaxe moderne SQLAlchemy 2.0 utilise `Mapped` et `mapped_column` :

```python
class Server(Base):
    __tablename__ = "servers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
```

### Les sessions et get_db

La session SQLAlchemy est l'objet qui maintient le contexte d'une transaction 
avec la base de données. Elle accumule les modifications en mémoire et les 
envoie à la base en un seul bloc lors du `commit()`.

Dans PA-Explorer, `app/database.py` expose `get_db()` comme générateur FastAPI :

```python
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

Le `yield` garantit que la session est fermée après la requête, même en cas 
d'erreur. Ce générateur est injecté dans les routes et les services via `Depends`.

### create_all et les migrations futures

`Base.metadata.create_all(bind=engine)` crée toutes les tables définies par 
les modèles qui héritent de `Base`, mais uniquement si ces tables n'existent 
pas encore. Elle ne modifie pas les tables existantes. C'est ce qui est 
exécuté dans le `lifespan` de `app/main.py` à chaque démarrage du serveur.

En développement, quand un modèle évolue (ajout de colonnes), la stratégie 
actuelle est de supprimer `pa_explorer.db` pour forcer une recréation complète. 
En production, cela sera remplacé par des migrations Alembic, qui permettent 
de modifier le schéma sans perdre les données. (Concept expliqué dans LEARNING.md, 
section du 28 avril.)

### La particularité timezone de SQLite

SQLite ne stocke pas nativement les informations de fuseau horaire dans les 
colonnes `DATETIME`. Malgré la déclaration `DateTime(timezone=True)` dans le 
modèle SQLAlchemy, les valeurs relues depuis SQLite arrivent sous forme de 
`datetime` naïfs (sans `tzinfo`). Comparer un datetime naïf avec un datetime 
aware (comme `datetime.now(timezone.utc)`) lève une `TypeError` en Python.

C'est le bug rencontré en semaine 2 sur l'endpoint GET /api/v1/servers avec 
`force_refresh=false`. Le correctif dans `_get_cached_servers` de 
`server_service.py` consiste à détecter les datetimes naïfs et à les traiter 
comme UTC avant la comparaison :

```python
if expires.tzinfo is None:
    expires = expires.replace(tzinfo=timezone.utc)
```

---

## Patterns de cache

### Cache aside avec TTL

Le cache aside est un pattern où l'application est responsable de lire et 
d'écrire dans son propre cache, par opposition à un cache transparent géré 
par l'infrastructure. Le TTL (Time To Live) est la durée pendant laquelle une 
donnée en cache est considérée fraîche. (Concept expliqué en prose dans 
LEARNING.md, section semaine 2.)

Dans PA-Explorer, `_get_cached_servers()` dans `server_service.py` implémente 
ce pattern : elle requête la base, vérifie `cache_expires_at`, et retourne 
`None` si le cache est expiré. `_refresh_from_ibm_pa()` calcule le prochain 
`cache_expires_at` comme `datetime.now(UTC) + timedelta(seconds=TTL)` et 
l'écrit sur chaque enregistrement.

Le TTL actuel est de 300 secondes (5 minutes), défini dans `config.py` comme 
`ibm_pa_servers_ttl_seconds: int = 300`. Cette valeur a été choisie 
délibérément courte pour qu'un cycle d'expiration soit observable dans une 
session de travail. (Source : decisions.md, D-006.)

### Schema-on-read avec raw_data

Le pattern schema-on-read consiste à stocker une représentation brute de la 
donnée telle qu'elle arrive de la source, en plus des colonnes typées et 
indexées. Cela permet d'absorber les évolutions du schéma source sans migration, 
et de réinterroger les données brutes si de nouveaux champs apparaissent.

Dans PA-Explorer, chaque enregistrement `Server` contient un champ `raw_data` 
de type `Text` qui stocke le JSON brut de la réponse IBM PA. Le champ est 
exposable dans la réponse API via le query param `include_raw=true`. (Source : 
decisions.md, D-008.)

---

## HTTP et httpx

### Le pattern client API

Quand une application doit communiquer avec un service distant, cette 
communication est encapsulée dans un module dédié appelé client. Le client 
masque les détails du protocole HTTP, des URLs, des headers d'authentification, 
et de la sérialisation. (Concept expliqué dans LEARNING.md, section semaine 2.)

Dans PA-Explorer, `app/clients/ibm_pa.py` contient la classe `IBMPAClient`. 
La méthode `get_servers()` encapsule un appel `GET` vers IBM PA, parse la 
réponse OData, et retourne une liste de dicts Python. Le reste de l'application 
ne connaît pas l'URL, ni les headers, ni le format de réponse IBM PA.

### Basic Auth avec httpx

HTTP Basic Authentication encode les credentials en Base64 dans l'en-tête 
`Authorization`. Dans le cas d'IBM PA SaaS, le format est 
`base64("apikey:" + api_key)` — le username est la chaîne littérale `"apikey"` 
et non l'email de l'utilisateur. (Source : decisions.md, D-004.)

Dans PA-Explorer, `httpx.BasicAuth("apikey", api_key)` est calculé une seule 
fois dans le constructeur de `IBMPAClient` et réutilisé à chaque appel :

```python
self._auth = httpx.BasicAuth("apikey", api_key)
```

### Timeouts et exceptions httpx

httpx lève des exceptions typées pour les différentes catégories d'erreur 
réseau : `httpx.TimeoutException` si la requête dépasse le délai configuré, 
`httpx.ConnectError` si la connexion ne peut pas être établie (DNS, port 
fermé). Ces exceptions sont distinctes des erreurs HTTP (statuts 4xx/5xx) 
qui sont représentées dans l'objet `response`.

Dans PA-Explorer, `IBMPAClient.get_servers()` attrape ces exceptions et les 
transforme en exceptions applicatives typées (`IBMPATimeoutError`, 
`IBMPAConnectionError`). Le router les convertit ensuite en réponses HTTP 
avec les bons codes (504 pour timeout, 503 pour connexion refusée).

---

## Pydantic

### Validation de réponses avec BaseModel

Un modèle Pydantic est une classe qui définit un contrat de données avec 
validation automatique des types. FastAPI l'utilise pour valider les réponses 
avant de les envoyer et pour générer la documentation Swagger.

Dans PA-Explorer, `ServerResponse` dans `app/schemas/server.py` définit les 
champs attendus dans la réponse d'un serveur. Le paramètre `response_model=ServersListResponse` 
sur les routes garantit que toute réponse non conforme lèverait une erreur.

### ConfigDict et from_attributes

`ConfigDict(from_attributes=True)` permet à Pydantic de construire un modèle 
à partir d'un objet quelconque (comme un objet SQLAlchemy) en lisant ses 
attributs plutôt qu'en attendant un dictionnaire. Sans cette configuration, 
Pydantic refuserait de consommer un objet ORM directement.

Dans PA-Explorer, `ServerResponse` porte cette configuration, ce qui permet 
d'écrire directement `ServerResponse.model_validate(server_orm_object)` ou 
de passer un objet `Server` là où Pydantic attend des données.

### pydantic-settings et BaseSettings

`pydantic-settings` est une extension de Pydantic qui lit la configuration 
depuis des fichiers `.env` et des variables d'environnement, avec validation 
des types. Les champs sans valeur par défaut sont obligatoires — l'application 
refuse de démarrer s'ils sont absents.

Dans PA-Explorer, `app/config.py` définit `class Settings(BaseSettings)` avec 
les champs `ibm_pa_base_url`, `ibm_pa_tenant_id` et `ibm_pa_api_key` sans 
valeur par défaut — ils sont donc obligatoires. La configuration lit 
successivement `.env` puis `.env.local`, ce dernier ayant priorité sur le 
premier.
