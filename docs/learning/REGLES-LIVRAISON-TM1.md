# Règles de livraison TM1 / Planning Analytics (source → cible)

> Référentiel métier pour PA-PROMOTE. Ces règles encadrent la promotion d'objets
> d'un serveur **source** vers un serveur **cible** via l'API REST OData de TM1,
> en respectant le modèle objet IBM et la spécification `tm1project`.
> Cible technique : **Planning Analytics V12** (Planning Analytics Engine), API
> OData exclusivement.

---

## 0. Principes fondateurs (à connaître avant tout)

Trois faits structurants tirés de la documentation IBM et du comportement de
`tm1-git` / `tm1project` conditionnent **toute** la logique de livraison :

1. **La livraison transporte la *structure*, pas les *données*.** `tm1-git` et
   `tm1project` publient/déploient cubes, dimensions, hiérarchies, vues, subsets,
   processus et chores — **jamais** les valeurs de cellules. Les données (y compris
   attributs et sécurité) se déplacent séparément, via des processus TI d'export/import
   ou via écriture de cellsets REST. → **PA-PROMOTE doit gérer deux pistes distinctes :
   livraison de structure et livraison de données.**

2. **La livraison ne supprime jamais côté cible.** Par design, `tm1-git` ne retire
   pas un objet du serveur cible même s'il a disparu de la source. → **Toute
   suppression est une opération explicite, séparée, et à haut risque.**

3. **Un objet ne peut être créé/mis à jour que si toutes ses dépendances existent
   déjà côté cible.** C'est la règle mère dont découlent toutes les autres : elle
   impose un **ordre de livraison topologique** (les feuilles avant les branches).

