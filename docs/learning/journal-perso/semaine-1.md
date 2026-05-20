# Semaine 1 — Prise en main de Claude Code

La semaine 1 pose les fondations du projet et de la collaboration avec Claude Code :
installation de l'environnement Python, premier endpoint FastAPI, et découverte du
workflow de session. Les deux sessions couvrent le lancement du projet et une
rétrospective de fin de semaine qui prépare la semaine 2.

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
