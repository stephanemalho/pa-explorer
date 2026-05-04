# Décisions architecturales

Ce fichier garde la trace des décisions architecturales importantes prises 
au fil du projet, avec leur justification contextuelle. Chaque décision est 
datée et marquée comme définitive ou révisable. Quand je reviens sur le 
code dans plusieurs mois et que je me demande pourquoi tel choix a été 
fait, c'est ici que je trouve la réponse.

---

## D-001 — Stack technique principale [DÉFINITIVE]
Date : 22 avril 2026

### Décision
Python 3.12 avec FastAPI pour l'API REST, SQLAlchemy en mode synchrone 
pour l'ORM, SQLite en développement avec migration possible vers 
PostgreSQL en production, httpx pour les appels HTTP distants, pytest 
et pytest-asyncio pour les tests futurs.

### Justification
Python est l'écosystème dans lequel Claude Code excelle particulièrement, 
ce qui maximise la qualité de l'assistance IA pendant l'apprentissage. 
FastAPI génère automatiquement la documentation OpenAPI, ce qui réduit 
le travail de documentation manuelle. SQLAlchemy synchrone est plus 
simple à raisonner que la version async pour un débutant Python, et la 
migration vers async reste possible sans changer l'interface publique.

### Conséquences
Le développeur principal du projet doit accepter d'apprendre Python en 
parallèle du parcours Claude Code. Les analogies avec Node.js et 
TypeScript faciliteront la transition.

---

## D-002 — Séparation métadonnées et données [DÉFINITIVE]
Date : 28 avril 2026

### Décision
Les métadonnées du système (serveurs, cubes, dimensions, leurs relations) 
sont stockées dans la base relationnelle SQLite via SQLAlchemy. Les 
données volumineuses comme les ensembles de cellules seront stockées en 
fichiers Parquet dans un dossier dédié, avec une référence vers le fichier 
maintenue dans la base relationnelle.

### Justification
Les métadonnées et les données ont des caractéristiques fondamentalement 
différentes. Les métadonnées sont relationnelles, peu volumineuses, 
relativement stables, et se prêtent au SQL. Les données de cellules sont 
multidimensionnelles, volumineuses, fréquemment requêtées de manière 
sélective, et bénéficient massivement du format columnar Parquet pour 
la compression et la lecture sélective.

Le format Parquet est aussi le format de prédilection pour passer des 
données à un LLM dans une forme compacte et structurée, ce qui prépare 
l'intégration future d'agents IA dans PA-Explorer.

### Alternatives écartées
MongoDB a été considéré pour les données de cellules. Écarté parce que 
les données TM1 sont structurellement homogènes (matrices numériques), 
ce qui ne tire aucun parti du modèle document de MongoDB et perd la 
compression columnar de Parquet.

### Statut
Métadonnées implémentées en semaine 2. Stockage Parquet à mettre en 
place en semaine 4 ou 5 selon le rythme du parcours.

---

## D-003 — Stratégie de cache à trois couches [DÉFINITIVE]
Date : 28 avril 2026

### Décision
Le cache des données IBM PA est géré selon une stratégie hybride en 
trois couches.

Couche 1 : cache aside avec TTL configurable. Quand une route est appelée, 
le service vérifie si la donnée existe en base et si son TTL est valide. 
Sinon, il appelle IBM PA, met à jour la base, et sert la donnée fraîche.

Couche 2 : préchauffage en arrière-plan pour les données stables. Les 
métadonnées qui changent peu pourront être rafraîchies périodiquement par 
un job en arrière-plan, indépendamment des requêtes utilisateur.

Couche 3 : rafraîchissement explicite par l'utilisateur via un paramètre 
force_refresh ou un endpoint POST refresh dédié.

### Justification
IBM PA ne propose pas de webhook ou de notifications poussées, donc le 
modèle event-driven naïf est impossible. Une stratégie hybride combine 
fraîcheur garantie sur demande, rapidité de réponse via cache, et 
contrôle utilisateur quand nécessaire.

### Statut
Couche 1 implémentée en semaine 2 avec TTL de 300 secondes en 
développement. Couches 2 et 3 partiellement présentes (couche 3 via 
force_refresh), à enrichir si besoin.

---

