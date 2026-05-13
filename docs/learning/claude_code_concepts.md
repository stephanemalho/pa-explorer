# Notes sur Claude Code — PA-Explorer

Ce fichier regroupe les observations, comportements à connaître, et patterns 
de collaboration spécifiques à Claude Code. Il est complémentaire de 
concepts.md qui couvre les concepts techniques de la stack Python.

Chaque section est issue d'observations faites au cours du parcours 
d'apprentissage, datées quand c'est pertinent. Les informations issues 
de la documentation officielle Anthropic sont signalées comme telles.

---

## Steering avec CLAUDE.md et skills personnalisés

Le steering est l'ensemble des mécanismes qui permettent de donner à 
Claude Code un cadre de référence persistant entre les sessions. 
L'objectif est de transformer Claude Code d'un assistant généraliste 
en spécialiste du projet sur lequel il travaille.

### Le fichier CLAUDE.md à la racine du projet

Claude Code lit automatiquement le fichier CLAUDE.md à la racine du 
dépôt à chaque démarrage de session. Ce fichier contient les 
conventions du projet, les patterns architecturaux à respecter, les 
pièges connus, et les références vers d'autres documents de 
spécification. Sans avoir à le copier-coller à chaque conversation, 
Claude Code a accès à ce contexte en début de session.

Dans PA-Explorer, CLAUDE.md est rédigé en français et couvre la 
stack technique, l'architecture en couches client service router 
model schema, les patterns en place comme le cache aside avec TTL, 
les conventions strictes, et les pièges Windows.

### Mémoire explicite et mémoire implicite

Claude Code maintient deux types de mémoire qui se complètent.

La mémoire explicite vit dans les fichiers que le développeur 
maintient manuellement, comme CLAUDE.md pour les conventions du 
projet, ou ~/.claude/CLAUDE.md pour les préférences utilisateur 
globales. Cette mémoire est sous contrôle total du développeur, qui 
décide ce qui doit être retenu et comment.

La mémoire implicite, appelée auto-memory, est capturée 
automatiquement par Claude Code au fil des sessions. Elle observe les 
interactions et retient les préférences récurrentes sans intervention 
explicite. Cette mémoire est stockée dans un dossier dédié sous 
.claude et peut être consultée ou modifiée via la commande 
slash memory.

Pour un projet d'apprentissage avancé, la mémoire explicite est 
préférée parce qu'elle permet un contrôle conscient de ce que Claude 
Code utilise comme contexte. La mémoire implicite peut être laissée 
active en arrière-plan pour capturer des préférences utiles, mais elle 
ne doit pas être la source principale du steering.

### Les skills personnalisés

Un skill est un fichier markdown qui formalise une procédure 
réutilisable. Quand le développeur demande une tâche correspondant au 
skill, Claude Code consulte le fichier et suit la procédure 
documentée. Cela garantit la cohérence du traitement entre différentes 
sessions et différentes entités similaires.

Dans PA-Explorer, le skill add_ibm_pa_endpoint dans docs/skills 
décrit en dix étapes la procédure d'ajout d'un nouvel endpoint IBM 
PA. Il a été utilisé avec succès pour list_cubes en semaine 3 et 
pour list_dimensions en validation du steering, avec des résultats 
cohérents qui confirment la valeur de l'investissement initial.

---

## Comportements de Claude Code à connaître

Cette section regroupe les observations faites au fil du parcours sur 
le fonctionnement de Claude Code, qui ne sont pas dans la 
documentation officielle mais qui sont utiles à connaître pour bien 
collaborer avec l'outil.

### Inférence raisonnable

Claude Code complète ses réponses avec des extrapolations cohérentes 
mais non sourcées dans les fichiers qu'il consulte. Quand il lit un 
fichier comme decisions.md et qu'on lui demande une information 
précise, il restitue fidèlement le contenu mais ajoute parfois des 
raisonnements logiques qui ne sont pas littéralement dans le texte. 

Cette inférence est utile pour la plupart des situations parce 
qu'elle enrichit les réponses, mais elle peut être problématique 
quand on cherche à valider une décision historique précise. Pour 
forcer la fidélité stricte aux sources, utiliser le prompt P-005 
documenté dans prompts.md.

Observation initiale faite en semaine 3 session une, lors d'un test 
de consultation de decisions.md à propos du choix SQLite. Claude Code 
avait restitué la justification correctement mais avait ajouté trois 
raisons pratiques qui n'étaient pas dans le fichier source, et une 
affirmation sur des intentions architecturales croisées entre 
décisions D-003 et D-008 qui n'était pas explicite dans les fichiers.

### Compact automatique du contexte

Quand le contexte d'une session sature, Claude Code lance 
automatiquement un compact qui résume l'historique pour libérer de 
l'espace. Cette opération peut prendre plusieurs minutes sur des 
sessions riches. Pendant le compact, Claude Code reste accessible 
mais inactif. Une fois terminé, il dispose d'un résumé textuel de la 
session au lieu de l'historique brut.

Important. L'historique complet avant compact reste stocké dans 
C:\Users\{user}\.claude\projects\{project_path}\{session_id}.jsonl. 
Ce fichier au format JSONL peut être consulté manuellement si besoin 
de retrouver un détail précis perdu lors du compact. Le format est 
peu lisible pour un humain mais reste parsable.

Pour des sessions très longues, le développeur peut anticiper en 
lançant manuellement un compact avec slash compact à un moment qui 
lui convient, plutôt que d'attendre le déclenchement automatique qui 
peut survenir au mauvais moment.

### Limitations de str.format en Python

