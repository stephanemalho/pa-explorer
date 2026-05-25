# Semaine 4 — Planification de tâches complexes

La semaine 4 a été la plus dense et la plus formatrice du parcours jusqu'ici. 
Elle a couvert l'implémentation complète d'un système d'authentification 
multi-utilisateur via un PRD découpé en trois phases, exécuté sur plusieurs 
sessions Claude Code distinctes.

C'est aussi la première fois que j'ai travaillé sur une feature qui dépasse 
une session unique de contexte. Le découpage en phases indépendantes est 
l'apprentissage central de la semaine, distinct de l'apprentissage technique 
sur l'authentification.

À la fin de la semaine, les trois phases du PRD magic link sont terminées 
et le système d'authentification est entièrement opérationnel.

---

## Apprentissage méthodologique majeur, les PRDs multi-phase

Un PRD pour Claude Code n'est pas le même type de document qu'un PRD produit 
classique. Il combine trois dimensions, la dimension métier qui décrit ce 
que la feature apporte, la dimension technique qui décrit comment elle 
s'implémente, et la dimension exécutoire qui permet à Claude Code de 
l'utiliser comme une feuille de route.

Le PRD doit être structuré pour qu'une session de Claude Code puisse charger 
uniquement la phase qu'elle exécute, sans avoir besoin de tout le contexte. 
Chaque phase doit être autonome et vérifiable indépendamment, ce qui permet 
de découper le travail sur plusieurs sessions sans dépendance bloquante. La 
phase 1 ne dépend pas de la phase 2 pour être testable, et la phase 2 ne 
dépend pas de la phase 3.

Le PRD ne contient pas de code. Il décrit l'intention, les phases, les 
livrables et les critères de validation. Cette absence de code est importante 
parce qu'elle laisse à Claude Code la liberté de prendre des décisions 
d'implémentation contextualisées à chaque session.

Les critères de validation explicites par phase sont essentiels. Sans eux, 
Claude Code peut considérer comme finie une phase qui ne l'est pas réellement. 
J'ai listé entre cinq et huit critères par phase pour forcer une vérification 
rigoureuse.

---

## Décision architecturale clé, authentification adaptée au contexte IBM PA

Plutôt que de recréer un système d'authentification email plus password 
classique, j'ai choisi de m'appuyer sur le fait qu'IBM PA gère déjà ses 
utilisateurs via son système de rôles et d'API keys. Mon authentification 
PA-Explorer est donc volontairement légère, un magic link envoyé après 
vérification de l'allowlist et validation des credentials IBM PA.

Cette décision a été prise en dialogue avec mon assistant pédagogique Claude 
AI, et documentée dans decisions.md comme D-011. Elle s'inscrit dans une 
vision plus large de support multi-version V11 V12 documentée dans 
docs/roadmap/multi_version_support.md.

Le modèle de session utilisateur a été pensé dès la conception pour accueillir 
plus tard des credentials de natures différentes selon la version IBM PA. Le 
champ credentials_encrypted en JSON chiffré arbitraire permet cette flexibilité.

---

## Phase 1, les fondations sans endpoints exposés

La phase 1 a couvert quatre modèles SQLAlchemy nouveaux User, UserSession, 
UserAllowlist, MagicLinkToken. Les trois premiers ont été créés en phase 1, 
le quatrième en phase 2. Plus le module de chiffrement Fernet et la fonction 
de validation des credentials IBM PA.

Le concept de seed initial a été découvert pendant cette phase. Faire un seed 
signifie pré-remplir une base de données avec des données initiales au 
démarrage de l'application. Sans seed initial sur UserAllowlist, je serais 
bloqué dehors de mon propre système après chaque reset de base. La fonction 
_seed_allowlist dans le lifespan FastAPI s'exécute une fois au démarrage et 
ajoute PA_EXPLORER_INITIAL_ADMIN_EMAIL à la table si absent. L'opération est 
idempotente.

Le piège SQLite déjà connu en semaine 2 sur les datetimes naive versus aware 
s'est manifesté à nouveau dans la validation d'expiration des sessions. La 
normalisation via expires_at.replace(tzinfo=timezone.utc) est devenue un 
pattern récurrent dans tout le code lié à l'authentification.

---

## Phase 2, génération et validation du magic link

La phase 2 a livré les deux endpoints d'authentification proprement dits plus 
le quatrième modèle MagicLinkToken. C'est cette phase qui a rendu la feature 
visible et testable dans Swagger pour la première fois.

