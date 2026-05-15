# PRD — Authentification utilisateur par magic link

**Statut** : Rédigé — en attente d'implémentation  
**Date** : 15 mai 2026  
**Cible** : semaine 4 du parcours d'apprentissage  
**Auteur** : Stéphane Malho

---

## 1. Contexte et motivation

### Situation actuelle

PA-Explorer n'a aucun système d'authentification utilisateur. Les
credentials IBM Planning Analytics — `IBM_PA_API_KEY` et
`IBM_PA_TENANT_ID` — sont stockés en variables d'environnement
globales dans `.env.local`. Chaque appel à l'API IBM PA utilise
ces credentials uniques, quel que soit l'appelant.

Cette architecture convient à un POC mono-utilisateur, mais elle
présente deux limites bloquantes pour la suite du parcours.

Premièrement, elle empêche tout usage multi-utilisateur. Si deux
analystes business accèdent à PA-Explorer, ils partagent la même
api_key et le même tenant, sans isolation ni traçabilité.

Deuxièmement, elle ne prépare pas le support multi-version IBM PA
prévu en semaines 5 à 8 (cf. `docs/roadmap/multi_version_support.md`).
En V11 on-premise, les credentials ne sont pas une api_key mais un
couple host/port avec un mode d'authentification variable. Cette
diversité ne peut pas être absorbée par des variables d'environnement
fixes.

### Objectif de la feature

Introduire un système d'authentification légère sans mot de passe,
adapté au contexte SaaS, dans lequel chaque utilisateur fournit ses
propres credentials IBM PA et est identifié par son email. Le magic
link est le mécanisme de vérification de l'email : l'utilisateur
reçoit un lien à usage unique et clique dessus pour activer sa session.

Une fois authentifié, chaque appel de l'utilisateur aux routes
protégées utilise ses propres credentials IBM PA, déchiffrés depuis
sa session persistante.

### Lien avec la roadmap multi-version

Le modèle de session conçu dans ce PRD anticipe le support V11/V12.
Les credentials sont stockés dans un champ JSON chiffré dont la
structure varie selon la version IBM PA ciblée par l'utilisateur. Seul
le cas V12 est implémenté maintenant, mais la structure est extensible
sans migration de schéma.

---

## 2. Périmètre

### Ce que ce PRD couvre

- Stockage sécurisé des credentials IBM PA par utilisateur, avec
  chiffrement Fernet symétrique.
- Génération et validation d'un magic link à usage unique avec
  expiration de 15 minutes.
- Création d'une session HTTP par cookie, valide 24 heures.
- Protection des routes existantes `/servers`, `/cubes`, `/dimensions`
  qui exigent une session valide.
- Résolution des credentials depuis la session pour instancier
  IBMPAClient par utilisateur.

### Ce que ce PRD ne couvre pas

- L'adaptateur multi-version V11/V12 — la structure de session
  l'anticipe, mais l'implémentation est dans la roadmap semaines 5-8.
- L'interface frontend de saisie du formulaire — ce PRD définit les
  endpoints backend. Les formulaires HTML restent hors scope.
- L'envoi d'email réel — en développement, le lien est loggé dans la
  console uvicorn. L'intégration d'un service d'email (Mailtrap,
  SendGrid, SES) est prévue en semaine 5 (cf. section 11).
- La révocation de session ou la déconnexion explicite — couvert dans
  une itération ultérieure.

---

## 3. Contraintes architecturales

Ces contraintes sont héritées des décisions documentées dans
`docs/learning/decisions.md` et de la vision `docs/roadmap/multi_version_support.md`.
Elles s'imposent à l'implémenteur et ne sont pas négociables dans le
cadre de ce PRD.

**C-1 — Flexibilité des credentials (multi-version)**  
Le modèle de session doit stocker des credentials de natures différentes
selon la version IBM PA ciblée. Pour V12 SaaS : `tenant_id` et `api_key`.
Pour V11 on-premise (futur) : `host`, `port`, `auth_mode`, et selon le
mode soit `username`+`password`, soit un CAM passport. La structure doit
être flexible dès maintenant même si seul le cas V12 est implémenté.

