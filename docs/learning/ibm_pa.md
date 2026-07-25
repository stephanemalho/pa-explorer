# Référentiel IBM Planning Analytics — PA-Explorer

Ce fichier documente les connaissances accumulées sur IBM Planning Analytics 
au fil du parcours, organisées par thème. Les informations issues de la 
documentation officielle IBM ou de la recherche documentaire sont signalées 
comme telles. Les informations issues de l'observation directe des réponses 
de l'API sur le tenant SaaS utilisé sont signalées comme observations terrain. 
Les informations tirées du code PA-Explorer sont référencées par leur fichier.

---

## Vue d'ensemble du domaine

IBM Planning Analytics (anciennement TM1) est une plateforme de planification 
financière et d'analyse multidimensionnelle. Son modèle de données est organisé 
autour de quelques entités centrales dont la connaissance est nécessaire pour 
naviguer dans son API REST.

Un **cube** est le conteneur de base des données numériques. Il est défini par 
un ensemble de dimensions qui forment ses axes. (Source : LEARNING.md, section 
notes IBM PA du 26 avril.)

Une **dimension** est un axe du cube. Elle contient une liste d'éléments. 
Quand une dimension est utilisée en ligne ou en colonne d'une vue, chacun de 
ses éléments génère un en-tête. Une **dimension de contexte** filtre le cube 
sans apparaître sur les axes de la grille. (Source : LEARNING.md.)

Un **ensemble de cellules** (cellset) est le résultat de l'exécution d'une vue 
ou d'une expression MDX. Il représente un instantané des données à un instant 
donné. L'identifiant d'un ensemble de cellules peut être réutilisé dans la 
même session API pour éviter de recalculer la vue plusieurs fois. (Source : 
LEARNING.md.)

Un **élément** identifie la position d'une cellule dans une dimension. 
Une **tâche** (process) est une entité TM1 exécutable, manipulable via les 
opérations CRUD standard de l'API REST. (Source : LEARNING.md.)

L'API REST TM1 implémente le protocole **OData v4**. Un document `$metadata` 
expose le schéma complet du serveur au format CSDL (Common Schema Definition 
Language). Pour un déploiement SaaS, ce document est accessible à l'adresse 
suivante selon la documentation IBM (connaissance générale non vérifiée sur 
le tenant PA-Explorer) :
`https://<base_url>/api/<tenant_id>/v0/tm1/$metadata`

Pour un TM1 Admin Server on-premise, le point d'accès aux métadonnées est 
`http://<adminserver>:5895/api/v1/$metadata`. (Source : LEARNING.md.)

---

## Authentification

### Méthode retenue : Basic Auth avec username littéral

L'API IBM Planning Analytics SaaS (plateforme MCSP — Multi-Cloud Subscription 
Platform) utilise HTTP Basic Authentication avec une convention spécifique. 
Le username n'est pas l'adresse email de l'utilisateur mais la chaîne littérale 
`"apikey"`. Le password est la clé API générée depuis l'interface IBM Planning 
Analytics Workspace. (Source : decisions.md, D-004 ; confirmé par recherche 
documentaire en semaine 2.)

L'en-tête HTTP résultant suit le format standard Basic Auth :
```
Authorization: Basic base64("apikey:<votre_clé_api>")
```

Dans PA-Explorer, cette authentification est construite dans 
`app/clients/ibm_pa.py` :
```python
self._auth = httpx.BasicAuth("apikey", api_key)
```
Et transmise sur chaque requête via le paramètre `auth` de httpx.

### Pourquoi les premières tentatives Postman ont échoué

Les premières tentatives d'appel API avec Postman en semaine 1 retournaient 
une erreur `AuthorizedConnectionFailed`. La cause était l'utilisation de 
l'adresse email comme username dans le Basic Auth au lieu de la chaîne 
`"apikey"`. (Source : LEARNING.md session du 28 avril ; decisions.md D-004.)

### URL de base et format du tenant

L'URL de base du déploiement SaaS utilisé dans PA-Explorer est définie dans 
`.env.local` sous la variable `IBM_PA_BASE_URL`. Dans la configuration du 
projet, cette variable pointe vers le cluster européen central d'IBM PA SaaS. 
(Source : `.env.example` à la racine du projet.)