Découverte lors de la session deux de la semaine 3 sur list_cubes. 
La méthode str.format en Python ne fait pas de format partiel. Si une 
chaîne template contient plusieurs variables à substituer et qu'on 
n'en fournit qu'une, Python lève KeyError sur les variables 
manquantes.

Cela invalide l'approche naïve consistant à enchaîner deux .format 
sur la même chaîne pour substituer progressivement les variables. La 
solution est de fournir toutes les variables dans un seul appel via 
kwargs. C'est ce qui a motivé la généralisation de la méthode _url 
dans le client IBMPAClient pour accepter des kwargs additionnels.

Le prompt de correction utilisé pour ce bug est documenté en P-006 
dans prompts.md.

### Exploration parallèle par agents

Observé lors du test de steering avec list_dimensions en session 
trois de la semaine 3. Pour explorer un codebase, Claude Code peut 
lancer plusieurs agents en parallèle qui se répartissent les fichiers 
à analyser. Un agent peut être chargé d'explorer les patterns client 
et service pendant qu'un autre explore les routers schemas et 
configuration.

Cette parallélisation accélère significativement la phase 
d'exploration sur des projets de taille moyenne. Elle est déclenchée 
automatiquement par Claude Code quand il juge que la tâche s'y prête, 
sans intervention manuelle du développeur.

---

## Commandes Claude Code utiles

### slash help et exploration des commandes

Dans les versions récentes de Claude Code, slash help redirige vers 
la documentation web plutôt que d'afficher la liste des commandes 
dans le terminal. Pour explorer rapidement les commandes disponibles, 
taper slash seul affiche l'autocomplétion avec la liste complète. 
C'est la méthode la plus rapide pour découvrir les fonctionnalités 
disponibles dans sa version.

### slash memory

Ouvre l'interface de gestion de la mémoire avec trois options. 
Project memory ouvre CLAUDE.md à la racine du projet. User memory 
ouvre ~/.claude/CLAUDE.md global. Open auto-memory folder ouvre le 
dossier contenant les apprentissages automatiques de Claude Code.

### slash clear

Vide la conversation en cours et repart sur un contexte propre. 
Utile quand on veut basculer sur un sujet complètement différent ou 
quand on a fait beaucoup d'expérimentations et qu'on veut repartir 
sur des bases nettes.

### slash compact

Lance manuellement le compact du contexte. Préférable au compact 
automatique parce qu'on peut choisir le moment qui convient plutôt 
que de subir un blocage au milieu d'une tâche urgente.

### slash init

Génère une trame initiale de CLAUDE.md basée sur l'analyse du projet 
en cours. Utile au démarrage d'un nouveau projet pour avoir une base 
à enrichir.

---

## Patterns de collaboration efficaces

Cette section documente les patterns de travail avec Claude Code qui 
ont fait leurs preuves dans le projet PA-Explorer.

### Plan Mode pour les features architecturales

Pour toute feature qui touche à l'architecture, c'est-à-dire qui 
crée de nouveaux fichiers, modifie plusieurs couches, ou introduit 
un nouveau pattern, démarrer en Plan Mode avec Shift+Tab ou via le 
prompt explicite. Ce mode empêche Claude Code de modifier le code 
tant que le plan n'est pas validé, ce qui permet de discuter 
l'architecture en amont.

### Mode direct pour les corrections circonscrites

Pour une correction de bug avec diagnostic précis, le mode direct 
est plus efficace que le Plan Mode. Le diagnostic partagé en amont 
suffit à cadrer Claude Code, et la planification serait redondante.

### Validation manuelle par approbation d'édits

Quand Claude Code exécute un plan validé, la validation manuelle 
des édits via Yes and manually approve edits permet d'observer 
chaque action en direct. C'est plus lent que l'auto-accept mais 
beaucoup plus formateur pour comprendre comment Claude Code 
implémente les patterns.

### Référence aux skills par convention de prompt

Quand un skill existe pour une tâche, mentionner explicitement le 
nom du skill dans le prompt. Par exemple cette feature suit le 
pattern habituel d'ajout d'un endpoint IBM PA garantit que Claude 
Code consultera add_ibm_pa_endpoint.md. Sans cette mention, il 
pourrait improviser au lieu d'appliquer le pattern documenté.

---

## Limites observées et contournements

### Limites d'usage par session

Les limites d'usage de Claude peuvent interrompre une session en 
plein milieu d'une tâche, ce qui s'est produit pendant la semaine 3 
session deux. Pour minimiser l'impact, conserver une habitude de 
commit fréquent permet de reprendre facilement au point d'arrêt.

Quand la limite est atteinte, sauvegarder l'état du travail dans le 
journal et reprendre plus tard avec un prompt contextuel qui rappelle 
où on s'est arrêté. Les fichiers learning et CONTEXT_FOR_CLAUDE_AI 
sont précieux pour ces reprises.

### Désynchronisation entre plan et exécution

Parfois Claude Code propose un plan validé puis exécute différemment, 
notamment sur des détails techniques fins comme le double format 
chaîné qui ne marche pas. La parade est de relire le code généré 
avant validation finale et de comparer aux intentions du plan.

### Logs uvicorn invisibles sous PowerShell Windows

Spécifique à l'environnement Windows. Les logs HTTP d'uvicorn ne 
s'affichent pas toujours dans le terminal PowerShell. Pour déboguer, 
préférer le navigateur direct sur les URLs et observer les réponses 
HTTP. Le terminal peut quand même afficher les tracebacks d'exceptions 
non gérées, donc cela reste utile en cas de 500.