Le pattern de sécurité par non-divulgation a été appliqué sur POST /auth/request. 
La même réponse 200 avec un message générique est retournée que l'email soit 
dans l'allowlist ou non. Cela empêche un attaquant de découvrir qui est 
inscrit dans le système. Le même principe s'applique sur GET /auth/verify 
avec un message d'erreur unique pour tous les cas d'échec.

L'utilisation de secrets.token_urlsafe(32) pour générer les tokens est la 
bonne pratique cryptographique. 32 octets donnent 256 bits d'entropie, ce 
qui est largement suffisant pour résister aux attaques par force brute.

Le caractère à usage unique du magic link est garanti par le champ used_at 
qui passe de null à un timestamp lors de la première utilisation. Toute 
tentative ultérieure avec le même token est rejetée par la vérification du 
champ.

J'ai aussi découvert ou redécouvert trois pièges lors des tests Swagger qui 
sont à retenir.

Premier piège, les guillemets dans le JSON Swagger doivent être uniquement 
les guillemets de syntaxe JSON, pas des guillemets répétés dans les valeurs. 
J'avais collé mes credentials avec leurs guillemets, ce qui transmettait des 
chaînes avec guillemets à IBM PA.

Deuxième piège, le copier-coller du token depuis l'URL complète peut tronquer 
le début du token. Il faut copier le token brut depuis la console uvicorn ou 
depuis la base via le script utilitaire get_magic_link_token.py.

Troisième piège, Swagger affiche la section Responses avec les codes possibles 
selon la spec, ce qui peut être confondu avec la réponse réelle qui est dans 
Server response. Apprendre à distinguer les deux sections est essentiel pour 
comprendre ce qui se passe vraiment.

---

## Phase 3, protection des routes par middleware

La phase 3 a introduit le concept de dépendance d'authentification FastAPI. 
En FastAPI, on ne met pas du code d'authentification dans chaque route. À 
la place, on crée une fonction de dépendance qui vérifie l'authentification 
et que toutes les routes protégées injectent via Depends. Cette approche 
évite la duplication et garantit la cohérence.

La fonction get_current_user dans app/security/dependencies.py lit le cookie 
session_token de la requête, vérifie sa validité en base, met à jour 
last_used_at pour suivre l'activité, et retourne l'utilisateur authentifié. 
Si la session est invalide ou absente, elle lève HTTPException 401 que 
FastAPI transforme automatiquement en réponse HTTP correcte.

Le message d'erreur 401 est volontairement unique pour tous les cas, "Session 
invalide ou expirée". Donner un message d'erreur précis comme "Cookie absent" 
ou "Session expirée" pourrait aider un attaquant à comprendre la structure 
de l'authentification. C'est le même principe de non-divulgation que pour 
POST /auth/request.

Le concept le plus important de cette phase est celui du client IBM PA scopé 
par utilisateur. Avant la phase 3, mon IBMPAClient était instancié au 
démarrage avec les credentials du fichier .env.local. Toutes les routes 
utilisaient le même client partagé. Après la phase 3, chaque requête 
authentifiée construit un IBMPAClient avec les credentials spécifiques de 
l'utilisateur de la session. Concrètement, chaque utilisateur appelle IBM PA 
avec ses propres clés, pas avec une clé partagée. C'est ce qui rend mon 
système vraiment multi-utilisateur.

La fonction get_ibm_pa_client_for_user prend l'utilisateur authentifié en 
dépendance via Depends(get_current_user), déchiffre ses credentials avec 
Fernet, et construit un IBMPAClient avec ces credentials spécifiques. C'est 
ce client scopé qui est ensuite injecté dans les services existants comme 
ServerService, CubeService et DimensionService.

La modification des routers existants servers, cubes et dimensions a été 
propre. Le pattern de remplacement consiste à substituer la dépendance 
client par get_ibm_pa_client_for_user et à supprimer l'ancienne fonction 
get_ibm_pa_client locale qui devient morte. Les services n'ont pas changé 
puisqu'ils prennent déjà un IBMPAClient en paramètre de constructeur.

La phase 3 a aussi introduit la gestion du cas 501 Not Implemented pour la 
version V11 d'IBM PA. Si un utilisateur a ibm_pa_version="V11" dans sa 
session, get_ibm_pa_client_for_user lève 501 avec un message clair. Cela 
prépare proprement le support futur V11 sans bloquer le développement actuel 
en V12.