Le `IBM_PA_TENANT_ID` est l'identifiant du tenant IBM PA. Il est injecté dans 
le chemin de l'URL de chaque requête. Le pattern d'URL pour les appels API 
est (source : recherche documentaire semaine 2, confirmé par observation 
terrain) :
```
https://<IBM_PA_BASE_URL>/api/<tenant_id>/v0/tm1/<endpoint>
```

---

## Endpoints découverts

### GET Servers

L'endpoint de listing des serveurs TM1 est le premier endpoint implémenté 
dans PA-Explorer. Son chemin sur le serveur IBM PA est :
```
GET /api/<tenant_id>/v0/tm1/Servers
```

Il retourne la liste des bases de données TM1 (appelées "serveurs" dans la 
terminologie IBM) accessibles pour le tenant. (Source : plan de la session du 
28 avril, confirmé par observation terrain.)

La réponse suit le format OData v4 avec une enveloppe `value` contenant le 
tableau des serveurs.

### Endpoints anticipés pour les semaines suivantes

La structure de l'API TM1 OData suggère les endpoints suivants pour les 
features à venir (connaissance générale basée sur la documentation IBM OData, 
non encore vérifiée sur le tenant PA-Explorer) :

```
GET /api/<tenant_id>/v0/tm1/<server_name>/Cubes
GET /api/<tenant_id>/v0/tm1/<server_name>/Dimensions
GET /api/<tenant_id>/v0/tm1/<server_name>/Processes
GET /api/<tenant_id>/v0/tm1/<server_name>/Cubes('<cube_name>')/Views
```

---

## Structure des réponses

### Champs observés sur le tenant SaaS PA-Explorer

Les champs suivants ont été observés dans les réponses IBM PA sur le tenant 
SaaS utilisé par le projet, et sont mappés dans le modèle `Server` de 
`app/models/server.py`. Ils sont donc sourcés par observation terrain :

| Champ IBM PA | Type | Colonne SQLAlchemy | Note |
|---|---|---|---|
| `Name` | string | `name` | Identifiant unique du serveur |
| `DisplayName` | string | `display_name` | Nom d'affichage |
| `Host` | string | `host` | Nom d'hôte ou adresse IP |
| `HTTPPort` | integer | `http_port` | Port HTTP de connexion |
| `IsLocal` | boolean | `is_local` | Serveur local ou distant |
| `AcceptingClients` | boolean | `accepting_clients` | Serveur en état d'accepter des connexions |
| `Href` | string | `href` | URL de l'objet dans l'API OData |
| `isV12` | boolean | `is_v12` | Indicateur de version V12 du moteur TM1 |

Le champ `raw_data` stocke l'intégralité de la réponse JSON brute par 
enregistrement, accessible via `include_raw=true` en query param. C'est la 
source de vérité sur ce que retourne réellement IBM PA pour ce tenant.

### Champs documentés IBM mais non vérifiés sur le tenant

La documentation IBM décrit d'autres champs potentiels sur l'objet Servers, 
notamment des informations de version détaillée, des états de maintenance, et 
des capacités de connexion. Aucun de ces champs n'a été observé dans les 
réponses du tenant SaaS PA-Explorer à ce stade. La colonne `raw_data` 
permettra de les découvrir si l'API les expose.

### Format OData de l'enveloppe de réponse

Les réponses de l'API IBM PA suivent le format OData v4. Une réponse de 
collection a la structure suivante (connaissance générale OData, confirmée 
par l'implémentation du client dans `app/clients/ibm_pa.py`) :

```json
{
  "@odata.context": "...",
  "value": [
    { ... },
    { ... }
  ]
}
```

Le client `IBMPAClient.get_servers()` extrait le tableau `value` et le retourne 
à la couche service.

---

## Pièges et particularités

### La documentation IBM ne reflète pas toujours le comportement SaaS

Un enseignement clé de la semaine 2 : la documentation IBM décrit le comportement 
général de l'API TM1, mais un déploiement SaaS sur un tenant de démonstration 
peut exposer moins de champs, ou des champs avec des valeurs différentes de ce 
qu'indique la documentation. La leçon consignée dans LEARNING.md (session 28 
avril) est de toujours observer `raw_data` pour connaître la réalité du terrain, 
plutôt que de présumer que la documentation est exacte.

