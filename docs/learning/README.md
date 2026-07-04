# Documentation d'apprentissage — PA-Explorer

Ce dossier contient les notes structurées de mon parcours d'apprentissage 
Claude Code et de mon projet PA-Explorer. Il sert à la fois de journal 
de bord, de référentiel de concepts, de manuel de prompts, et d'historique 
des décisions architecturales.

Quand je reviens sur le projet après une pause, c'est ici que je commence.

## Structure des fichiers

### journal-perso/journal.md
Chronologie temporelle des sessions de travail. Chaque entrée datée 
contient ce qui a été accompli, les difficultés rencontrées, les surprises, 
et les leçons retenues. À lire pour se replacer dans le contexte du projet 
et comprendre la trajectoire d'apprentissage.

### harness/
Notes et référentiels de sources spécifiques à chaque harness IA.
Voir `harness/README.md` pour la structure.

### concepts.md
Notes synthétiques sur les concepts techniques découverts au fil du 
parcours, organisés par thème. Sections sur Python, FastAPI, SQLAlchemy, 
les patterns de cache, le format Parquet, l'authentification HTTP, etc. 
À consulter pour rafraîchir un concept précis sans avoir à parcourir 
toute la chronologie.

### ibm_pa.md
Référentiel métier sur l'API IBM Planning Analytics. Endpoints découverts, 
particularités d'authentification, structure des réponses, pièges connus, 
et concepts du domaine TM1 comme les cubes, dimensions, processus. À 
consulter pour toute question liée à IBM PA.

### decisions.md
Historique des décisions architecturales prises avec leur justification 
contextuelle. Permet de retrouver pourquoi tel ou tel choix a été fait 
quand on revient sur le code dans plusieurs mois. Chaque décision est 
datée et marquée comme définitive ou révisable.

### prompts.md
Collection des meilleurs prompts forgés au fil du parcours, avec leur 
note pédagogique. Sert de manuel de référence pour la composition de 
prompts efficaces avec Claude Code, au-delà du parcours d'apprentissage.

## Le parcours d'apprentissage complet

Le parcours suit une adaptation du programme AIhero "Claude Code for 
Real Engineers", étalé sur huit semaines à raison de quatre à six heures 
par semaine. L'objectif est de monter en compétence sur l'utilisation 
avancée de Claude Code tout en construisant PA-Explorer comme projet 
fil rouge.

### Semaine 1 — Prise en main de Claude Code [TERMINÉE]
Installation et configuration de Claude Code, gestion de session, 
prompts dans le terminal, intégration IDE, navigation dans l'historique, 
exécution de commandes bash, gestion fine des permissions. Mise en place 
du projet avec FastAPI, configuration .env multi-fichiers, premier 
endpoint health.

### Semaine 2 — Fondamentaux de Claude Code [TERMINÉE]
Contraintes des LLMs, exploration de codebase, subagents, construction 
d'une feature avec Plan Mode, boucle Plan-Execute-Clear. Première feature 
métier réelle de listing des serveurs TM1 avec authentification IBM PA, 
client httpx, pattern cache aside, gestion d'erreurs structurée.

### Semaine 3 — Steering avec Agents.md [TERMINÉE]
Création d'un fichier Agents.md ou CLAUDE.md qui devient le manuel 
d'utilisation de Claude Code sur ce projet. Principe de divulgation 
progressive de l'information. Découverte des skills et écriture du 
premier skill personnalisé. Configuration de la mémoire automatique.

### Semaine 4 — Planification de tâches complexes [TERMINÉE]
Comment attaquer des features massives sans se perdre. Écriture de PRDs 
exécutables par Claude Code. Découpage de features sur plusieurs fenêtres 
de contexte avec multi-phase plans. Pattern des tracer bullets pour 
valider une architecture avant l'investissement complet.

### Semaine 5 — Feedback Loops [EN_COURS]
La question fondamentale "le code est-il bon marché ?" et son impact 
sur la philosophie de prototypage. Construction d'un skill "Do Work" 
qui enseigne à Claude comment livrer proprement. Pre-commit hooks pour 
empêcher du code mal formaté. Application du Red-Green Refactor sur 
PA-Explorer. Mise en place d'une suite de tests pytest robuste avec 
mocks de l'API IBM PA. Migration vers Alembic pour la gestion du schéma 
de base de données. Premiers livrables réalisés : tests des services
cache `ServerService`, `CubeService`, `DimensionService` avec fake IBM PA,
puis infrastructure pytest partagée avec fixtures séparées par domaine,
DB SQLite isolée par test, et `TestClient` FastAPI branché sur `get_db`
de test.

### Semaine 6 — Pattern Ralph et tâches autonomes [À VENIR]
Découverte du pattern Ralph d'orchestration autonome où l'agent travaille 
en boucle sur un backlog. Comparaison HITL (Human In The Loop) versus 
AFK (Away From Keyboard). Mise en place d'un sandbox sécurisé pour les 
tâches AFK. Connexion de Claude Code à un backlog d'issues GitHub.

### Semaine 7 — Patterns Human In The Loop avancés [À VENIR]
Quand utiliser le Kanban et quand l'éviter. Écriture d'un skill Kanban. 
Recherche et prototypage assistés par Claude Code. Implémentation de la 
page de mapping des relations entre cubes, dimensions et processus dans 
PA-Explorer.

### Semaine 8 — Consolidation et codebase pour IA [À VENIR]
Conception d'un codebase que l'IA aime maintenir. Écriture d'un skill 
"Improve My Codebase". Conscience des modules dans le skill PRD. Bilan 
réflexif du parcours et préparation à l'intégration future d'agents IA 
dans PA-Explorer.

## Pour démarrer une nouvelle session de travail

1. Lire journal.md pour se replacer dans la chronologie
2. Vérifier le README à la racine du projet pour les commandes courantes
3. Lancer le serveur uvicorn et vérifier que tout démarre proprement
4. Continuer le travail là où on s'était arrêtés selon le journal
