# CLAUDE.md

Ce fichier guide Claude Code dans le projet PA-Explorer. Il est lu 
automatiquement à chaque démarrage de session dans ce dépôt.

## Le projet en deux phrases

PA-Explorer est un POC backend Python qui consomme l'API REST IBM 
Planning Analytics SaaS pour exposer serveurs, cubes, dimensions et 
données de cellules à un futur frontend BI assisté par IA. La vision 
long terme est un outil de monitoring de performance pour analystes 
business, avec analyse automatique des anomalies par un agent IA.

## Stack technique

Python 3.12, FastAPI pour l'API REST, SQLAlchemy synchrone pour 
l'ORM, SQLite en développement (migration PostgreSQL prévue), httpx 
pour les appels HTTP distants, pytest et pytest-asyncio pour les 
tests à venir en semaine 5 du parcours d'apprentissage.

## Architecture du code
app/
├── clients/        # Clients pour APIs distantes (httpx)
│   └── ibm_pa.py   # IBMPAClient + hiérarchie d'exceptions IBMPAError
├── services/       # Logique métier et orchestration
│   └── server_service.py  # Cache-aside avec TTL, mapping IBM PA
├── models/         # Modèles ORM SQLAlchemy (héritent de Base)
│   └── server.py   # Server avec colonnes typées + raw_data JSON
├── schemas/        # Modèles Pydantic pour requêtes/réponses
│   └── server.py   # ServerResponse, ServersListResponse
├── routers/        # Endpoints FastAPI, un fichier par domaine
│   └── servers.py  # GET /servers, POST /servers/refresh
├── config.py       # Settings via pydantic-settings (.env + .env.local)
├── database.py     # Engine SQLAlchemy, get_db, check_db_connection
└── main.py         # App FastAPI, lifespan, mount des routers

Chaque nouveau domaine (cubes, dimensions, processus à venir) suit 
le même pattern. Créer le client si l'API change, le service avec 
cache-aside, le modèle SQLAlchemy, le schéma Pydantic, le router 
avec injection de dépendance, et monter le router dans main.py sous 
le préfixe /api/v1.

## Patterns en place

**Cache aside avec TTL**. Le service vérifie cache_expires_at avant 
de décider d'appeler IBM PA. TTL configurable via 
ibm_pa_servers_ttl_seconds, par défaut 300 secondes en dev.

**Injection de dépendance FastAPI**. Session DB, client IBM PA, 
service sont tous injectés via Depends. Ne jamais instancier 
directement dans les routers.

**Hiérarchie d'exceptions métier**. Le client lève des exceptions 
typées (IBMPAAuthError, IBMPATimeoutError, etc.). Le router les 
traduit en HTTPException avec codes HTTP cohérents (502 pour 
erreurs IBM, 503 pour réseau indisponible, 504 pour timeout).

**Schema-on-read avec raw_data**. Le modèle Server stocke à la fois 
les champs typés et le JSON brut. Cela permet les requêtes BI 
rapides via les colonnes typées et la flexibilité d'évolution via 
raw_data, qui sera aussi la matière passée aux LLMs.

## Conventions strictes

Pas de logique métier dans les routers. Les routers délèguent au 
service.

Pas d'appels HTTP directs hors des clients. Le service utilise le 
client, le router utilise le service.

Toujours injecter les dépendances via Depends. Ne jamais instancier 
les clients ou services directement dans les routers.

Datetimes toujours UTC en code. SQLite ne supporte pas les timezones 
nativement malgré DateTime(timezone=True), donc normaliser les 
datetimes naïfs au point de lecture via .replace(tzinfo=timezone.utc).

## Configuration et démarrage

Variables d'environnement requises dans .env.local (l'app refuse de 
démarrer sans elles).
IBM_PA_BASE_URL=https://eu-central-1.planninganalytics.saas.ibm.com
IBM_PA_TENANT_ID=...
IBM_PA_API_KEY=...

Procédure de démarrage.

```bash
# Activer le venv (Windows PowerShell)
.\venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt

# Lancer le serveur de développement
python -m uvicorn app.main:app --reload

# Vérifier que tout fonctionne
# Naviguer vers http://localhost:8000/api/v1/health
# Doit retourner {"status": "ok", ...}
```

Note importante. uvicorn n'est pas dans le PATH système, donc 
toujours utiliser python -m uvicorn et pas uvicorn directement.

## Pièges connus de l'environnement