### Les valeurs null ne sont pas toujours des bugs

Plusieurs champs du modèle `Server` peuvent être `null` dans la réponse API, 
non pas à cause d'un bug de mapping, mais parce que IBM PA ne les expose pas 
pour ce tenant ou ce serveur. (Source : LEARNING.md, session 28 avril.) Cette 
distinction entre "champ absent de la source" et "bug de mapping" est 
essentielle pour éviter des corrections inutiles.

### isV12 versus versions antérieures TM1

Le champ `isV12` (clé IBM PA : `isV12`, casse mixte) signale si le moteur TM1 
sous-jacent est la version V12. IBM Planning Analytics V12 est une version 
architecturalement différente des versions précédentes du moteur TM1, avec des 
implications sur les fonctionnalités disponibles via l'API et sur les formats 
de données attendus. (Source : observation du champ dans les réponses IBM PA ; 
signification V12 issue de connaissances générales IBM PA, non sourçable depuis 
les fichiers du projet.)

### Codage URL des noms avec espaces

Les noms d'objets TM1 (cubes, dimensions, processus) peuvent contenir des 
espaces. Dans les URLs OData, ces noms doivent être encodés. Par exemple, un 
cube nommé `Sales Budget` serait référencé dans une URL comme 
`Cubes('Sales%20Budget')`. (Connaissance générale OData/TM1 non encore 
rencontrée en pratique dans PA-Explorer, à valider lors de l'implémentation 
des endpoints cubes.)

### Particularité du tenant de démonstration

Le tenant IBM PA utilisé dans PA-Explorer est un tenant SaaS de démonstration 
ou d'évaluation. Il peut exposer moins de données, ou des données plus limitées 
que ce qu'exposerait un tenant de production avec des modèles TM1 complexes. 
Les observations terrain de ce projet sur les champs et les valeurs retournées 
par l'API sont donc spécifiques à ce contexte.

---

## Inventaire et livraison (cap PA-PROMOTE)

> Provenance : cette section synthétise `docs/learning/REGLES-LIVRAISON-TM1.md`
> (référentiel de livraison, lui-même issu de la documentation IBM). Les docs IBM
> officielles n'ont pas pu être re-vérifiées par fetch le 2026-07-25 (réponses HTTP
> 403/429). Conformément à la règle « ne pas deviner », rien n'est ajouté au-delà
> du référentiel. À revalider sur le `$metadata` du serveur cible et sur la doc IBM
> lors de l'implémentation (semaines 10-11).

### Distinction de familles d'URL

Trois formats d'URL coexistent selon le déploiement — ne pas les confondre :

- **MCSP SaaS (lecture actuelle de PA-Explorer)** : `/api/<tenant_id>/v0/tm1/<endpoint>`
  (voir sections plus haut). C'est le tenant de démonstration utilisé jusqu'ici.
- **V11 (cap livraison)** : `https://host:port/api/v1/<endpoint>`.
- **V12 (cap livraison)** : scopé par base de données —
  `https://host:port/api/v1/Databases('tm1-i-<id>')/<endpoint>`.

### Endpoints d'inventaire (modèle objet OData v4, commun V11/V12)

Entités utilisées pour explorer un modèle et préparer une livraison (source :
référentiel §1-§10) :

```
GET/POST  /Dimensions                                   (+ GET/DELETE /Dimensions('d'))
GET       /Dimensions('d')/Hierarchies                  (+ /Hierarchies('h'))
GET/POST  /Dimensions('d')/Hierarchies('h')/Elements
GET/POST  /Dimensions('d')/Hierarchies('h')/Edges       (ParentName / ComponentName / Weight)
GET       /Dimensions('d')/Hierarchies('h')/Subsets
GET/POST  /Cubes                                        (+ GET/DELETE /Cubes('c'))
GET       /Cubes('c')?$expand=Dimensions                (dimensionnalité d'un cube)
GET       /Cubes('c')/Views
GET       /Processes                                    (TurboIntegrator)
GET       /Chores
```

