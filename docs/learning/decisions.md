# Décisions architecturales

Ce fichier garde la trace des décisions architecturales importantes prises 
au fil du projet, avec leur justification contextuelle. Chaque décision est 
datée et marquée comme définitive ou révisable. Quand je reviens sur le 
code dans plusieurs mois et que je me demande pourquoi tel choix a été 
fait, c'est ici que je trouve la réponse.

<!--
MODÈLE — Nouvelle décision architecturale

## D-XXX — [Titre court] [DÉFINITIVE | RÉVISABLE]
Date : YYYY-MM-DD

### Décision
[Décision prise, exprimée en une à deux phrases.]

### Justification
[Pourquoi ce choix a été retenu, avec le contexte de l'époque.]

### Conséquences
[Ce que cette décision implique pour le développement futur.]

### Conditions de révision
[Dans quelles circonstances ce choix pourrait être remis en question.
"Définitive" si le choix est irréversible ou structurant à long terme.]
-->

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

---

## D-010 — verify_magic_link sans transaction atomique [DETTE TECHNIQUE — RÉVISABLE]
Date : 15 mai 2026

### Décision
La méthode `AuthService.verify_magic_link` effectue trois opérations
séquentielles sans transaction englobante : (1) marquage du token comme
utilisé (`used_at`), (2) upsert de l'utilisateur, (3) création de la
session. Un crash entre les étapes laisserait la base dans un état
partiellement cohérent.

### Justification
Sur SQLite en développement local, le risque est négligeable et la
complexité d'une gestion transactionnelle explicite (savepoints, rollback
partiel) n'est pas justifiée pour un POC solo. SQLAlchemy autorise les
transactions explicites via `db.begin()` mais l'implémentation actuelle
s'appuie sur l'autocommit implicite de chaque `db.commit()`.

### Conséquences
Si le serveur crashe entre l'étape 1 et l'étape 3, le token est marqué
`used_at` mais aucune session n'est créée. L'utilisateur doit relancer
une demande de magic link. Ce comportement est acceptable en POC.

### Conditions de révision
Avant tout déploiement en production ou migration vers PostgreSQL, wrapper
les trois opérations dans une transaction unique :
```python
with self._db.begin():
    token.used_at = ...
    # upsert user
    # create session
```
La méthode `create_or_update_user` devra ne plus appeler `db.commit()`
pour que le commit soit délégué à la transaction parente.

---

## D-011 — Authentification utilisateur par magic link sans password [DÉFINITIVE]
Date : 15 mai 2026

### Décision
PA-Explorer n'implémente pas de système d'authentification utilisateur 
avec email plus password. À la place, le système utilise un magic link 
envoyé après vérification que l'email est dans une allowlist et que 
les credentials IBM PA fournis sont valides.

### Justification
IBM PA gère déjà l'authentification utilisateur via son propre système 
de rôles et d'API keys. Recréer un système d'authentification dans 
PA-Explorer ferait doublon et introduirait des problèmes de 
synchronisation. Le magic link sert uniquement à identifier la session 
PA-Explorer, en s'appuyant sur le fait que la personne a déjà été 
authentifiée par IBM via la génération de son API key.

L'allowlist permet de contrôler qui peut utiliser l'application sans 
créer un système complet de gestion d'utilisateurs.

### Conséquences
Les credentials IBM PA sont stockées chiffrées en base, associées à 
l'email de l'utilisateur. La validité de ces credentials est vérifiée 
à chaque appel via la gestion existante des exceptions IBMPAAuthError.

---

## D-012 — Chiffrement Fernet des credentials utilisateur [DÉFINITIVE]
Date : 15 mai 2026

### Décision
Les credentials IBM PA des utilisateurs sont chiffrées avec Fernet 
(bibliothèque cryptography) avant stockage en base. La clé de 
chiffrement PA_EXPLORER_ENCRYPTION_KEY est stockée dans .env.local.

### Justification
Stocker des api_keys en clair en base serait une mauvaise pratique de 
sécurité, même pour un POC, parce que cela créerait une mauvaise 
habitude. Fernet offre un chiffrement symétrique robuste avec rotation 
de clé possible plus tard.