**Modification de modèle SQLAlchemy**. En développement, modifier un 
modèle nécessite de supprimer pa_explorer.db pour que create_all 
recrée la table. La procédure complète est dans le README à la 
racine. Alembic sera installé en semaine 5 ou 6 pour gérer cela 
proprement en production.

**Fichier base de données verrouillé**. Si del pa_explorer.db échoue 
avec "fichier en cours d'utilisation", arrêter uvicorn (Ctrl+C), 
fermer l'onglet pa_explorer.db dans VS Code s'il est ouvert, puis 
réessayer. Le script reset_db.ps1 à la racine automatise cette 
procédure.

**Logs uvicorn invisibles dans PowerShell**. Sur Windows, les logs 
de requêtes HTTP ne s'affichent parfois pas dans le terminal 
uvicorn. Pour déboguer, utiliser directement le navigateur sur les 
URLs et observer les réponses HTTP, plutôt que de chercher les logs 
serveur.

**Authentification IBM PA SaaS**. Le username du Basic Auth doit 
être la chaîne littérale "apikey" et non l'email de l'utilisateur. 
C'est documenté par IBM pour les déploiements MCSP. Toute autre 
valeur de username échoue avec AuthorizedConnectionFailed.

## Tests

```bash
# Lancer toute la suite (vide actuellement)
python -m pytest

# Lancer un fichier de test précis
python -m pytest tests/test_health.py -v
```

Le squelette tests/ existe avec __init__.py et conftest.py. Les 
tests réels seront écrits en semaine 5 du parcours d'apprentissage 
quand seront couverts simultanément les mocks IBMPAClient via 
dependency_overrides, les bases SQLite en mémoire, et les 
httpx.MockTransport.

## Documentation projet

Pour aller plus loin que ce fichier de steering, consulter.

**docs/learning/decisions.md** — Justifications des choix 
architecturaux historiques avec leur contexte. À consulter quand 
une décision technique est questionnée ou doit être révisée.

**docs/learning/ibm_pa.md** — Référentiel métier IBM Planning 
Analytics. Endpoints découverts, particularités d'authentification, 
structure des réponses, concepts du domaine TM1.

**docs/skills/add_ibm_pa_endpoint.md** — Procédure réutilisable pour 
ajouter un nouvel endpoint IBM PA suivant le pattern établi en 
semaine 2. À consulter chaque fois que l'utilisateur demande "ajoute 
un endpoint pour [entité IBM PA]" comme Cubes, Dimensions, Processes.

**docs/learning/claude_code_concepts.md** — Notes spécifiques sur Claude Code, 
ses comportements à connaître, ses commandes utiles, et les patterns 
de collaboration. À consulter pour les questions sur l'outil lui-même 
plutôt que sur le projet.

**docs/learning/concepts.md** — Notes synthétiques sur les concepts 
techniques (SQLAlchemy, FastAPI, Pydantic, patterns de cache, etc.) 
organisés par thème.

**docs/learning/journal.md** — Chronologie des sessions de travail 
avec leçons et difficultés rencontrées.

**docs/learning/prompts.md** — Manuel des bons prompts forgés au 
fil du parcours, avec leur note pédagogique.

**docs/learning/README.md** — Index général de l'architecture 
documentaire et vue d'ensemble du parcours d'apprentissage en 
huit semaines.

**README.md** à la racine — Procédures opérationnelles complètes, 
commandes de développement, gestion de la base de données.

## Mode de travail attendu

Quand une feature touche à l'architecture (nouveaux endpoints, 
nouveau modèle, nouveau pattern), commencer en Plan Mode et 
proposer un plan structuré avant toute écriture de code.

Quand une correction de bug est circonscrite et que le diagnostic 
est partagé en amont, le mode direct est plus efficace.

Toujours respecter la séparation client/service/router/model/schema 
décrite plus haut. Si une feature ne s'inscrit pas dans ce pattern, 
proposer une nouvelle convention plutôt que de la contourner 
silencieusement.

Quand l'utilisateur demande l'ajout d'un endpoint IBM PA, consulter 
systématiquement docs/skills/add_ibm_pa_endpoint.md avant de proposer 
un plan d'implémentation. Cette compétence formalise le pattern de 
référence pour assurer la cohérence entre les différentes entités.

## Conventions Git

Les messages de commit suivent le pattern conventional commits.
type(scope): description courte en anglais à l'impératif