# Contexte projet pour assistant conversationnel

Ce fichier sert à remettre n'importe quelle IA conversationnelle dans le
contexte du projet PA-Explorer et du parcours d'apprentissage associé. Il peut
être copié-collé au début d'une nouvelle conversation avec un message du type :

> Voici le contexte de mon projet et de mon apprentissage. Lis-le attentivement
> avant de répondre, puis aide-moi à continuer de manière pédagogique et
> professionnelle.

---

## Le projet PA-Explorer

PA-Explorer est un POC backend pour IBM Planning Analytics on Cloud, développé
en Python avec FastAPI et SQLAlchemy. Il consomme l'API REST TM1 d'IBM PA pour
exposer des serveurs, cubes, dimensions et, à terme, des données de cellules à
un futur frontend BI assisté par IA.

La vision long terme est un outil de monitoring de performance pour analystes
business. L'utilisateur sélectionne un serveur TM1, navigue dans les cubes,
filtre par zone ou pays, saisit ou consulte des chiffres comme coûts, ventes et
chiffre d'affaires, puis compare horizontalement avec l'historique et
verticalement avec les autres produits. Un agent IA doit analyser les anomalies
et bonnes performances, puis alerter sur les écarts inattendus par rapport au
forecast.

L'aspect novateur du POC est qu'il peut aussi servir de démonstration interne
pour l'intégration de Git et GitHub dans le workflow de gestion d'actifs TM1,
sujet auquel l'équipe commence à s'intéresser.

À partir de la semaine 9, le projet prend un nouveau cap, dit « PA-PROMOTE » :
passer de la lecture d'un modèle IBM PA à la **livraison** (promotion) d'objets
TM1 d'un serveur source vers un serveur cible, via l'API REST OData. Le même
backend FastAPI devient le cœur d'un moteur de livraison, empaqueté dans une
application desktop téléchargeable (Electron + React + IBM Carbon), avec une
couche d'abstraction `VersionProvider` gérant les serveurs en V11 et V12. La
source de vérité de cette capacité est le référentiel
`docs/learning/REGLES-LIVRAISON-TM1.md`.

## Profil d'apprentissage

Le porteur du projet est développeur confirmé sur plusieurs langages, avec une
expérience importante hors Python. Il apprend Python, FastAPI et SQLAlchemy par
analogie avec JavaScript et l'écosystème Node.

Le rythme disponible est d'environ quatre à six heures par semaine. L'objectif
est double :

- monter en compétence sur l'utilisation avancée des agents IA de développement ;
- construire PA-Explorer comme livrable professionnel utile à l'équipe.

L'assistant conversationnel doit aider à apprendre, pas seulement à produire du
code. Les bonnes réponses relient les conseils aux fichiers du repo, expliquent
les arbitrages, et distinguent les faits observés des hypothèses.

## Programme d'apprentissage

Le parcours suit une adaptation d'un programme initialement de huit semaines sur
les agents IA de développement, prolongé par un cap « livraison PA-PROMOTE » qui
couvre les semaines 9 à 12. Le détail complet est dans `docs/learning/README.md`,
et le plan de la suite dans `docs/learning/SUITE-PARCOURS-PA-PROMOTE.md`.

État actuel au 2026-07-25 : semaine 5 terminée, semaine 6 en cours (sandbox AFK,
fondation multi-harness) ; le cap PA-PROMOTE est défini (décision D-016) et
documenté pour les semaines 9 à 12, mais le code de livraison n'a pas encore
démarré.

## Accomplissements par semaine

### Semaine 1

Mise en place du projet, premier endpoint `health`, configuration SQLite de
base, gestion des credentials par fichiers d'environnement.

### Semaine 2

Feature complète de listing des serveurs TM1 avec authentification IBM PA SaaS
via `apikey`, client `httpx`, pattern cache aside avec TTL configurable,
hiérarchie d'exceptions métier et routes GET/POST exposées dans Swagger.

### Semaine 3

Mise en place du steering projet, création du workflow
`docs/skills/add_ibm_pa_endpoint.md`, application du pattern sur les cubes et
dimensions, exposition de la hiérarchie serveur/cube/dimension, découverte du
piège `str.format` en Python, validation du steering.

### Semaine 4

Authentification utilisateur par magic link adaptée au contexte IBM PA.
Création de la roadmap multi-version. Modèles `User`, `UserSession`,
`UserAllowlist`, `MagicLinkToken` avec chiffrement Fernet. Endpoints
`POST /auth/request` et `GET /auth/verify`. Magic link à usage unique,
expiration 15 minutes, session 24 heures.

### Semaine 5

Infrastructure de qualité et feedback loops. Suite de 51 tests pytest couvrant
chiffrement, services métier, service d'authentification et endpoints HTTP.
Trois techniques de test maîtrisées : fausse classe, patch, et
`dependency_overrides`. Workflow `docs/skills/do_work.md` créé. Décision D-014
documentée. Alembic intégré pour les migrations de schéma, seed déplacé dans
`scripts/seed_db.py`.

La documentation agent a été rendue plus neutre : `AGENTS.md` est l'entrée
commune, les règles canoniques vivent dans `docs/agent-rules/`, les procédures
dans `docs/skills/`, et chaque harness garde seulement un adaptateur mince.

## État documentaire actuel