**C-2 — Stack synchrone**  
SQLAlchemy synchrone, FastAPI synchrone — pas d'`async/await` dans
les handlers ni dans les services. Cohérent avec D-001.

**C-3 — Séparation stricte des couches**  
La logique d'authentification suit le pattern établi :
client / service / model / schema / router. Pas de logique métier dans
les routers. Les dépendances FastAPI sont injectées via `Depends`.

**C-4 — Datetimes UTC avec SQLite**  
Les datetimes stockés dans SQLite sont naïfs. Appliquer
`.replace(tzinfo=timezone.utc)` au point de lecture pour la comparaison,
comme dans `server_service.py` existant.

---

## 4. Flow d'authentification

Le flow est un magic link en deux étapes, suivi d'une session cookie.

### Étape A — Soumission des credentials

L'utilisateur appelle `POST /api/v1/auth/request` avec son email, sa
version IBM PA cible, et ses credentials (au minimum tenant_id et
api_key pour V12).

Le système crée ou met à jour l'utilisateur en base. Les credentials
sont sérialisés en JSON et chiffrés avec Fernet avant persistence.

Un token `MagicLinkToken` est généré via `secrets.token_urlsafe(32)`.
Il est associé à l'utilisateur avec une expiration de 15 minutes.

Le lien de vérification est loggé dans la console uvicorn via le
logger Python standard (niveau INFO), de façon à pouvoir le copier
pendant les tests. Aucune réponse JSON ne contient le token — la
réponse HTTP est toujours un 200 avec un message générique.
L'envoi par email réel est prévu en début de semaine 5 (cf. section 11).

### Étape B — Validation du magic link

L'utilisateur appelle `GET /api/v1/auth/verify?token=<token>`.

Le système vérifie que le token existe en base, qu'il n'est pas expiré
(comparaison UTC), et qu'il n'a pas déjà été consommé (used_at est null).

Si valide : `used_at` est marqué avec le datetime courant. Une
`UserSession` est créée avec un `session_token` aléatoire et une
expiration de 24 heures. Un cookie HTTP HttpOnly est posé sur la
réponse.

Si invalide : retour 401 avec un message générique qui ne distingue
pas token inexistant, expiré ou déjà utilisé — pour ne pas faciliter
l'énumération.

### Requêtes authentifiées

Chaque requête aux routes protégées passe par la dépendance
`get_current_user` qui lit le cookie, résout la `UserSession`, vérifie
l'expiration, et retourne l'objet `User`. Les credentials déchiffrés
alimentent l'instance `IBMPAClient` de la session.

---

## 5. Phase 1 — Modèle de session utilisateur

### Objectif de la phase

Créer la représentation persistante d'un utilisateur et de sa session
active. Aucun endpoint auth n'est créé dans cette phase — uniquement
les fondations de données et la configuration.

### Modèle User

Fichier cible : `app/models/user.py`

Table `users` avec les colonnes suivantes :

| Colonne | Type SQLAlchemy | Contraintes |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `email` | String(255) | unique, nullable=False, index=True |
| `ibm_pa_version` | String(10) | nullable=False, default="V12" |
| `credentials_encrypted` | Text | nullable=True |
| `created_at` | DateTime(timezone=True) | server_default=func.now() |

