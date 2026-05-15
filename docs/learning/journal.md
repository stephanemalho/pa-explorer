# Journal de bord — PA-Explorer

Ce fichier retrace la chronologie des sessions de travail sur le projet, 
en s'appuyant sur les notes de LEARNING.md à la racine et sur l'historique 
git. Les dates des sessions sont issues de LEARNING.md. Les dates des commits 
sont issues de `git log`.

---

## Session du 22 avril 2026 — Lancement du projet

Le projet démarre avec une ambition claire : construire une API REST en Python 
qui serve de passerelle vers IBM Planning Analytics. C'est aussi le premier 
contact avec Claude Code, utilisé non pas comme un simple générateur de code 
mais comme un partenaire de conception à qui l'on soumet d'abord un plan avant 
de lancer l'exécution.

La première session pose les fondations en quelques heures. La structure de 
projet FastAPI est générée, l'endpoint GET /api/v1/health fonctionne, Swagger 
est accessible, et la base SQLite s'initialise au démarrage. L'impression est 
positive : la structure proposée semble solide, la documentation s'affiche sans 
friction, et chaque fichier a un rôle clair.

La première difficulté apparaît avec Postman. La tentative de configurer 
l'authentification pour appeler l'API IBM PA échoue, parce que les variables 
d'authentification sont mal renseignées. La séance se conclut sur la décision 
pragmatique de ne pas insister sur Postman et de se concentrer sur 
l'implémentation depuis VS Code, où le workflow est mieux maîtrisé.

La leçon technique principale de cette session concerne l'écosystème Python 
vu depuis un profil JavaScript. Le dossier `venv` est l'équivalent de 
`node_modules`. Le fichier `requirements.txt` remplit le même rôle que 
`package.json`. La commande `python -m uvicorn app.main:app --reload` est 
fonctionnellement similaire à `pnpm run dev`. Ces analogies, notées 
explicitement dans LEARNING.md, permettent d'ancrer des concepts nouveaux sur 
des repères déjà connus.

Une subtilité est apparue immédiatement après l'installation : les scripts 
Python (uvicorn, pytest) sont installés dans un répertoire non présent dans 
le PATH Windows. La commande `uvicorn` seule ne fonctionnait pas. La solution 
`python -m uvicorn` est la forme canonique à retenir.

Note sur le git : le premier commit du dépôt (`44b8da0`) date du 27 avril 2026 
selon `git log`. Le projet a donc existé plusieurs jours sans être versionné, 
ce qui explique l'absence de trace git de la session du 22 avril. Le dépôt a 
été initialisé après coup.

---

## Session du 26 avril 2026 — Retour sur expérience et préparation de la semaine 2

La deuxième session est une session de recul. Elle commence par un exercice 
de rétrospective structuré autour de questions sur l'expérience Claude Code de 
la semaine précédente.

La conclusion générale est positive. Aucune limite significative n'a été 
perçue dans la compréhension des prompts. Un seul écart a été identifié : la 
configuration `pydantic-settings` avait été initialisée avec `env_file=".env"` 
uniquement, alors que le fichier de credentials réel était `.env.local`. Ce 
n'est pas une erreur de Claude mais un oubli de précision dans les instructions 
initiales. Le correctif a été ajouté en cours de session.

Deux regrets émergent de cette rétrospective. Le premier : aucun dépôt GitHub 
n'a été créé lors de la semaine 1. C'est une omission qui n'est pas imputable 
à Claude — sans instruction explicite, il n'a aucune raison de le suggérer. 
Le second regret concerne certaines zones d'ombre persistantes sur l'écosystème : 
à quoi servent exactement FastAPI et uvicorn ? Pourquoi la base SQLite affiche 
"connected" alors qu'aucune table n'y a encore été créée manuellement ? Ces 
questions témoignent d'une connaissance fonctionnelle mais pas encore 
conceptuelle de l'infrastructure en place.

La session se conclut par une phase d'étude de la documentation IBM PA. Un 
bloc de notes sur le modèle TM1 est rédigé dans LEARNING.md : cubes, 
dimensions, ensembles de cellules, éléments, processus, OData. Cette lecture 
prépare la semaine 2 et révèle un sujet qui suscite un intérêt particulier : 
la gestion des actifs de base de données TM1 avec Git, documentée par IBM et 
qui permettrait de versionner des cubes et des vues sans arrêter la base.

---