Les **valeurs d'attributs** ne sont pas de la structure : elles vivent dans le cube
de contrôle `}ElementAttributes_<dim>` et relèvent de la piste données (référentiel
§4, §12). Les objets de contrôle (préfixe `}`) sont exclus par défaut d'une livraison.

### Authentification V11 vs V12 (référentiel §14)

| | V11 | V12 |
|---|---|---|
| Méthode | Basic (natif, mode 1) **ou CAM** : en-tête `CAMNamespace base64(user:pass:namespace)` ou `CAMPassport` (modes 2-5, **mode 5 = CAM/Cognos**), HTTPS obligatoire | **OIDC/OAuth** : bearer token, `WWW-Authenticate: openid`, client OAuth |
| Scope d'URL | `/api/v1/...` | `/api/v1/Databases('tm1-i-<id>')/...` |
| Accès fichier (TI) | fichiers locaux / ODBC disponibles | **supprimé** — REST only |

L'accès à l'API REST complète en V11 ne dépend pas du mode de sécurité mais du bon
en-tête d'auth ; valider la connexion sur `/api/v1/Cubes` avant toute livraison.

### Pièges V12 à anticiper

- **OData only** : les API REST « C / Java / .Net » et versions internes ne sont pas
  supportées ; les utilitaires en ligne de commande V11 sont remplacés par des
  endpoints REST.
- **Pas d'accès fichier** : les processus TI qui lisaient des fichiers locaux / ODBC
  doivent être reparamétrés ou signalés (référentiel P2, VN3).
- **Scope par base** : chaque appel est relatif à `Databases('tm1-i-<id>')` ; le
  `ServerName` a la forme `tm1-i-<id>`.

Ces trois différences (auth, scope, accès fichier) sont les seules isolées derrière
la couche `VersionProvider` (D-016) ; le reste du modèle objet est commun.

## Sources documentaires IBM

| Source | URL | Quand la consulter |
| --- | --- | --- |
| Doc REST API IBM PA | `https://www.ibm.com/docs/en/planning-analytics/latest?topic=rest-api` | Découvrir un endpoint, vérifier un schéma de réponse |
| `$metadata` du tenant | `{IBM_PA_BASE_URL}/api/{TENANT_ID}/v0/tm1/$metadata` | Obtenir le schéma OData réel du tenant (priorité sur la doc statique) |
| Troubleshooting API | `https://www.ibm.com/docs/fr/planning-analytics/3.1.0?topic=api-troubleshooting` | Diagnostiquer une erreur de connexion ou de requête |
| Paramètres TM1 | `https://www.ibm.com/docs/fr/planning-analytics/3.1.0?topic=api-tm1-settings` | Configurer les paramètres avancés du tenant |
| Gestion des actifs TM1 avec Git | `https://www.ibm.com/docs/fr/planning-analytics/3.1.0?topic=api-managing-tm1-database-assets-git` | Déployer des actifs TM1 entre environnements via Git |
| Spécification tm1project | `https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=git-tm1-model-source-specification` | Ce qu'une livraison publie/exclut (structure, objets `}`) |
| Auth & sessions V11 (CAM) | `https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=api-authenticating-managing-sessions` | En-têtes `CAMNamespace` / `CAMPassport`, mode 5 |
| Auth REST V12 (OIDC/OAuth) | `https://www.ibm.com/docs/en/planning-analytics/3.1.0?topic=api-authenticating-rest-requests` | Bearer OAuth en V12 |
| TM1 Database 12 (V12) | `https://www.ibm.com/docs/SSD29G_3.1.0/com.ibm.swg.ba.cognos.planning_analytics_engine.2.0.0.doc/pa_engine_getting_started.html` | Spécificités V12 (scope par base, OData only) |
| Référentiel de livraison (repo) | `docs/learning/REGLES-LIVRAISON-TM1.md` | Règles de promotion synthétisées — source de vérité |

**Consigne pour l'agent** : toujours consulter le `$metadata` du tenant avant de proposer
un nouvel endpoint. La doc statique IBM peut diverger du comportement SaaS réel (constaté en S2).
L'URL validée sur ce tenant : `{IBM_PA_BASE_URL}/api/{TENANT_ID}/v0/tm1/$metadata`.
