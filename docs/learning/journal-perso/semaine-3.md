# Semaine 3 — Steering avec CLAUDE.md

La semaine 3 consolide le steering de Claude Code via CLAUDE.md et étend l'API avec
les entités cubes et dimensions. Trois sessions couvrent la mise en place du fichier
de pilotage, l'intégration de la route des cubes, et la découverte des skills personnalisés.

---

## Session du 4 mai 2026 — Semaine 3, création du CLAUDE.md et teste de steering

Session du début de semaine 3. Création du CLAUDE.md consolidé en 
français à la racine du projet, suppression du CONTEXT_FOR_CLAUDE_CODE.md 
devenu redondant. Premier test de steering réussi sur la consultation 
de decisions.md à propos du choix de SQLite. Observation importante : 
Claude Code lit bien les fichiers indiqués dans CLAUDE.md, mais peut 
compléter ses réponses avec des inférences raisonnables qui ne sont 
pas littéralement dans les sources. Pour les sujets où la fidélité 
compte, prévoir d'ajouter une consigne explicite dans le prompt.

---

## Session du 11 mai 2026 — Intégration de la route GET /api/v1/servers/{server_name}/cubes

### Apprentissages techniques

Mise en évidence d'une limitation de str.format en Python : la méthode 
ne prend pas en charge le formatage partiel, contrairement à ce que 
l'on pourrait supposer intuitivement. Point à retenir pour les 
développements futurs.

### Fonctionnement de Claude Code et gestion de l'historique

Activation automatique de la commande /compact durant la session. À 
cette occasion, j'ai identifié que Claude Code conserve l'historique 
des conversations dans le répertoire suivant.
C:\Users\smalho.claude\projects\c--Users-smalho-Desktop-pa-explorer

Il y stocke l'historique des discussions même après le compact. Il 
est possible de retrouver l'historique complet d'un projet.

J'ai aussi remarqué quelque chose d'intéressant. Claude crée un 
dossier .claude dans mon répertoire Utilisateurs, et il garde 
l'entièreté des discussions avant compact. Après le compact, Claude 
m'a explicitement indiqué.

> If you need specific details from before compaction (like exact 
> code snippets, error messages, or content you generate) read the 
> full transcript at: C:\Users\smalho\.claude\projects\c--Users-smalho-Desktop-pa-explorer\1dbc581c-4ea4-46b7-b946-20337976817b.jsonl

Donc il est possible de retrouver un historique complet des 
discussions, même si le format jsonl n'est pas très lisible pour un 
humain. Reste à déterminer s'il est nécessaire de nettoyer ce 
répertoire lors de la suppression d'un projet, ou si une purge 
périodique est requise pour éviter une croissance excessive du 
dossier .claude dans le temps.

### Découverte de la richesse métier IBM PA

Je viens de découvrir que mon tenant Seminaire contient des cubes 
avec une vraie complexité métier TM1. Le cube Categories Salaires 
a des règles de calcul TurboIntegrator complètes, des feeders 
auto-générés, des dimensions multiples qui apparaissent dans les 
règles comme annee, phase, categories_salaires, mois, salaires. 
J'ai aussi des attributs comme Caption qui donnent un nom 
d'affichage en anglais Salary categories.

Cette richesse ouvre énormément de portes pour la suite du projet. 
On pourra un jour exposer ces règles dans un éditeur, visualiser 
les dépendances entre cubes via les feeders, suivre les dates de 
mise à jour pour détecter les changements. Mais on ne fera pas 
tout cela maintenant, sinon on perdrait le cap.

### Commandes Claude Code

Taper le symbole / seul affiche l'autocomplétion avec la liste 
complète des commandes disponibles dans la version actuelle. 
C'est la méthode la plus rapide pour découvrir les fonctionnalités.

---

## Session du 12 mai 2026 — Attente des actions de claude suite à un settup de skills

Je m'attends à ce que Claude Code consulte add_ibm_pa_endpoint.md sans qu'on lui demande, qu'il identifie correctement que l'URL contient deux variables server_name et cube_name à substituer, qu'il propose un modèle Dimension cohérent avec le pattern existant, et qu'il pose la question de l'URL encoding pour les noms de cubes avec espaces.