Le champ `ibm_pa_version` accepte les valeurs `"V12"` (implémenté
maintenant) et `"V11"` (réservé pour l'adaptateur futur).

Le champ `credentials_encrypted` contient le JSON chiffré des
credentials. Sa structure interne varie selon `ibm_pa_version` :

Pour V12 :
```
{"tenant_id": "<tenant>", "api_key": "<clé>"}
```

Pour V11 (réservé, non implémenté) :
```
{"host": "...", "port": ..., "auth_mode": "basic"|"cam", "username": "...", "password": "..."}
```

Ce design satisfait C-1 sans introduire de colonne nullable par version.
Il n'est pas nécessaire de valider la structure interne en base — le
service est responsable du parsing.

### Modèle UserSession

Fichier cible : `app/models/user_session.py`

Table `user_sessions` avec les colonnes suivantes :

| Colonne | Type SQLAlchemy | Contraintes |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `user_id` | Integer | FK → users.id, nullable=False, index=True |
| `session_token` | String(255) | unique, nullable=False, index=True |
| `expires_at` | DateTime(timezone=True) | nullable=False |
| `last_used_at` | DateTime(timezone=True) | nullable=True |
| `created_at` | DateTime(timezone=True) | server_default=func.now() |

Le `session_token` est une chaîne aléatoire générée par
`secrets.token_urlsafe(32)`. Il est le seul identifiant utilisé dans
le cookie HTTP — jamais l'`id` entier ou l'email.

Le champ `last_used_at` est réservé pour un mécanisme de prolongation
de session futur. Dans cette phase, il n'est pas mis à jour.

### Modèle UserAllowlist

Fichier cible : `app/models/user_allowlist.py`

Table `user_allowlist` avec les colonnes suivantes :

| Colonne | Type SQLAlchemy | Contraintes |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `email` | String(255) | unique, nullable=False, index=True |
| `created_at` | DateTime(timezone=True) | server_default=func.now() |

Ce modèle implémente un contrôle d'accès par liste blanche. Avant de
traiter une demande d'authentification, le service vérifie que l'email
du demandeur figure dans cette table. Si l'email est absent, la
création du magic link est rejetée avec HTTP 403 et le message :
`"Accès non autorisé. Contactez l'administrateur pour obtenir une invitation."`.

**Seed initial** : au premier démarrage, la table doit contenir au moins
l'email du développeur principal. Cet email est configurable via la
variable `PA_EXPLORER_INITIAL_ADMIN_EMAIL` dans `.env.local`. L'insertion
se fait dans le bloc `lifespan` de `app/main.py` ou via un script de seed
dédié, au choix de l'implémenteur — l'important est que la table ne
soit jamais vide au démarrage d'un environnement neuf.

### Validation des credentials IBM PA

Avant de persister les credentials et de générer le magic link, le
service doit vérifier que l'api_key fournie est effectivement valide
en faisant un appel léger à IBM PA :

```
GET /api/<tenant_id>/v0/tm1/Servers
```

Ce endpoint est le plus simple disponible et ne requiert pas de
paramètre supplémentaire. Il suffit à confirmer que l'api_key est
acceptée par IBM PA.

Comportement attendu selon la réponse IBM PA :

- **Réponse 200** : credentials valides, on continue le flow.
- **Réponse 401** : api_key invalide ou révoquée. Rejet HTTP 400 avec
  message : `"Clé API IBM PA invalide. Vérifiez votre api_key."`.
- **Timeout ou erreur réseau** : IBM PA injoignable. Rejet HTTP 400
  avec message : `"Impossible de joindre IBM PA pour valider les
  credentials. Réessayez."`.
- **Autre erreur IBM PA (5xx, 403)** : Rejet HTTP 400 avec message
  adapté au code d'erreur.

Cette validation utilise le `IBMPAClient` existant avec la gestion
d'exceptions `IBMPAAuthError`, `IBMPATimeoutError`, `IBMPAConnectionError`
déjà en place. Pas de nouvelle logique d'appel HTTP à créer.

### Chiffrement Fernet

La clé de chiffrement est une variable d'environnement
`PA_EXPLORER_ENCRYPTION_KEY`, une chaîne base64url de 44 caractères
générée par Fernet. La bibliothèque cible est `cryptography`.

La méthode de chiffrement et de déchiffrement est encapsulée dans
`app/services/auth_service.py`. Elle ne doit pas être dispersée dans
les routers.

Procédure de génération de la clé (à faire une seule fois par
environnement) :
```
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```
Copier la valeur affichée (44 caractères) dans `.env.local` sous la
variable `PA_EXPLORER_ENCRYPTION_KEY`. Ne jamais la versionner.

### Configuration

`app/config.py` doit être étendu avec :
```
pa_explorer_encryption_key: str
pa_explorer_initial_admin_email: str
auth_session_ttl_hours: int = 24
auth_magic_link_ttl_minutes: int = 15
```

`.env.example` doit être mis à jour avec les nouvelles variables.

### Livrables de la Phase 1

- `app/models/user.py` — modèle `User`
- `app/models/user_session.py` — modèle `UserSession`
- `app/models/user_allowlist.py` — modèle `UserAllowlist`
- `app/schemas/auth.py` — schéma Pydantic `AuthRequest` (email,
  ibm_pa_version, credentials_payload)
- `app/services/auth_service.py` — classe `AuthService` avec méthodes
  `encrypt_credentials`, `decrypt_credentials`, `create_or_update_user`,
  `get_session_by_token`, `check_allowlist`, `validate_ibm_pa_credentials`
- `app/config.py` étendu avec `pa_explorer_encryption_key`,
  `pa_explorer_initial_admin_email`, TTL auth
- `.env.example` mis à jour avec les nouvelles variables
- `app/main.py` mis à jour pour importer les trois nouveaux modèles
  (noqa F401) et pour seeder `UserAllowlist` avec
  `pa_explorer_initial_admin_email` au démarrage
- `reset_db.ps1` à ré-exécuter pour recréer la base avec les nouvelles
  tables

### Critères de validation de la Phase 1

1. `python -m uvicorn app.main:app --reload` démarre sans erreur.
2. Les tables `users`, `user_sessions` et `user_allowlist` sont
   visibles dans `pa_explorer.db`.
3. La table `user_allowlist` contient une ligne avec l'email défini
   dans `PA_EXPLORER_INITIAL_ADMIN_EMAIL` dès le premier démarrage.
4. Le schéma `AuthRequest` est exposé dans la documentation Swagger
   sous `/docs`.
5. Une ligne insérée manuellement en base avec des credentials JSON
   chiffrés n'est pas lisible en clair dans le champ
   `credentials_encrypted`.

---

## 6. Phase 2 — Génération et validation du magic link

### Objectif de la phase

Implémenter le flow complet de demande d'authentification et de
validation du token. À l'issue de cette phase, un utilisateur peut
obtenir une session active via le magic link.

### Modèle MagicLinkToken

Fichier cible : `app/models/magic_link_token.py`

Table `magic_link_tokens` avec les colonnes suivantes :

| Colonne | Type SQLAlchemy | Contraintes |
|---|---|---|
| `id` | Integer | PK, autoincrement |
| `user_id` | Integer | FK → users.id, nullable=False, index=True |
| `token` | String(255) | unique, nullable=False, index=True |
| `expires_at` | DateTime(timezone=True) | nullable=False |
| `used_at` | DateTime(timezone=True) | nullable=True |
| `created_at` | DateTime(timezone=True) | server_default=func.now() |

Le token est généré par `secrets.token_urlsafe(32)`. Il est à usage
unique : dès qu'il est consommé, `used_at` est marqué et toute tentative
ultérieure retourne 401.

### Endpoint POST /api/v1/auth/request

**Entrée** : corps JSON conforme à `AuthRequest`.

```
{
  "email": "user@company.com",
  "ibm_pa_version": "V12",
  "credentials_payload": {
    "tenant_id": "mon-tenant",
    "api_key": "ma-cle-ibm-pa"
  }
}
```

**Traitement** :
1. Vérifier que l'email figure dans `UserAllowlist`. Si absent : HTTP 403
   avec message `"Accès non autorisé. Contactez l'administrateur pour obtenir une invitation."`.
2. Valider les credentials contre IBM PA via `IBMPAClient.get_servers()`
   (instancié avec les credentials fournis). Selon la réponse :
   - 401 IBM PA → HTTP 400 `"Clé API IBM PA invalide. Vérifiez votre api_key."`
   - Timeout → HTTP 400 `"Impossible de joindre IBM PA pour valider les credentials. Réessayez."`
   - Autre erreur IBM PA → HTTP 400 avec message adapté au code.
3. Chiffrer `credentials_payload` avec Fernet.
4. Créer ou mettre à jour le `User` (upsert sur email).
5. Créer un `MagicLinkToken` avec expiration à maintenant + 15 minutes.
6. Construire l'URL de vérification et la logger dans la console uvicorn
   (niveau INFO) : `logger.info("Magic link: %s", verify_url)`.

**Réponse** : HTTP 200 avec message générique.
```json
{"message": "Un lien d'authentification a été généré. Consultez les logs uvicorn."}
```

Le token n'apparaît jamais dans le corps de la réponse HTTP. En semaine 5,
cette étape sera remplacée par un envoi par email réel (cf. section 11).

### Endpoint GET /api/v1/auth/verify

**Paramètre** : `token` (query string).

**Traitement** :
1. Chercher le `MagicLinkToken` par valeur de token.
2. Si introuvable : 401.
3. Si `used_at` n'est pas null : 401.
4. Si `expires_at` < maintenant (UTC) : 401.
5. Marquer `used_at = datetime.now(timezone.utc)`.
6. Créer une `UserSession` avec token aléatoire et expiration à
   maintenant + 24 heures.
7. Retourner HTTP 200 avec un cookie `session_token` HttpOnly, Secure,
   SameSite=Lax, durée max 86400 secondes.

**Réponse** :
```json
{"message": "Session créée. Vous êtes authentifié."}
```

Le message d'erreur pour les cas 401 (token invalide, expiré, déjà
utilisé) doit être identique et générique pour ne pas faciliter
l'énumération.