**Ordre de livraison canonique (dépendances résolues d'abord) :**

```
1. Dimensions (conteneurs)
2.   └─ Hiérarchies
3.       └─ Éléments / membres
4.           └─ Edges (relations parent-enfant)
5.   └─ Attributs de dimension  (}ElementAttributes_<dim>)
6.   └─ Subsets  (statiques puis dynamiques/MDX)
7. Cubes  (référencent des dimensions existantes)
8.   └─ Règles (rules) et feeders
9.   └─ Vues  (natives puis MDX)
10. Processus TI  (référencent cubes/dims/vues/subsets)
11. Chores  (référencent des processus)
12. Sécurité + données  (piste séparée, via TI/cellsets)
```

La règle de suppression suit **l'ordre inverse** (les branches avant les feuilles) :
on retire une dimension d'un cube avant de supprimer la dimension, on supprime le
chore avant le processus, etc.

---

## 1. Dimensions

| # | Règle | Justification / Source |
|---|-------|------------------------|
| D1 | Une dimension doit exister côté cible **avant** tout cube qui l'utilise. | Modèle objet : un cube est défini par sa liste de dimensions. |
| D2 | Créer/mettre à jour une dimension **avant** ses hiérarchies, éléments et subsets. | Les enfants référencent la dimension parente. |
| D3 | Une dimension **ne peut pas être supprimée si elle est encore utilisée par un cube**. `DELETE /Dimensions('x')` échoue sinon. | Contrainte IBM confirmée (erreur côté serveur). |
| D4 | Ne pas livrer les dimensions de contrôle (préfixe `}`) par défaut ; les inclure explicitement seulement si nécessaire (`}ElementAttributes_`, `}ElementSecurity_`…). | `tm1project` : les objets `}` sont exclus sauf `!`-inclusion explicite. |
| D5 | En V11, **l'ordre physique des dimensions d'un cube ne fait pas partie de l'objet publié** ; ne pas s'y fier pour la livraison. À revalider en V12. | Limitation `tm1-git` documentée. |

Endpoints : `GET/POST /Dimensions`, `GET/DELETE /Dimensions('x')`.

---

## 2. Hiérarchies

| # | Règle | Justification |
|---|-------|---------------|
| H1 | La dimension parente doit exister avant la hiérarchie. | Dépendance de conteneur. |
| H2 | Toute dimension possède au minimum une hiérarchie du même nom (hiérarchie « feuille »/leaf) ; la traiter comme cas par défaut. | Modèle PA : dimension = conteneur de hiérarchies. |
| H3 | Livrer les **éléments avant les edges** de la hiérarchie (un edge ne peut lier que des éléments existants). | Ordre topologique interne. |
| H4 | Attention aux hiérarchies « réelles » de PA (niveau intermédiaire) : elles n'existent pas en TM1 classique — vérifier la compatibilité de version source/cible. | Feature PA hiérarchies. |

Endpoints : `/Dimensions('d')/Hierarchies`, `.../Hierarchies('h')/Elements`,
`.../Hierarchies('h')/Edges`.

---

## 3. Éléments / membres

| # | Règle | Justification |
|---|-------|---------------|
| M1 | Un élément doit appartenir à une hiérarchie existante avant d'être créé. | Dépendance. |
| M2 | Créer les éléments **enfants et parents avant** de créer l'edge qui les relie ; un edge vers un élément inexistant échoue. | Intégrité référentielle des edges. |
| M3 | Respecter le **type d'élément** (Numeric / String / Consolidated). Un edge parent implique un parent de type Consolidated. | Cohérence de type TM1. |
| M4 | Ne pas dupliquer un élément déjà présent : livraison **idempotente** (upsert), comparer avant d'écrire. | Éviter les erreurs et effets de bord. |
| M5 | La suppression d'un élément doit vérifier qu'il n'est pas la seule feuille alimentant un consolidé, ni référencé par un subset statique / une règle / un feeder. | Éviter de casser consolidations et règles. |

Endpoints : POST `/Dimensions('d')/Hierarchies('h')/Elements`,
POST `.../Edges` (payload `ParentName` / `ComponentName` / `Weight`).

---

## 4. Attributs (element / cube / dimension)

| # | Règle | Justification |
|---|-------|---------------|
| A1 | Les **définitions** d'attributs se livrent avec la structure ; les **valeurs** d'attributs sont des **données** (stockées dans le cube de contrôle `}ElementAttributes_<dim>`) → piste données. | Séparation structure/données. |
| A2 | La dimension cible et ses éléments doivent exister avant de charger des valeurs d'attributs. | Le cube `}ElementAttributes_` est dimensionné par la dimension + `}ElementAttributes_<dim>`. |
| A3 | Livrer les valeurs d'attributs (et de sécurité) via des **processus TI d'export/import** (`export_before_push` / `import_after_pull`) plutôt que par tm1-git. | Pattern `tm1project` officiel. |
| A4 | Attributs multilingues : livrer la dimension `}Cultures` et les valeurs par locale de façon cohérente. | Cohérence i18n. |

---

## 5. Subsets

| # | Règle | Justification |
|---|-------|---------------|
| S1 | Un subset appartient à une hiérarchie : dimension + hiérarchie doivent exister. | Dépendance. |
| S2 | **Subset statique** : tous les éléments listés doivent exister côté cible. | Intégrité référentielle. |
| S3 | **Subset dynamique (MDX)** : l'expression MDX doit se résoudre côté cible — tous les membres, hiérarchies et fonctions référencés doivent exister. Valider l'expression avant livraison. | Les subsets dynamiques dépendent de l'état du modèle cible. |
| S4 | Les subsets référencés par des vues et des processus doivent être livrés **avant** ces objets. | Ordre topologique. |
| S5 | Distinguer subsets **privés** (`}Subsets` par utilisateur) et **publics** ; par défaut on ne promeut que le public. | Éviter de polluer la cible avec des objets privés. |

---

## 6. Cubes

| # | Règle | Justification |
|---|-------|---------------|
| C1 | **Ne jamais livrer un cube si une de ses dimensions n'existe pas côté cible.** Bloquer la livraison et lister les dimensions manquantes. | Règle mère (D1). C'est l'exemple canonique demandé. |
| C2 | Livrer/valider **toutes** les dimensions du cube (dans leur intégralité : éléments requis par les règles/feeders) avant le cube. | Une règle/feeder référençant un élément absent échouera. |
| C3 | Un cube existant côté cible avec une **dimensionnalité différente** (dimensions ajoutées/retirées/réordonnées) ne peut pas être « mis à jour » à la volée : c'est un changement destructif (perte de données). À traiter comme migration explicite. | Changer les dimensions d'un cube recrée le cube. |
| C4 | Ne pas livrer les cubes de contrôle (`}`) par défaut. | `tm1project` Ignore. |
| C5 | La création du cube précède ses règles, feeders et vues. | Ordre topologique. |

Endpoints : `GET/POST /Cubes`, `GET /Cubes('c')?$expand=Dimensions`, `DELETE /Cubes('c')`.

---

## 7. Règles (rules) et feeders

| # | Règle | Justification |
|---|-------|---------------|
| R1 | Le cube porteur de la règle doit exister avant d'attacher la règle. | Dépendance. |
| R2 | Tous les cubes, dimensions et éléments **référencés** dans la règle (règles inter-cubes) doivent exister côté cible. | Une règle référençant un objet absent est invalide. |
| R3 | Pour les règles inter-cubes : le **calcul réside dans le cube cible**, mais le **feeder doit être placé dans le cube source** de la donnée. Livrer les deux cubes de façon cohérente. | Bonne pratique TM1 (propagation correcte). |
| R4 | Après livraison d'une règle, prévoir un **`}CubeProcessFeeders` / re-feed** si nécessaire pour recalculer les feeders. | Intégrité des feeders. |
| R5 | Valider la syntaxe de la règle côté cible avant commit (dry-run) ; une règle invalide peut bloquer le calcul du cube. | Sécurité de déploiement. |

---

## 8. Vues (natives et MDX)

| # | Règle | Justification |
|---|-------|---------------|
| V1 | Le cube doit exister avant la vue. | Dépendance. |
| V2 | **Vue native** : les subsets (ou sélections de titres/lignes/colonnes) référencés doivent exister côté cible. | Intégrité référentielle. |
| V3 | **Vue MDX** : l'expression MDX doit se résoudre côté cible (cube, hiérarchies, membres, sets). Valider avant livraison. | Dépend de l'état du modèle cible. |
| V4 | Distinguer vues **privées** vs **publiques** ; par défaut ne promouvoir que les publiques. | Hygiène. |
| V5 | Les vues utilisées comme **source de données d'un processus TI** doivent être livrées avant le processus. | Ordre topologique. |

---

## 9. Processus TI (TurboIntegrator)

| # | Règle | Justification |
|---|-------|---------------|
| P1 | Tous les objets référencés par le processus (cubes, dimensions, vues, subsets, autres processus via `ExecuteProcess`) doivent exister côté cible. | Dépendance. |
| P2 | Vérifier les **sources de données** : chemins de fichiers, ODBC/DSN, dossiers — n'existent pas forcément côté cible (surtout **V12 : plus d'accès fichier**). Reparamétrer ou signaler. | V12 supprime l'accès fichier local. |
| P3 | Les **paramètres** du processus et leurs valeurs par défaut doivent être livrés avec le processus. | Cohérence d'exécution. |
| P4 | Exclure de la livraison les processus de travail/brouillon via convention de nommage (`zTest`, `WIP`, préfixe dédié). | Pattern `tm1project` Ignore. |
| P5 | Ne pas exécuter automatiquement un processus livré sans validation (un TI peut écrire/supprimer des données). Séparer *livraison* et *exécution*. | Sécurité. |