## Session du 28 avril 2026 — Semaine 2, implémentation de la feature serveurs

La troisième session est la plus dense du parcours à ce stade. Elle couvre 
la conception, l'implémentation, et le débogage de la première feature métier 
réelle du projet.

La session débute par un apprentissage théorique. Avant d'écrire une ligne de 
code, cinq concepts techniques sont expliqués et intégrés : le pattern client 
API et son rôle d'isolation, la séparation architecturale entre métadonnées 
relationnelles et données volumineuses, le cache aside avec TTL, l'injection 
de dépendance FastAPI via `Depends`, et le format Parquet pour le stockage 
futur des cellules. Ces concepts sont rédigés en prose dans LEARNING.md et 
constituent la base conceptuelle sur laquelle repose toute l'architecture de 
la feature.

Le cycle Plan Mode est utilisé pour la première fois sur une feature 
structurante. Un prompt de planification en neuf sections déclenche une 
recherche documentaire sur l'authentification IBM PA SaaS, une investigation 
qui révèle que les tentatives Postman de la semaine 1 avaient échoué pour une 
raison précise : le username du Basic Auth doit être la chaîne littérale 
`"apikey"` et non l'adresse email de l'utilisateur. Cette découverte valide 
à posteriori la démarche de recherche documentaire avant implémentation.

L'implémentation se déroule sans accroc majeur : client IBM PA avec hiérarchie 
d'exceptions, modèle SQLAlchemy `Server` avec sept colonnes typées plus 
`raw_data`, service cache-aside avec TTL de 300 secondes, router FastAPI avec 
les routes GET /api/v1/servers et POST /api/v1/servers/refresh. Les premiers 
appels à IBM PA retournent des données réelles.

Le débogage commence immédiatement après les premiers tests. Le premier bug 
se manifeste par un HTTP 500 sur le chemin `force_refresh=false`, alors que 
`force_refresh=true` fonctionne correctement. La méthode de diagnostic adoptée 
est celle qui deviendra une habitude : comparer le cas qui marche et le cas 
qui plante pour cerner la zone exacte du problème. La cause est une comparaison 
entre un `datetime` avec timezone (créé avec `timezone.utc`) et un `datetime` 
naïf (retourné par SQLite, qui ne stocke pas les informations de fuseau horaire 
malgré la déclaration `DateTime(timezone=True)` dans le modèle SQLAlchemy). 
Le correctif consiste à détecter les datetimes naïfs lors de la lecture et à 
leur attacher `UTC` via `.replace(tzinfo=timezone.utc)`.

Le deuxième bug est plus subtil : les champs `accepting_clients`, `href` et 
`is_v12` sont présents dans `raw_data` mais restent `null` dans la réponse 
API. Le service écrit bien ces champs en base, mais la fonction `_build_response` 
dans le router les omet lors de la construction des objets `ServerResponse`. 
Les données transitent correctement jusqu'à la base de données et s'arrêtent 
là, silencieusement, sans aucune erreur. C'est une illustration directe du 
type de régression invisible que seuls les tests automatisés permettraient de 
détecter systématiquement — la motivation concrète pour la semaine 5 du 
parcours.

La session se termine par une réflexion sur les migrations SQLAlchemy. Chaque 
modification de schéma en développement nécessite de supprimer `pa_explorer.db` 
pour que `create_all` recrée la table avec le bon schéma. C'est une pratique 
acceptable en développement sur des données rechargeables, et radicalement 
inacceptable en production où Alembic prend le relais.

À la fin de la semaine 2, le projet expose une API REST fonctionnelle connectée 
à IBM PA, avec un cache local, une gestion d'erreurs en sept catégories, et 
une architecture en couches prête à accueillir les prochaines entités.

## Session du 4 mai 2026 - Semaine 3, création du CLAUDE.md et teste de steering

Session du début de semaine 3. Création du CLAUDE.md consolidé en 
français à la racine du projet, suppression du CONTEXT_FOR_CLAUDE_CODE.md 
devenu redondant. Premier test de steering réussi sur la consultation 
de decisions.md à propos du choix de SQLite. Observation importante : 
Claude Code lit bien les fichiers indiqués dans CLAUDE.md, mais peut 
compléter ses réponses avec des inférences raisonnables qui ne sont 
pas littéralement dans les sources. Pour les sujets où la fidélité 
compte, prévoir d'ajouter une consigne explicite dans le prompt.