### Conséquences
La perte de PA_EXPLORER_ENCRYPTION_KEY rend toutes les credentials 
chiffrées illisibles. La base doit alors être réinitialisée.

### Conditions de révision
En production, prévoir une stratégie de rotation de clé et de backup 
sécurisé documentée. Investiguer aussi les solutions de gestion de 
secrets comme HashiCorp Vault ou AWS Secrets Manager.

---

## D-013 — Allowlist d'emails pour le contrôle d'accès [DÉFINITIVE pour le POC]
Date : 15 mai 2026

### Décision
Le contrôle d'accès à PA-Explorer se fait via une table 
UserAllowlist qui liste les emails autorisés à demander un magic link. 
Un email administrateur initial est pré-peuplé via la variable 
PA_EXPLORER_INITIAL_ADMIN_EMAIL.

### Justification
Cette approche minimaliste permet de contrôler qui peut utiliser le 
système sans créer un mécanisme complet de gestion de rôles. Elle est 
extensible vers des rôles ou des permissions plus fins si nécessaire.

### Conditions de révision
Si PA-Explorer évolue vers un usage multi-tenants ou avec une vraie 
gestion d'équipes, l'allowlist sera remplacée par un système de 
permissions plus structuré.

## D-014 — Instanciation directe d'IBMPAClient dans validate_ibm_pa_credentials [EXCEPTION RECONNUE]
Date : 23 mai 2026

### Décision
La méthode statique validate_ibm_pa_credentials dans 
app/services/auth_service.py instancie directement un IBMPAClient avec 
les credentials passées en paramètres, sans utiliser Depends. C'est une 
violation apparente de la convention C-1 du skill do_work, mais elle 
est acceptée comme exception justifiée.

### Justification
La méthode est appelée pendant le flow POST /auth/request, avant que 
l'utilisateur ne soit authentifié et avant qu'une session existe. Les 
credentials sont fournies dans la requête HTTP. À ce stade, il n'y a 
pas encore d'utilisateur à qui rattacher un client via Depends. Le 
client est créé spécifiquement pour valider ces credentials et n'est 
pas réutilisé après.

L'alternative serait de faire que le router POST /auth/request 
instancie le client et le passe en paramètre à 
validate_ibm_pa_credentials. Cela serait plus cohérent architecturalement 
mais introduirait une complexité supplémentaire dans le router pour un 
gain marginal.

### Conséquences
Le skill do_work continuera de signaler cette ligne lors de l'audit 
architectural via grep. C'est attendu et acceptable. Le signal sert 
de rappel que cette exception existe.

### Conditions de révision
Si d'autres cas similaires émergent où un client doit être créé hors 
contexte d'authentification, revoir la stratégie pour éventuellement 
introduire une factory pattern ou une dépendance contextuelle.

---

## D-015 — Fixtures pytest séparées par domaine [DÉFINITIVE]
Date : 13 juin 2026

### Décision
L'infrastructure de tests pytest est organisée avec un `conftest.py`
minimal et des modules de fixtures spécialisés sous `tests/fixtures/`.
`conftest.py` prépare les variables d'environnement avant les imports
applicatifs puis charge les fixtures via `pytest_plugins`.

Les fixtures de base de données et de client FastAPI vivent dans
`tests/fixtures/database.py`. Les factories liées à l'authentification
vivent dans `tests/fixtures/auth.py`.

### Justification
Le premier jet centralisait toutes les fixtures dans `conftest.py`, ce
qui rendait le fichier trop volumineux et mélangeait plusieurs
responsabilités. La séparation par domaine rend l'infrastructure plus
lisible, plus DRY, et plus facile à étendre pendant la semaine 5.

La DB de test utilise SQLite en mémoire avec `StaticPool` afin que le
`TestClient` FastAPI et la session SQLAlchemy du test partagent la même
base isolée. Chaque test recrée ses tables et nettoie les dependency
overrides FastAPI après exécution.

### Conséquences
Les nouveaux tests doivent réutiliser les fixtures existantes plutôt que
recréer manuellement une session SQLAlchemy, un utilisateur, une session
ou un magic link dans chaque fichier.

Si une nouvelle famille de fixtures grossit, créer un module dédié sous
`tests/fixtures/` plutôt que d'allonger `conftest.py`.
