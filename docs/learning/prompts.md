# Manuel de prompts

Ce fichier collectionne les prompts forgés ou utilisés pendant le 
parcours, avec leur note pédagogique. Il sert de manuel de référence 
pour la composition de prompts efficaces avec Claude Code, au-delà du 
parcours d'apprentissage.

Chaque entrée présente le contexte, le prompt complet, et l'analyse de 
ce qui en fait sa qualité.

---

## P-001 — Premier prompt d'amorçage du projet
Contexte : Semaine 1, prise en main de Claude Code, mise en place 
initiale du projet PA-Explorer.

### Le prompt
"Je veux créer une API backend en Python avec FastAPI et SQLAlchemy 
pour interagir avec IBM Planning Analytics. Peux-tu d'abord explorer 
ce dossier, puis me proposer une structure de projet minimale avec 
juste un endpoint de santé, une configuration de base de données 
PostgreSQL, et un fichier README qui explique comment démarrer ? Ne 
code rien encore, propose-moi d'abord le plan."

### Analyse pédagogique
Ce prompt illustre trois principes fondamentaux. Premièrement, demander 
l'exploration avant l'action permet à Claude de s'imprégner du contexte. 
Deuxièmement, le périmètre est clairement défini avec des éléments 
précis et limités. Troisièmement, la garde explicite "Ne code rien 
encore" prépare le réflexe du Plan Mode qui sera formalisé en semaine 2.

---

## P-002 — Prompt de planification riche en Plan Mode
Contexte : Semaine 2, conception de la feature de listing des serveurs 
TM1 avec authentification IBM PA, cache aside et gestion d'erreurs.

### Le prompt
Le prompt complet est trop long pour être reproduit ici, voir le 
journal de la session du 28 avril 2026 pour le texte intégral. La 
structure générale couvrait neuf sections explicites :
1. Compréhension de la demande
2. Recherche documentaire avec citation des sources
3. Arborescence des fichiers
4. Schéma SQLAlchemy détaillé
5. Contrats des fonctions et méthodes
6. Énumération exhaustive des cas d'erreur
7. Recommandation sur la stratégie de tests
8. Plan de validation manuelle pas à pas
9. Questions ouvertes et points à arbitrer

### Analyse pédagogique
Ce prompt est un modèle de prompt en Plan Mode pour une feature 
architecturalement structurante. Les éléments qui en font la qualité.

L'ancrage dans l'existant via la référence au CODEBASE_TOUR.md évite 
à Claude de repartir de zéro et préserve le travail de contexte déjà 
fait.

Le partage de l'expérience préalable (tentative Postman ratée avec 
erreur AuthorizedConnectionFailed) oriente Claude vers les bonnes 
recherches documentaires plutôt que vers des hypothèses naïves.

Les contraintes architecturales explicites (séparation client/service, 
injection de dépendance, cache aside avec TTL) donnent un cadre précis 
qui empêche les dérives.

La structure de réponse en neuf sections force Claude à couvrir 
exhaustivement les dimensions du problème plutôt que de produire un 
plan superficiel.

La garde finale de Plan Mode strict empêche toute exécution prématurée.

### Variation utile
Pour des features moins structurantes, on peut simplifier en réduisant 
les sections à 4 ou 5 plutôt que 9. Le principe à conserver est de 
toujours forcer la pensée explicite avant l'action.

---

## P-003 — Prompt de correction de bug avec hypothèse précise
Contexte : Semaine 2, correction du bug 500 sur l'endpoint servers 
quand force_refresh=false. Le bug venait d'une comparaison datetime 
naive versus aware liée à SQLite qui ne supporte pas les timezones.

### Le prompt
"Bug à corriger sur la feature servers.

Symptôme observable. L'endpoint GET /api/v1/servers retourne un 
Internal Server Error 500 quand force_refresh=false. Quand 
force_refresh=true, l'endpoint répond correctement avec un 200.

Ce que j'ai vérifié.
- Les données en base SQLite sont correctes, raw_data contient bien du 
  JSON valide
- La construction d'un ServerResponse en isolation fonctionne, j'ai 
  testé via une commande python -c
- Le bug se produit donc uniquement dans le chemin du cache

Mon hypothèse principale est que la fonction _get_cached_servers compare 
un datetime avec timezone à un datetime sans timezone, ce qui lève une 
TypeError. SQLite ne stocke pas les timezones nativement.

Diagnostique le bug, corrige-le proprement, et explique-moi en deux 
phrases ce qui se passait. Pas de plan en amont, exécute directement."

### Analyse pédagogique
Ce prompt illustre le mode direct opposé au Plan Mode. Quand le 
diagnostic est déjà bien avancé et que la correction est circonscrite, 
imposer un plan ralentirait inutilement.

Les éléments qui en font la qualité.