## D-004 — Authentification IBM PA SaaS [DÉFINITIVE]
Date : 28 avril 2026

### Décision
L'authentification contre l'API IBM Planning Analytics SaaS utilise un 
HTTP Basic Auth avec la chaîne littérale "apikey" comme username et la 
clé API utilisateur comme password.

### Justification
Cette convention est documentée par IBM pour les déploiements MCSP 
(Multi-Cloud Subscription Platform). Les premières tentatives avec 
l'email utilisateur en username échouaient avec une erreur 
AuthorizedConnectionFailed.

### Statut
Implémenté en semaine 2 dans la classe IBMPAClient via 
httpx.BasicAuth("apikey", api_key).

---

## D-005 — Erreur stricte si IBM PA indisponible [RÉVISABLE]
Date : 28 avril 2026

### Décision
Si IBM PA est indisponible et que le cache est expiré, l'API retourne 
une erreur stricte avec code HTTP 503 ou 504 selon le cas, plutôt qu'un 
cache dégradé avec flag stale.

### Justification
À ce stade du projet, il n'existe pas encore de frontend qui sache 
afficher visuellement un état stale à l'utilisateur. Servir des données 
expirées sans avertissement visible serait une trahison silencieuse. 
L'erreur stricte est la posture honnête tant que l'interface ne peut 
pas signaler l'état du cache.

### Conditions de révision
Cette décision sera revisitée quand le frontend BI sera en place et 
qu'il pourra afficher un badge stale, probablement en semaine 8 ou au 
moment de l'intégration du frontend React.

---

## D-006 — TTL de cache à 300 secondes en développement [RÉVISABLE]
Date : 28 avril 2026

### Décision
Le TTL par défaut du cache des serveurs est fixé à 300 secondes (5 
minutes) en environnement de développement.

### Justification
Cette valeur permet d'observer le cycle complet d'expiration et de 
rafraîchissement plusieurs fois dans une même session de travail, ce qui 
est précieux pédagogiquement. Une valeur plus longue comme 3600 secondes 
empêcherait d'observer le comportement.

### Conditions de révision
À remonter en production vers 3600 secondes ou plus selon la fréquence 
réelle de changement des serveurs côté IBM PA.

---

## D-007 — Pas de tests pytest en semaine 2 [DÉFINITIVE]
Date : 28 avril 2026

### Décision
Aucun test pytest n'est écrit en semaine 2 sur la feature des serveurs. 
Un squelette de dossier tests avec __init__.py et conftest.py est créé 
pour matérialiser l'intention de tester en semaine 5.

### Justification
Le pattern de test pertinent (mock IBMPAClient via dependency_overrides, 
SQLite en mémoire, httpx.MockTransport) nécessite trois concepts qui 
seront couverts ensemble en semaine 5. Écrire des tests incomplets 
maintenant créerait de la dette technique ou de la fausse confiance.

### Statut
Squelette créé. Tests réels à écrire en semaine 5.

---

## D-008 — Champ raw_data en JSON brut sur le modèle [DÉFINITIVE]
Date : 28 avril 2026

### Décision
Le modèle Server contient un champ raw_data de type Text qui stocke le 
JSON brut tel que retourné par l'API IBM PA. Ce champ coexiste avec les 
champs typés explicites comme display_name, host, http_port, etc.

### Justification
Cette redondance est volontaire et applique le pattern schema-on-read. 
Les champs typés permettent les requêtes BI rapides et la validation 
Pydantic. Le raw_data permet d'absorber les évolutions de l'API IBM PA 
sans migration de schéma, et fournit la matière brute pour passer aux 
LLMs en semaine 8.

### Statut
Implémenté en semaine 2.

---

## D-009 — Gestion git en branche unique main [DÉFINITIVE pour ce projet]
Date : 26 avril 2026

### Décision
Tout le travail est fait directement sur la branche main. Aucune branche 
de feature, aucune branche par semaine.

### Justification
Le développement est solo, le projet est un POC d'apprentissage, et la 
complexité supplémentaire des branches n'apporte aucun bénéfice à ce 
stade. La discipline cible est plutôt de faire des commits propres et 
atomiques avec des messages descriptifs.

### Conditions de révision
Si un collègue rejoint le projet, ou si une feature risquée justifie 
une isolation, on basculera vers un workflow de branches feature.