---

## 10. Chores

| # | Règle | Justification |
|---|-------|---------------|
| CH1 | **Tous les processus référencés par un chore doivent exister côté cible avant le chore.** | Dépendance directe. |
| CH2 | Livrer la définition de planification (fréquence, heure de départ) mais **désactiver le chore côté cible par défaut** (ne pas déclencher d'exécutions non voulues en prod). | Sécurité de déploiement. |
| CH3 | Vérifier la cohérence des paramètres passés aux processus dans le chore. | Cohérence. |
| CH4 | Fuseaux horaires / heure de départ : revalider côté cible (serveur potentiellement dans un autre TZ). | Éviter des exécutions décalées. |

---

## 11. Objets de contrôle, sécurité et sandboxes

| # | Règle | Justification |
|---|-------|---------------|
| X1 | Les objets de contrôle (préfixe `}`) sont **exclus par défaut** ; inclusion explicite uniquement (`!Cubes('}ElementAttributes_')`). | `tm1project`. |
| X2 | La **sécurité** (}ClientGroups, }ElementSecurity_, }CellSecurity_, groupes, capabilities) se traite comme de la **donnée** → export/import TI, jamais en aveugle. | Séparation structure/données + risque d'écrasement des droits. |
| X3 | Les **sandboxes** et données de sandbox ne sont pas de la structure ; les exclure de la promotion de structure. | Périmètre. |
| X4 | Ne jamais écraser la sécurité cible sans sauvegarde préalable (`backup_instance` avant pull). | Pattern `PrePull` de `tm1project`. |