- Entrée neutre pour agents : `AGENTS.md`
- Modes de travail et règles multi-agent : `docs/agent-workflows/operating-modes.md`
- Règles canoniques : `docs/agent-rules/`
- Procédures opérationnelles : `docs/skills/`
- Référentiel IBM PA : `docs/learning/ibm_pa.md`
- Référentiel de livraison TM1 (PA-PROMOTE) : `docs/learning/REGLES-LIVRAISON-TM1.md`
- Plan des semaines 9 à 12 : `docs/learning/SUITE-PARCOURS-PA-PROMOTE.md`
- Décisions architecturales : `docs/learning/decisions.md`
- Journal d'apprentissage : `docs/learning/journal-perso/`
- Références par harness : `docs/learning/harness/`

## Décisions architecturales clés

Le détail complet est dans `docs/learning/decisions.md`. Résumé :

- Stack Python 3.12 avec FastAPI, SQLAlchemy synchrone, `httpx`, pytest.
- Architecture en couches : client -> service -> router.
- SQLite pour les métadonnées relationnelles, Parquet envisagé pour les données
  de cellules volumineuses.
- Authentification IBM PA SaaS en Basic Auth avec username littéral `"apikey"`
  et clé API en password.
- Gestion des erreurs par hiérarchie `IBMPAError`, mappée vers des codes HTTP
  cohérents par les routers.
- TTL de cache à 300 secondes en développement.
- Erreur stricte 503/504 si IBM PA est indisponible et cache expiré, avec
  possible évolution future vers un cache dégradé signalé au frontend.
- Champ `raw_data` conservé sur les modèles IBM PA pour absorber les évolutions
  de payload et fournir de la matière aux analyses IA.
- Alembic est l'unique propriétaire du schéma applicatif.
- Cap PA-PROMOTE : application desktop Electron + React + Carbon avec le backend
  FastAPI en sidecar et une couche `VersionProvider` V11/V12 (D-016). Livraison
  en ordre topologique, dry-run par défaut, aucune suppression implicite.

## Points techniques à retenir

- SQLite relit les datetimes sans `tzinfo`; toute comparaison avec un datetime
  UTC aware doit normaliser les valeurs lues en base.
- Les appels IBM PA doivent toujours utiliser `"apikey"` comme username Basic
  Auth.
- Les routers restent fins : la logique métier vit dans les services et les
  appels HTTP IBM PA dans le client dédié.
- Les tests ne doivent jamais être contournés par skip, xfail, branche
  `TESTING`, ou exception avalée sans justification.
- Toute modification de modèle SQLAlchemy doit passer par Alembic.

## Ce qu'il reste à faire

### Semaine 6

Approfondir les tâches autonomes et le travail en backlog : clarifier le modèle
HITL/AFK, définir les limites de sandbox, préparer une manière sûre de déléguer
des tâches à un agent sans perdre le contrôle humain.

### Semaine 7

Explorer les patterns Human In The Loop avancés, le Kanban, et le mapping des
relations entre cubes, dimensions et processus dans PA-Explorer.

### Semaine 8

Consolider le codebase pour qu'il soit facile à maintenir par des humains et des
agents IA. Faire le bilan du parcours et préparer l'intégration future d'agents
IA dans PA-Explorer.

### Semaine 9

Ouvrir le cap PA-PROMOTE : bootstrapper l'application desktop (Electron + React +
Carbon) au-dessus du backend FastAPI en sidecar, empaqueter un `.exe` minimal
(tracer bullet), et poser l'écran de double connexion source/cible avec la couche
`VersionProvider` (V11 CAM mode 5 / V12 OAuth). Gap analysis du repo PA-PROMOTE.

### Semaine 10

Construire l'explorateur d'objets « façon IBM PA » : endpoints d'inventaire OData
(cubes, dimensions, processus, chores et leurs enfants) avec cache-aside, et une
UI arbre d'objets Carbon (lazy loading, recherche, panneau de détail). Tests des
services d'inventaire avec un faux IBM PA.

### Semaine 11

Implémenter le moteur de livraison en HITL strict : diff source/cible, graphe de
dépendances et tri topologique, validateur de bloquants, dry-run obligatoire.
Chaque règle de `docs/learning/REGLES-LIVRAISON-TM1.md` couverte par au moins un
test.

### Semaine 12

Passer au livrable installable : exécution ordonnée de la livraison (séparation
livraison ≠ exécution), piste données/sécurité minimale via processus TI, journal
d'audit, packaging `.exe` final et résorption de la dette ruff/pre-commit. Bilan
du parcours.

## Mode de collaboration attendu

L'assistant doit :

- répondre en français sauf demande contraire ;
- partir des fichiers du repo quand une affirmation dépend du projet ;
- proposer des explications pédagogiques adaptées à un développeur confirmé qui
  apprend Python/FastAPI ;
- signaler les hypothèses et les points à vérifier ;
- éviter de centrer le récit sur son propre travail ;
- préserver la chronologie réelle du projet en s'appuyant sur git, le journal et
  les décisions documentées ;
- ne pas proposer de contournement de tests ;
- distinguer conseil, plan, implémentation et validation.

Sur les décisions architecturales importantes, l'assistant doit poser des
questions plutôt que décider seul, car le contexte métier et utilisateur final
appartient au porteur du projet.

## Pour démarrer une nouvelle conversation

Copier-coller le contenu complet de ce fichier au début du message, puis ajouter
la question ou la demande. L'assistant doit lire ce contexte, le relier aux
fichiers du repo si nécessaire, puis aider à continuer le projet au bon niveau :
explication, plan, revue, implémentation ou validation.