### Extension de AuthService

`app/services/auth_service.py` reçoit deux nouvelles méthodes :

`create_magic_link(user: User) -> MagicLinkToken` — génère et persiste
le token.

`verify_magic_link(token_str: str) -> UserSession` — valide le token,
crée la session, retourne la `UserSession`. Lève une exception métier
`InvalidTokenError` dans tous les cas d'échec (introuvable, expiré,
déjà utilisé) — le router la traduit en 401.

### Router auth

Fichier cible : `app/routers/auth.py`

Contient les deux endpoints décrits ci-dessus, avec injection de
`AuthService` via `Depends`, et gestion des exceptions métier auth vers
`HTTPException`.

Le router est monté dans `app/main.py` sous le préfixe `/api/v1`.

### Livrables de la Phase 2

- `app/models/magic_link_token.py` — modèle `MagicLinkToken`
- Extension de `app/services/auth_service.py` — méthodes
  `create_magic_link` et `verify_magic_link`
- `app/routers/auth.py` — endpoints `POST /auth/request` et
  `GET /auth/verify`
- `app/schemas/auth.py` étendu avec `AuthRequestResponse` et
  `AuthVerifyResponse`
- `app/main.py` mis à jour pour importer le modèle `magic_link_token`
  et monter `auth.router`