Tous les critères de validation de la phase 3 ont été validés. GET /api/v1/servers 
sans cookie retourne 401. Le flow complet POST /auth/request puis GET /auth/verify 
puis GET /api/v1/servers retourne la liste des serveurs TM1 de l'utilisateur 
authentifié avec ses propres credentials. Un cookie falsifié retourne 401.

---

## Rôle pivot de la clé Fernet dans toute la chaîne

PA_EXPLORER_ENCRYPTION_KEY est utilisée à trois moments critiques du flow 
d'authentification.

Premier moment, lors de POST /auth/request, le service chiffre les credentials 
utilisateur avant de les stocker dans magic_link_tokens.

Deuxième moment, lors de GET /auth/verify, les credentials chiffrées sont 
copiées du magic_link_token vers la table users, toujours chiffrées avec la 
même clé.

Troisième moment, lors de chaque appel aux routes protégées, la fonction 
get_ibm_pa_client_for_user déchiffre les credentials de l'utilisateur pour 
construire le client IBM PA scopé.

Sans cette clé Fernet, personne ne peut lire les credentials stockées. C'est 
ce qui rend mon système sûr contre une fuite de la base. Si je perds ou 
modifie cette clé, toutes les credentials existantes deviennent illisibles 
et la base doit être réinitialisée.

---

## Pièges environnementaux rencontrés

Plusieurs pièges Windows et venv ont causé des pertes de temps qu'il faut 
retenir.

L'oubli de pip install après mise à jour de requirements.txt a fait planter 
uvicorn avec une erreur sur email_validator manquant. La règle à retenir, 
après tout pull Git ou modification de requirements.txt, toujours faire 
pip install -r requirements.txt avant de relancer uvicorn.

Le script reset_db.ps1 n'existait pas encore et il a fallu faire la 
suppression manuelle de pa_explorer.db. Le script utilitaire a été créé 
pendant la semaine pour automatiser cette procédure récurrente.

VS Code SQLite Viewer peut verrouiller la base et faire échouer silencieusement 
les opérations de reset. Le piège est connu et la parade est de fermer les 
onglets pa_explorer.db avant tout reset.

VS Code SQLite Viewer affiche une seule table à la fois sans navigation 
visible vers les autres. J'ai dû créer le script check_db.py rangé dans le 
dossier scripts pour vérifier l'état réel de la base. Ce dossier accueillera 
mes futurs scripts utilitaires.

---

## Évolution de la documentation

CLAUDE.md a été drastiquement allégé de plus de 200 lignes à environ 30 
lignes. Le nouveau fichier est une vraie table des matières annotée qui 
pointe vers les fichiers spécialisés. Cela économise du contexte à chaque 
démarrage de session Claude Code, et cela permet d'enrichir les fichiers 
spécialisés sans que CLAUDE.md grossisse hors de contrôle.

Quatre nouvelles décisions architecturales ont été ajoutées dans decisions.md, 
D-010 sur la dette transactionnelle de verify_magic_link, D-011 sur le choix 
du magic link sans password, D-012 sur le chiffrement Fernet, D-013 sur 
l'allowlist.

Le document docs/roadmap/multi_version_support.md a été créé pour documenter 
la vision long terme sur le support V11 V12 sans bloquer l'implémentation 
actuelle qui reste sur V12 uniquement.

Le journal.md original a été restructuré en plusieurs fichiers par semaine 
dans docs/learning/journal-perso/ pour faciliter la navigation et la 
relecture sélective.

---

## Pour la suite

La semaine 5 commence sur les feedback loops et les tests pytest. C'est une 
semaine de qualité plutôt que de fonctionnalité, mais elle est essentielle 
pour la robustesse du projet. Je pourrai d'ailleurs appliquer les tests sur 
le système d'authentification que je viens de construire en semaine 4.

Plusieurs points sont à reprendre en semaine 5 notamment la migration de 
l'envoi du magic link vers email réel via Mailtrap, l'installation d'Alembic 
pour les migrations propres, et l'ajout d'un endpoint logout pour permettre 
la déconnexion explicite.

La dette technique notée en D-010 sur l'atomicité transactionnelle de 
verify_magic_link reste à traiter avant tout déploiement en production.

Un test de steering sur une nouvelle machine MacBook a validé en début de 
semaine 5 que la documentation du projet est suffisamment claire pour 
permettre à Claude Code de se mettre en contexte sans intervention humaine. 
C'est la confirmation que l'investissement documentaire des semaines 3 et 4 
a porté ses fruits.