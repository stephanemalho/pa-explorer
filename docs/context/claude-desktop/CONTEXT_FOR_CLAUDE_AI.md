# Contexte pour Claude AI assistant pédagogique

Ce fichier sert à remettre Claude AI dans le contexte de mon parcours
d'apprentissage Claude Code et de mon projet PA-Explorer au début d'une
nouvelle conversation. Je le copie-colle en début de session avec un
message qui dit "Voici le contexte de notre travail ensemble, lis-le
attentivement avant de me répondre".

## Le projet PA-Explorer

PA-Explorer est un POC backend pour IBM Planning Analytics on Cloud,
développé en Python avec FastAPI et SQLAlchemy. Il consomme l'API REST
TM1 d'IBM PA pour exposer des serveurs, cubes, dimensions et données
de cellules à un futur frontend BI assisté par IA.

L'environnement de développement est sur ma machine Windows avec un
tenant de démo IBM PA hébergé sur eu-central-1.planninganalytics.saas.ibm.com.
J'ai un siège Team chez Anthropic et le feu vert de mon entreprise pour
ce POC.

La vision long terme est un outil de monitoring de performance pour
analystes business, qui permet de naviguer dans les cubes TM1, de
saisir des chiffres, de comparer horizontalement avec l'historique et
verticalement avec les autres produits, et d'obtenir des analyses
automatiques d'anomalies via un agent IA.

## Mon profil d'apprentissage

Je suis développeur confirmé sur plusieurs langages avec des projets
conséquents derrière moi. Je suis débutant sur Python et FastAPI mais
j'apprends vite par analogie avec JavaScript et l'écosystème Node.

Je dispose de quatre à six heures par semaine pour ce projet, à un
rythme régulier sur huit semaines.

Mon objectif principal est de monter en compétence sur l'utilisation
avancée de Claude et Claude Code, avec le POC IBM PA comme support
d'apprentissage et livrable professionnel pour mon équipe.

## Le programme d'apprentissage

Le parcours suit une adaptation du programme AIhero "Claude Code for
Real Engineers", étalé sur huit semaines à raison de quatre à six
heures par semaine. Les semaines couvrent dans l'ordre la prise en
main de Claude Code, les fondamentaux, le steering avec Agents.md,
la planification, les feedback loops, le pattern Ralph, les patterns
HITL avancés, et la consolidation finale.

[CETTE SECTION EST À METTRE À JOUR À LA FIN DE CHAQUE SEMAINE]

État actuel : Semaine 2 terminée le 28 avril 2026.

Semaine 1 accomplie. Mise en place du projet, premier endpoint health,
configuration de base SQLite, gestion des credentials par env files.

Semaine 2 accomplie. Feature complète de listing des serveurs TM1
avec authentification IBM PA SaaS via apikey, client httpx, pattern
cache aside avec TTL configurable, gestion d'erreurs en sept types
d'exceptions métier, exposition de routes GET et POST avec Swagger.
Migration nécessaire vers Alembic en semaine 5 ou 6 pour gérer les
évolutions de schéma SQLAlchemy sans suppression de la base.

Semaine 3 à venir. Steering avec Agents.md, mémoire automatique de
Claude Code, premier skill personnalisé pour le projet.

## Mode de travail établi entre nous

Tu composes les prompts pour Claude Code avec une note pédagogique
au-dessus qui explique la logique du prompt. Je copie ces prompts
dans Claude Code et j'observe l'exécution.

Sur les décisions architecturales importantes, tu me poses des
questions plutôt que de décider seul, parce que je suis le seul
à connaître mon métier et mes utilisateurs cibles.

Je tiens un journal d'apprentissage dans docs/learning/ que je
maintiens à jour à la fin de chaque session.

Sur deux ou trois moments charnières du programme, notamment la
semaine 3 sur le steering, tu me feras composer un ou deux prompts
moi-même pour pratiquer sans en faire mon sujet quotidien.

## Décisions architecturales clés

Stack Python 3.12 avec FastAPI, SQLAlchemy synchrone, httpx pour les
appels API distants, pytest et pytest-asyncio prêts pour la semaine 5.

Cache à deux niveaux : SQLite via SQLAlchemy pour les métadonnées
relationnelles, Parquet à venir pour les données de cellules
volumineuses.

Authentification IBM PA SaaS via Basic Auth avec username "apikey"
littéral et clé API en password.

Gestion des erreurs en hiérarchie d'exceptions métier IBMPAError,
mappées vers des codes HTTP cohérents 502 503 504 par le router.

TTL de cache à 300 secondes en développement, à remonter en
production. Stratégie de rafraîchissement à trois couches, lecture
opportuniste avec TTL, préchauffage en arrière-plan pour les données
stables, refresh explicite par l'utilisateur via paramètre force_refresh.

Erreur stricte 503/504 si IBM PA est indisponible et cache expiré, à
revoir vers cache dégradé avec flag stale quand le frontend saura
afficher cet état visuellement.

## Pour démarrer une nouvelle session avec moi

Copie-colle le contenu complet de ce fichier en début de message,
puis ajoute ta question ou ta demande. Je lirai le contexte
attentivement et je reprendrai notre travail là où on s'était arrêté.