- `reset_db.ps1` à ré-exécuter pour créer la table `magic_link_tokens`

### Critères de validation de la Phase 2

1. `POST /api/v1/auth/request` avec des credentials V12 valides retourne
   HTTP 200 avec `verify_url` en mode `DEBUG=true`.
2. `GET /api/v1/auth/verify?token=<token>` avec le token reçu retourne
   HTTP 200 et pose le cookie `session_token`.
3. Un second appel `GET /auth/verify` avec le même token retourne HTTP 401.
4. Un appel `GET /auth/verify` avec un token forgé retourne HTTP 401.
5. Un appel `GET /auth/verify` après expiration des 15 minutes retourne
   HTTP 401 (à tester en réduisant `auth_magic_link_ttl_minutes` à 0).

---

## 7. Phase 3 — Middleware de protection des routes

### Objectif de la phase

Protéger les routes existantes `/servers`, `/cubes`, `/dimensions` avec
la session utilisateur, et injecter `IBMPAClient` avec les credentials
de la session plutôt que les variables d'environnement globales.

### Dépendance get_current_user

Fichier cible : `app/dependencies/auth.py` (nouveau dossier `dependencies/`)

```
get_current_user(request: Request, db: Session = Depends(get_db)) -> User
```

Cette dépendance lit le cookie `session_token` depuis la requête. Elle
interroge la table `user_sessions` pour résoudre la session. Elle vérifie
que `expires_at` n'est pas dépassé (normalisation UTC pour SQLite). Elle
retourne l'objet `User` associé.

