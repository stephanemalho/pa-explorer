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