## Session du 11 mai 2026 — Semaine 3 : intégration de la route GET /api/v1/servers/{server_name}/cubes
Apprentissages techniques
Mise en évidence d’une limitation de str.format en Python : la méthode ne prend pas en charge le formatage partiel, contrairement à ce que l’on pourrait supposer intuitivement. Point à retenir pour les développements futurs.
Fonctionnement de Claude Code — gestion de l’historique
Activation automatique de la commande /compact durant la session. À cette occasion, j’ai identifié que Claude Code conserve l’historique des conversations dans le répertoire suivant :
C:\Users\smalho\.claude\projects\c--Users-smalho-Desktop-pa-explorer
```

Il y stock l'historique des discussions meme après le compact, il est possible de retrouver l'historique complet de la discussion d'un projet.

J'ai aussi remarqué quelque chose d'intéressant, claude crée un .claude dans mon répertoire Utilisateurs, et il garde l'entièreté des discussions avant compact (c'est une impréssion que j'ai) car il à dit apres le compact: If you need specific details from before compaction (like exact code snippets, error messages, or content you generate) read the full transcript at: C:\Users\smalho\.claude\projects\c--Users-smalho-Desktop-pa-explorer\1dbc581c-4ea4-46b7-b946-20337976817b.jsonl, Donc je pense qu'il est possible de retrouver un historique complet des discusssions meme si c'est pas très lisible pour humain. Je me demande s'il est necessaire de nettoyer cela si je supprime un projet ou s'il devient trop gros dans le temps. Mais c'est un bon apprentissage pour le moment.

Je viens de découvrir que mon tenant Seminaire contient des cubes avec une vraie complexité métier TM1. Le cube Categories Salaires a des règles de calcul TurboIntegrator complètes, des feeders auto-générés, des dimensions multiples qui apparaissent dans les règles comme annee, phase, categories_salaires, mois, salaires. J'ai aussi des attributs comme Caption qui me donnent un nom d'affichage en anglais Salary categories.
Cette richesse ouvre énormément de portes pour la suite de mon projet. On pourra un jour exposer ces règles dans un éditeur, visualiser les dépendances entre cubes via les feeders, suivre les dates de mise à jour pour détecter les changements. Mais on ne fera pas tout cela maintenant, sinon on perdrait le cap.

### Command :
Taper le symbole :
```bash
 / 