---

## 12. Données (piste séparée)

| # | Règle | Justification |
|---|-------|---------------|
| DT1 | Les données ne transitent pas par tm1-git : utiliser TI export → fichier/flux → import, ou écriture de cellsets REST (`POST /Cubes('c')/tm1.Update` / cellset). | Fait fondateur n°1. |
| DT2 | La structure cible (dims, éléments, cube) doit être livrée **avant** le chargement de données. | Une cellule ne peut viser que des éléments existants. |
| DT3 | `SaveDataAll()` et un **backup** avant tout chargement destructif (pattern `save_data` + `backup_instance` en PrePull). | Récupérabilité. |
| DT4 | Charger uniquement des intersections de **feuilles** (pas de consolidés) ; respecter les types (N/S). | Règles d'écriture TM1. |

---

## 13. Règles transverses de livraison (moteur PA-PROMOTE)

| # | Règle | Justification |
|---|-------|---------------|
| G1 | **Idempotence / upsert** : comparer source vs cible (diff) et n'écrire que les deltas. | Évite erreurs et exécutions coûteuses. |
| G2 | **Validation des dépendances en amont** (dry-run) : produire un rapport « bloquants » (ex. dimensions manquantes) avant toute écriture. | Sécurité — c'est le cœur des règles ci-dessus. |
| G3 | **Ordre topologique** appliqué automatiquement (tri des objets par dépendances) pour la livraison, et **ordre inverse** pour la suppression. | §0. |
| G4 | **Aucune suppression implicite** : la cible ne perd un objet que sur action explicite et confirmée. | Fait fondateur n°2. |
| G5 | **Transaction / rollback logique** : backup avant, journal des opérations, capacité à annuler ; regrouper une livraison en un « lot » traçable. | Récupérabilité + audit. |
| G6 | **Séparer livraison et exécution** : livrer processus/chores ≠ les lancer. | Sécurité. |
| G7 | **Compatibilité de version** source↔cible (V11 vs V12, hiérarchies réelles, ordre des dimensions) vérifiée avant livraison. | Éviter les incompatibilités silencieuses. |
| G8 | **Traçabilité** : chaque livraison consigne qui, quoi, quand, source→cible, résultat (audit log). | Gouvernance. |

---

## 14. Multi-version V11 ⇄ V12 (switch de version)

