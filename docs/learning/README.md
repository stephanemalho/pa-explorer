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

### ../context/conversational-ai/PROJECT_LEARNING_CONTEXT.md
Contexte synthétique à copier-coller dans une IA conversationnelle pour obtenir
des conseils d'apprentissage à jour sur PA-Explorer, ses accomplissements et les
prochaines étapes.

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

### REGLES-LIVRAISON-TM1.md
Référentiel métier des règles de livraison TM1 (promotion source vers cible)
via l'API REST OData. Source de vérité du cap PA-PROMOTE : ordre topologique,
règles objet par objet (dimensions, hiérarchies, éléments, cubes, règles,
vues, processus, chores), dry-run, aucune suppression implicite, et couche
multi-version V11/V12. À consulter avant toute feature de livraison.

### SUITE-PARCOURS-PA-PROMOTE.md
Plan des semaines 9 à 12 du parcours : transformation de PA-Explorer en app
desktop de livraison (Electron + Carbon + sidecar FastAPI), roadmap produit
M0 à M5, encadré VersionProvider et fils rouges de gouvernance. Prolonge le
parcours des semaines 1 à 8.

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
fil rouge. Le parcours se prolonge ensuite avec les semaines 9 à 12 
(cap « livraison PA-PROMOTE ») : PA-Explorer passe de la lecture d'un 
modèle IBM PA à la livraison d'objets TM1 d'un serveur source vers un 
serveur cible, sous la forme d'une app desktop téléchargeable. Le plan 
détaillé de cette suite vit dans `SUITE-PARCOURS-PA-PROMOTE.md`.

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

### Semaine 5 — Feedback Loops [TERMINÉE]
La question fondamentale "le code est-il bon marché ?" et son impact 
sur la philosophie de prototypage. Livrables réalisés : skill `do_work` 
(`docs/skills/do_work.md`) qui enseigne à Claude comment livrer proprement, 
suite de 51 tests pytest couvrant chiffrement, services cache 
(`ServerService`, `CubeService`, `DimensionService` avec fake IBM PA), 
`AuthService` et endpoints HTTP, infrastructure pytest partagée avec 
fixtures séparées par domaine, DB SQLite isolée par test, `TestClient` 
FastAPI branché sur `get_db` de test, trois techniques de mock maîtrisées 
(fausse classe, `patch`, `dependency_overrides`), décision D-014 documentée, 
et intégration d'Alembic pour la gestion du schéma (seed déplacé dans 
`scripts/seed_db.py`). Reportés volontairement à plus tard : ruff, 
pre-commit hooks, tests des dépendances de sécurité, endpoint logout.

### Semaine 6 — Pattern Ralph et tâches autonomes [EN_COURS]
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

### Semaine 9 — Fondations PA-PROMOTE : desktop shell et double connexion [À VENIR]
Bascule de la lecture à la livraison : PA-Explorer devient une app desktop 
qui promeut des objets TM1 d'un serveur source vers un serveur cible. 
Bootstrap d'une nouvelle surface Electron + React + IBM Carbon Design System 
au-dessus du backend FastAPI existant embarqué en sidecar, empaqueté en `.exe` 
(tracer bullet : l'app démarre, lance le sidecar, ping le health endpoint). 
Écran Connexions à deux serveurs source et cible avec sélecteur de version 
V11 ou V12. Introduction de la couche d'abstraction VersionProvider (V11 = 
Basic/CAM mode 5, V12 = OIDC/OAuth) et gap analysis du repo GitHub PA-PROMOTE, 
source d'inspiration. Décision D-016 figée.

### Semaine 10 — Exploration du modèle façon IBM PA [À VENIR]
Conception d'un PRD exécutable multi-phases pour l'explorateur d'objets, 
découpé sur plusieurs fenêtres de contexte, en réinvestissant le pattern 
feedback-loop de la semaine 5. Endpoints backend d'inventaire (cubes, 
dimensions, processus, chores et leurs enfants) via l'API OData avec 
cache-aside, UI arbre d'objets Carbon (TreeView, chargement paresseux, 
recherche, panneau de détail) « exactement comme sur IBM PA ». Tests des 
services d'inventaire avec un faux IBM PA et mise à jour de `ibm_pa.md`.

### Semaine 11 — Moteur de livraison : diff, dépendances, dry-run [À VENIR]
Le cœur technique et le plus risqué, mené en HITL strict avec revue de diff 
systématique car on touche à des opérations destructives potentielles. Module 
`app/promotion/` : diff source vers cible, graphe de dépendances et tri 
topologique selon l'ordre canonique du référentiel, validateur produisant un 
rapport de bloquants (par exemple un cube non livrable car ses dimensions 
manquent côté cible). Dry-run obligatoire, sans écriture. UI de plan de 
livraison. Chaque règle de `REGLES-LIVRAISON-TM1.md` couverte par au moins un 
test. Écriture du skill `add_promotion_rule`.

### Semaine 12 — Exécution, sécurité de déploiement, packaging et bilan [À VENIR]
Passage du prototype au livrable installable. Exécution ordonnée de la 
livraison de structure (barre de progression, arrêt/reprise, séparation stricte 
livraison ≠ exécution), piste données/sécurité minimale via processus TI 
(SaveDataAll et backup en pré-pull), journal d'audit consultable dans l'app, 
packaging `.exe` final. Écriture du skill `improve_my_codebase` et résorption 
de la dette ruff/pre-commit reportée de la semaine 5. Bilan réflexif : de la 
lecture PA-Explorer à la livraison PA-PROMOTE.

## Pour démarrer une nouvelle session de travail

1. Lire journal.md pour se replacer dans la chronologie
2. Vérifier le README à la racine du projet pour les commandes courantes
3. Lancer le serveur uvicorn et vérifier que tout démarre proprement
4. Continuer le travail là où on s'était arrêtés selon le journal