```
 afin de lister l'ensemble des commandes disponobles pour Claude Code.
L’historique complet d’un projet y reste accessible, y compris après l’exécution de /compact. Après la compaction, Claude m’a explicitement indiqué :
« If you need specific details from before compaction (like exact code snippets, error messages, or content you generate) read the full transcript at: C:\Users\smalho.claude\projects\c–Users-smalho-Desktop-pa-explorer\1dbc581c-4ea4-46b7-b946-20337976817b.jsonl »
Il semble donc possible de récupérer l’intégralité des échanges, bien que le format .jsonl ne soit pas particulièrement lisible pour un humain.
Point ouvert
Reste à déterminer s’il est nécessaire de nettoyer ce répertoire lors de la suppression d’un projet, ou si une purge périodique est requise pour éviter une croissance excessive du dossier .claude dans le temps.

## Session du 12 mai 2026 — Attente des actions de claude suite à un settup de skills 

Je m'attends à ce que Claude Code consulte add_ibm_pa_endpoint.md sans qu'on lui demande, qu'il identifie correctement que l'URL contient deux variables server_name et cube_name à substituer, qu'il propose un modèle Dimension cohérent avec le pattern existant, et qu'il pose la question de l'URL encoding pour les noms de cubes avec espaces.

## Session du 15 mai 2026 — Semaine 4, exécution des phases 1 et 2 du PRD magic link

Cette session est la plus longue du parcours jusqu'ici. Elle couvre l'exécution 
de deux phases d'un PRD complexe sur l'authentification utilisateur, qui est 
aussi ma première vraie expérience de la méthode multi-phase plans.

### Conception du PRD avec contraintes métier IBM PA

La conception du PRD a fait apparaître plusieurs choix architecturaux 
importants. Plutôt que de recréer une authentification email plus password 
classique, j'ai choisi de m'appuyer sur le fait qu'IBM PA gère déjà ses 
utilisateurs via son système de rôles et d'API keys. Mon authentification 
PA-Explorer est donc volontairement légère : un magic link envoyé après 
vérification de l'allowlist et validation des credentials IBM PA.

Cette décision a été prise en dialogue avec mon assistant pédagogique 
Claude AI, et documentée dans decisions.md comme D-011. Elle s'inscrit 
dans une vision plus large de support multi-version V11 V12 documentée 
dans docs/roadmap/multi_version_support.md.

### Exécution de la phase 1, les fondations

La phase 1 a couvert la création des trois modèles User, UserSession, 
UserAllowlist plus le module de chiffrement Fernet et la fonction de 
validation des credentials IBM PA. C'était une session principalement de 
fondations sans endpoints exposés.

Le piège principal rencontré cette fois est venu de mon environnement et 
non de Claude Code. Le script reset_db.ps1 n'existait pas encore à la 
racine et il a fallu faire une suppression manuelle. Plus subtil, j'ai 
constaté que VS Code peut maintenir un verrou sur la base SQLite via 
son extension SQLite Viewer, ce qui peut faire échouer silencieusement 
les opérations de reset.

J'ai aussi découvert que VS Code SQLite Viewer affiche une seule table à 
la fois sans navigation visible vers les autres. J'ai dû créer un petit 
script de diagnostic check_db.py que j'ai rangé dans un nouveau dossier 
scripts à la racine pour vérifier l'état réel de la base. Ce dossier 
accueillera mes futurs scripts utilitaires.

### Exécution de la phase 2, les endpoints d'authentification

La phase 2 a livré les deux endpoints POST /auth/request et GET /auth/verify 
plus le quatrième modèle MagicLinkToken. C'est cette phase qui a rendu la 
feature visible et testable dans Swagger pour la première fois.

Trois pièges à retenir lors des tests Swagger. Le premier, les guillemets 
dans le JSON Swagger doivent être uniquement les guillemets de syntaxe 
JSON, pas des guillemets répétés dans les valeurs. J'avais collé mes 
credentials avec leurs guillemets, ce qui transmettait des chaînes avec 
guillemets à IBM PA. Le second, le copier-coller du token depuis l'URL 
complète peut tronquer le début du token. Il faut copier le token brut 
depuis la console uvicorn ou depuis la base. Le troisième, Swagger affiche 
la section Responses avec les codes possibles selon la spec, ce qui peut 
être confondu avec la réponse réelle qui est dans Server response.

### Apprentissages méthodologiques

Cette session m'a aussi appris que les PRDs en plusieurs phases sont un 
outil très puissant pour découper le travail. Chaque phase est validable 
indépendamment, ce qui permet de faire des pauses propres et de revenir 
sur le travail sans perdre le fil.

J'ai aussi consolidé deux nouveaux prompts dans prompts.md. Le P-005 sur 
la fidélité stricte aux sources, et le P-006 sur la correction de bug 
basée sur traceback. Ces deux prompts sont déjà réutilisables dans les 
semaines à venir.

### Pour la suite

Phase 3 du PRD à venir, qui ajoutera le middleware de protection des 
routes existantes. C'est cette phase qui va vraiment connecter 
l'authentification au reste du projet, en imposant qu'on ne puisse 
appeler les endpoints servers cubes dimensions qu'avec un cookie de 
session valide.

## Session du 15 mai 2026 

Compléter le route auth pour swagger

```bash
/api/v1/auth/request 
```
et mettre à jour les données sensibles

```json
{
  "email": "user@example.com",
  "ibm_pa_version": "V12",
  "credentials_payload": {
    "tenant_id": "ta-vraie-valeur-tenant",
    "api_key": "ta-vraie-valeur-api-key"
  }
}
```
puis lancer le commande pour afficher le token :

```python
python -c "import sqlite3; conn = sqlite3.connect('pa_explorer.db'); cursor = conn.cursor(); cursor.execute('SELECT token FROM magic_link_tokens ORDER BY created_at DESC LIMIT 1'); print(cursor.fetchone()[0]); conn.close()"
```

- Premièrement, un utilisateur dont l'email est dans l'allowlist peut soumettre ses credentials IBM PA via POST /auth/request. Le système valide les credentials contre IBM PA, génère un magic link sécurisé, et logge ce lien dans la console uvicorn.
- Deuxièmement, l'utilisateur peut utiliser le magic link via GET /auth/verify pour obtenir un cookie de session. Le système marque le token comme utilisé pour empêcher le rejeu, crée ou met à jour son enregistrement User, et établit une UserSession active pour 24 heures.