**Le modèle objet OData v4 est commun à V11 et V12** (mêmes entités : `Cubes`,
`Dimensions`, `Hierarchies`, `Elements`, `Edges`, `Subsets`, `Views`, `Processes`,
`Chores`). Les **payloads d'objets sont donc quasi identiques** : un switch de version
est réaliste si l'on isole les **trois seules différences** derrière une couche
d'abstraction (`VersionProvider`).

| # | Règle | V11 | V12 |
|---|-------|-----|-----|
| VN1 | **Authentification** adaptée par version. | Basic (natif, mode 1) **ou CAM** : en-tête `CAMNamespace base64(user:pass:namespace)` ou `CAMPassport` (modes 2–5, **mode 5 = CAM/Cognos**). HTTPS obligatoire (`UseSSL=T`). | **OIDC / OAuth** bearer (`WWW-Authenticate: openid`, client OAuth). |
| VN2 | **URL de base / scope** adaptée par version. | `https://host:port/api/v1/...` | scopé base de données : `.../api/v1/Databases('tm1-i-<id>')/...`. |
| VN3 | **Sources de données fichier** des TI. | fichiers locaux / ODBC disponibles. | **accès fichier supprimé** → REST only ; reparamétrer/signaler les TI concernés. |
| VN4 | **Accès API complet en V11 indépendant du mode de sécurité** : mode 5 (CAM) donne accès à l'API REST complète via le bon en-tête d'auth ; valider la connexion sur `/api/v1/Cubes` avant toute livraison. | — | — |
| VN5 | **Payload : normaliser** (via le provider) les rares écarts (scope base, métadonnées OData `@odata.etag`, en-têtes `Accept`) ; le moteur de livraison reste agnostique de la version. | — | — |
| VN6 | Interdire/avertir sur une livraison **cross-version incompatible** (ex. hiérarchies réelles, features V12 absentes en V11) après vérification des versions source↔cible (cf. G7). | — | — |

> Autres faits V12 : les REST « C / Java / .Net » et versions internes ne sont **pas**
> supportées (OData only) ; les utilitaires en ligne de commande V11 sont remplacés par
> des endpoints REST ; `ServerName` de la forme `tm1-i-<id>`.

---

## Sources

- [IBM — TM1 model source specification (tm1project)](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=git-tm1-model-source-specification)
- [IBM — TM1 REST API introduction](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=overview-tm1-rest-api-introduction)
- [IBM — Planning Analytics TM1 REST API (v11r2, PDF)](https://www.ibm.com/docs/en/SSD29G_2.0.0/com.ibm.swg.ba.cognos.tm1_rest_api.2.0.0.doc/tm1_rest_api.pdf)
- [IBM — Authenticating and managing sessions (CAMNamespace / CAMPassport)](https://www.ibm.com/docs/en/planning-analytics/2.0.0?topic=api-authenticating-managing-sessions)
- [IBM — Authenticating REST API requests (PA 3.1)](https://www.ibm.com/docs/en/planning-analytics/3.1.0?topic=api-authenticating-rest-requests)
- [TM1 Forum — REST API and Mode 5 Security / CAM](https://tm1forum.com/viewtopic.php?t=16073)
- [IBM — Getting started with TM1 Database 12](https://www.ibm.com/docs/SSD29G_3.1.0/com.ibm.swg.ba.cognos.planning_analytics_engine.2.0.0.doc/pa_engine_getting_started.html)
- [Cubewise — A take on tm1project](https://cubewise-code.github.io/tm1py-tales/2023/tm1-project.html)
- [Cubewise — Preparing your TM1 / PA model for the REST API](https://cubewise.com/blog/preparing-your-tm1-planning-analytics-model-for-the-tm1-rest-api/)
- [ACGI — v11 to v12 migration](https://www.acgi.com/blog/v11-to-v12-migration-moving-to-the-next-generation-pa-server)
- [TM1py — Developer interface (endpoints)](https://tm1py.readthedocs.io/en/latest/api.html)