La distinction explicite entre symptôme observable et hypothèse 
préserve l'autonomie de jugement de Claude. Il peut confirmer 
l'hypothèse ou la rejeter selon ce qu'il trouve.

L'énumération des vérifications déjà effectuées évite à Claude de 
refaire le travail de diagnostic en isolation.

La demande d'une explication courte en deux phrases force la 
pédagogie au lieu d'une simple correction silencieuse.

La phrase "Pas de plan en amont, exécute directement" assume le mode 
direct sans ambiguïté.

---

## P-004 — Prompt d'évolution mineure sans plan
Contexte : Semaine 2, ajout des trois champs accepting_clients, href 
et is_v12 au modèle des serveurs après découverte de leur présence dans 
les réponses IBM PA.

### Le prompt
"Bug à corriger sur la feature servers.

Symptôme. Les colonnes accepting_clients, href et is_v12 sont créées 
en base et déclarées dans le schéma Pydantic, mais elles restent à 
null dans la réponse API alors que les valeurs correspondantes sont 
présentes dans raw_data avec les clés AcceptingClients, Href et isV12.

Cause probable. Le mapping dans _refresh_from_ibm_pa du ServerService 
n'a pas été mis à jour pour extraire ces trois champs depuis raw vers 
les colonnes de l'objet Server.

Diagnostique et corrige proprement. Pas de plan en amont, exécute 
directement."

### Analyse pédagogique
Variante du P-003 pour une évolution fonctionnelle plutôt qu'une 
correction de bug. Le pattern reste le même, symptôme plus hypothèse 
plus instruction.

À retenir, plus le diagnostic est partagé en amont, plus Claude peut 
aller vite et juste. Les prompts vagues comme "ça ne marche pas, 
répare" produisent des allers-retours coûteux. Les prompts qui 
partagent l'effort de réflexion produisent des réponses précises.

---

## Principes généraux de composition de prompts

Au fil du parcours, plusieurs principes émergent des prompts qui 
fonctionnent.

L'ancrage dans l'existant. Toujours faire référence à ce qui est déjà 
en place pour éviter que Claude redémarre à zéro.

L'explicitation des contraintes. Préciser les choix architecturaux 
attendus, les bibliothèques à utiliser, les patterns à respecter.

Le partage du contexte. Donner ce qu'on a déjà appris ou essayé pour 
éviter à Claude de refaire le chemin.

La structure de réponse demandée. Plus le prompt est riche, plus la 
structure de réponse attendue doit être explicite.

La garde sur l'exécution. Pour les features structurantes, toujours 
demander un plan validable avant action. Pour les corrections 
circonscrites, le mode direct est plus efficace.

L'ouverture aux questions. Inviter Claude à poser des questions plutôt 
que de faire des hypothèses silencieuses, surtout en début de feature.

## P-005 — Prompt de fidélité stricte aux sources
Contexte : Semaine 3, après avoir constaté que Claude Code complète parfois 
ses réponses avec des inférences raisonnables non sourcées dans les fichiers 
qu'il consulte. Pour les questions où la fidélité aux sources est critique, 
comme une revue de décisions architecturales ou la recherche d'un précédent, 
ce prompt impose une discipline stricte.

### Le prompt
"Pour répondre à ma question, consulte uniquement [nom du fichier ou des 
fichiers]. Réponds strictement à partir de ce qui y est écrit littéralement, 
sans inférer ni compléter avec des raisonnements qui ne sont pas dans le 
texte. Si l'information demandée ne figure pas explicitement dans les 
sources, indique-le clairement plutôt que de combler le vide.

Voici ma question : [question]"

### Analyse pédagogique
Ce prompt traite un comportement spécifique de Claude Code, qui consiste à 
formuler des réponses convaincantes en mêlant contenu sourcé et extrapolations 
raisonnables. Pour la plupart des situations, ce comportement est utile parce 
qu'il enrichit les réponses. Mais quand tu cherches à valider une décision 
historique, à retrouver un précédent, ou à auditer une architecture, tu as 
besoin de pouvoir distinguer ce qui est documenté de ce qui est inféré.

Les éléments qui en font la qualité.

L'instruction "réponds strictement à partir de ce qui y est écrit 
littéralement" pose explicitement le contrat de fidélité.

L'instruction "sans inférer ni compléter" nomme directement le comportement 
indésirable, ce qui aide Claude à le supprimer.

L'instruction "indique-le clairement" prévient le faux positif, c'est-à-dire 
le cas où Claude complète parce qu'il a peur de paraître insuffisant.

À retenir, ce prompt est utile pour les revues, audits, et questions sur 
l'historique du projet. Pour les questions de conception ou les nouvelles 
features, l'inférence raisonnable est au contraire utile et il ne faut pas 
la brider.