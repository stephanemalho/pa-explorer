# Contexte pour Claude Code

Ce fichier sert à remettre Claude Code dans le contexte du projet 
PA-Explorer au début d'une nouvelle session de développement. Il 
complète le futur fichier CLAUDE.md ou Agents.md qui sera créé en 
semaine 3 du parcours et qui contiendra les instructions techniques 
détaillées.

Je copie-colle le contenu de ce fichier au début d'une nouvelle 
session Claude Code avec un message qui dit "Voici le contexte du 
projet, prends-en connaissance avant qu'on continue".

---

## Le projet PA-Explorer

PA-Explorer est un POC backend pour IBM Planning Analytics on Cloud, 
développé en Python avec FastAPI et SQLAlchemy. Il consomme l'API REST 
TM1 d'IBM PA via un client httpx avec authentification Basic apikey.

L'application expose des routes REST sur préfixe /api/v1 et une 
documentation OpenAPI auto-générée sur /docs. Elle utilise SQLite en 
développement avec migration possible vers PostgreSQL en production.

## Architecture du code

Le code source vit dans le dossier app/ avec la structure suivante.

app/clients/ contient les clients pour les API distantes. Le fichier 
ibm_pa.py contient IBMPAClient qui parle à l'API IBM PA, avec une 
hiérarchie d'exceptions typées IBMPAError et ses sous-classes.

app/services/ contient la logique métier. Le fichier server_service.py 
contient ServerService qui orchestre le cache aside, la lecture en 
base, le rafraîchissement depuis IBM PA, et le mapping des champs.

app/models/ contient les modèles SQLAlchemy. Le fichier server.py 
contient Server avec les colonnes typées et un champ raw_data en Text 
qui stocke le JSON brut de l'API IBM PA.

app/schemas/ contient les modèles Pydantic. Le fichier server.py 
contient ServerResponse et ServersListResponse pour la sérialisation 
des réponses API.

app/routers/ contient les routes FastAPI. Le fichier servers.py expose 
GET /servers et POST /servers/refresh avec injection de dépendance via 
Depends pour la session de base et le client IBM PA.

app/main.py monte les routers et configure le lifespan de l'application.

app/database.py configure le moteur SQLAlchemy et expose get_db.

app/config.py définit Settings via pydantic-settings et lit .env puis 
.env.local.

## Patterns en place

Cache aside avec TTL. Le service vérifie cache_expires_at avant de 
décider d'appeler IBM PA. TTL configurable via 
ibm_pa_servers_ttl_seconds, par défaut 300 secondes en dev.

Injection de dépendance FastAPI. Toutes les dépendances comme la 
session DB, le client IBM PA, le service, sont injectées via Depends 
dans les routes.

Hiérarchie d'exceptions métier. Les erreurs côté IBM PA sont levées 
comme exceptions typées par le client, traduites en HTTPException 
par le router avec des codes HTTP appropriés (502 pour erreurs IBM, 
503 pour réseau, 504 pour timeout).

Schema-on-read avec raw_data. Le modèle Server stocke à la fois des 
champs typés et le JSON brut, pour combiner requêtes BI rapides et 
flexibilité d'évolution.

## Conventions à respecter

Pas de logique métier dans les routers. Les routers délèguent au 
service.

Pas d'appels HTTP directs hors des clients. Les services utilisent les 
clients, les routers utilisent les services.

Toujours injecter les dépendances via Depends. Ne jamais instancier 
les clients ou services directement dans les routers.

Datetimes toujours UTC en code. SQLite ne supporte pas les timezones 
nativement, donc une normalisation est appliquée au point de lecture 
via replace tzinfo timezone.utc.

Les nouvelles entités IBM PA (cubes, dimensions, processus, etc.) 
suivront le même pattern client/service/router/model/schema.

## Pièges connus

SQLite ne stocke pas les timezones malgré DateTime timezone True dans 
SQLAlchemy. Comparer un datetime lu depuis SQLite à un datetime aware 
avec timezone.utc lève une TypeError. Solution : normaliser au point 
de lecture.

Modifier un modèle SQLAlchemy nécessite de supprimer pa_explorer.db 
en environnement de développement, parce qu'Alembic n'est pas encore 
installé. La procédure est documentée dans le README.

Le fichier .env.local est verrouillé par uvicorn quand le serveur 
tourne. Pour le modifier, arrêter uvicorn d'abord.

Les logs uvicorn ne s'affichent pas toujours dans PowerShell Windows. 
Utiliser le navigateur pour observer les réponses HTTP plutôt que les 
logs serveur en cas de doute.

## Pour démarrer une session de développement

1. Activer le venv : `.\venv\Scripts\activate`
2. Vérifier que .env.local contient bien IBM_PA_BASE_URL, IBM_PA_TENANT_ID, 
   IBM_PA_API_KEY
3. Lancer uvicorn : `python -m uvicorn app.main:app --reload`
4. Vérifier que /api/v1/health répond 200 OK
5. Continuer le travail

## Référence pour aller plus loin

Le détail des décisions architecturales est dans 
docs/learning/decisions.md.

Le journal des sessions est dans docs/learning/journal.md.

Les concepts techniques découverts sont dans docs/learning/concepts.md.

Les particularités d'IBM PA sont dans docs/learning/ibm_pa.md.