Lève `HTTPException(401)` si le cookie est absent, si la session est
introuvable, ou si la session est expirée.

### Dépendance get_ibm_pa_client_for_user

Dans le même fichier `app/dependencies/auth.py` :

```
get_ibm_pa_client_for_user(user: User = Depends(get_current_user)) -> IBMPAClient
```

Cette dépendance déchiffre `user.credentials_encrypted`, parse le JSON
selon `user.ibm_pa_version`, et instancie `IBMPAClient` avec les
credentials de l'utilisateur.

Pour V12 : utilise `tenant_id` et `api_key` issus du JSON déchiffré,
et `ibm_pa_base_url` depuis `settings` (l'URL de base reste globale).

Cette dépendance remplace la dépendance locale `get_ibm_pa_client` définie
dans chaque router. La dépendance locale est supprimée des routers.

### Migration des routers existants

Les fichiers `app/routers/servers.py`, `app/routers/cubes.py`,
`app/routers/dimensions.py` subissent les modifications suivantes :

1. Supprimer la fonction locale `get_ibm_pa_client`.
2. Importer `get_ibm_pa_client_for_user` depuis `app.dependencies.auth`.
3. Remplacer `Depends(get_ibm_pa_client)` par
   `Depends(get_ibm_pa_client_for_user)` dans les dépendances de service.

Aucun autre changement dans la logique des routers. Le pattern
service/cache-aside reste intact.

### Sort des variables d'environnement globales IBM PA

Les variables `IBM_PA_BASE_URL`, `IBM_PA_TENANT_ID`, `IBM_PA_API_KEY`
restent dans `app/config.py` et dans `.env.local`. Elles ne sont plus
utilisées par les routers protégés, mais leur suppression serait un
breaking change inutile à ce stade.

L'implémenteur peut choisir de les supprimer totalement (Option A,
propre) ou de les conserver comme documentation (Option B, prudent).
Le PRD ne tranche pas : les deux sont valides, au jugement de la session
d'implémentation.

### Livrables de la Phase 3

- `app/dependencies/__init__.py` (fichier vide pour le package)
- `app/dependencies/auth.py` — dépendances `get_current_user` et
  `get_ibm_pa_client_for_user`
- Modification de `app/routers/servers.py` — migration de la dépendance
  IBM PA client
- Modification de `app/routers/cubes.py` — idem
- Modification de `app/routers/dimensions.py` — idem

### Critères de validation de la Phase 3

1. `GET /api/v1/servers` sans cookie retourne HTTP 401.
2. `GET /api/v1/cubes` sans cookie retourne HTTP 401.
3. `GET /api/v1/dimensions` sans cookie retourne HTTP 401.
4. Après un flow complet (POST /auth/request → GET /auth/verify),
   `GET /api/v1/servers` avec le cookie retourne les données IBM PA de
   l'utilisateur authentifié.
5. Modifier manuellement le `session_token` dans le cookie avant un
   appel retourne HTTP 401.

---

## 8. Dépendances entre phases

```
Phase 1  ──prérequis──►  Phase 2  ──prérequis──►  Phase 3
(modèles)               (magic link)              (middleware)
```

Phase 1 est un prérequis strict de Phase 2 : les modèles `User`,
`UserSession`, et le service `AuthService` avec chiffrement doivent
être en place avant de créer `MagicLinkToken` et les endpoints auth.

Phase 2 est un prérequis strict de Phase 3 : la dépendance
`get_current_user` résout une `UserSession` — elle ne peut être testée
que si le flow de création de session (Phase 2) fonctionne.

Chaque phase doit se terminer avec uvicorn démarrant et les critères
de validation vérifiés manuellement avant de démarrer la suivante.
Ne pas enchaîner les phases sans validation intermédiaire.

---

## 9. Décisions architecturales à documenter

À l'issue de l'implémentation complète des trois phases, le fichier
`docs/learning/decisions.md` doit être mis à jour avec les entrées
suivantes :

**D-010 — Chiffrement Fernet des credentials utilisateur [DÉFINITIVE]**  
Justification : Fernet est un chiffrement symétrique authentifié
disponible sans dépendance externe lourde via la bibliothèque
`cryptography`. Les credentials IBM PA ne transitent jamais en clair
en base de données.

**D-011 — Magic link sans mot de passe [DÉFINITIVE]**  
Justification : le contexte IBM PA SaaS n'a pas de concept de mot de
passe PA-Explorer distinct de l'api_key. Le magic link vérifie l'email
sans ajouter un nouveau secret à gérer pour l'utilisateur.

**D-012 — Variables IBM_PA globales conservées après Phase 3 [RÉVISABLE]**  
Justification : suppression trop agressive pour un POC en cours
d'apprentissage. À réévaluer si PA-Explorer évolue vers un usage
multi-tenant réel.

---

## 10. Notes pour l'implémenteur

### Piège datetime SQLite

Les `expires_at` stockés dans SQLite seront naïfs (sans timezone).
Avant toute comparaison avec `datetime.now(timezone.utc)`, appliquer :
```python
if dt.tzinfo is None:
    dt = dt.replace(tzinfo=timezone.utc)
```
Ce pattern est déjà en place dans `server_service.py` — s'y référer.

### Sécurité du cookie

Le cookie `session_token` doit être posé avec `httponly=True`,
`samesite="lax"`. L'attribut `secure=True` est recommandé en
production mais peut être désactivé en développement HTTP local.

### Pas d'invalidation de tokens anciens

Si un utilisateur appelle `POST /auth/request` une seconde fois avant
d'avoir consommé un premier token, un second token est créé. L'ancien
reste valide jusqu'à son expiration naturelle. Ce comportement est
acceptable pour un POC. Une implémentation plus stricte invaliderait les
anciens tokens sur chaque nouvelle demande.

### Dépendance cryptography

Ajouter `cryptography` dans `requirements.txt`. Vérifier la compatibilité
avec Python 3.12.

### Avertissement — perte de la clé PA_EXPLORER_ENCRYPTION_KEY

La clé Fernet est le seul moyen de déchiffrer les credentials IBM PA
stockés en base. Si `PA_EXPLORER_ENCRYPTION_KEY` est perdue, modifiée
ou régénérée, toutes les entrées `credentials_encrypted` de la table
`users` deviennent illisibles. La seule procédure de récupération est
de réinitialiser la base (`reset_db.ps1`), de regénérer une clé, et de
demander à tous les utilisateurs de se ré-enregistrer.

**Procédure de génération initiale** (une seule fois par environnement) :

```bash
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

La commande affiche une chaîne de 44 caractères. La copier dans
`.env.local` :

```
PA_EXPLORER_ENCRYPTION_KEY=<chaîne de 44 caractères>
```

Ne jamais committer cette valeur dans git. Ne jamais l'afficher dans
les logs. Ne pas confondre avec `IBM_PA_API_KEY` — ce sont deux secrets
distincts avec des cycles de vie différents.

Les bonnes pratiques de gestion de clé en production (rotation, stockage
dans un secret manager, audit d'accès) seront abordées dans les semaines
avancées du parcours.

---

## 11. Évolutions prévues

### Envoi du magic link par email — début de semaine 5

Dans la version semaine 4 décrite par ce PRD, le lien de vérification
est loggé dans la console uvicorn. Cette approche est fonctionnelle pour
un développement solo et simplifie le démarrage sans dépendance externe.

En début de semaine 5, une session de suivi ajoutera l'envoi par email
réel via **Mailtrap** (service de sandbox email pour le développement)
ou un équivalent. Cette évolution touchera uniquement la méthode
`create_magic_link` de `AuthService` et n'impactera pas les modèles
ni les autres couches.

Le choix de Mailtrap est motivé par sa capacité à intercepter les emails
envoyés sans les délivrer réellement, ce qui maintient un environnement
de développement sûr tout en testant le rendu des emails.

L'intégration d'un service d'envoi transactionnel en production
(SendGrid, Amazon SES, Brevo, ou autre) sera traitée comme une décision
d'infrastructure séparée, documentée dans `decisions.md` au moment du choix.
