# Suite du parcours d'apprentissage — PA-Explorer devient livreur (semaines 9 → 12)

> Prolongement du parcours PA-Explorer (semaines 1–8) une fois la semaine 8
> terminée. Même format que `docs/learning/README.md` : chaque semaine mêle un objectif
> pédagogique Claude Code et un livrable concret sur le projet fil rouge. La suite
> transforme **PA-Explorer** en une application **desktop téléchargeable (.exe)** qui
> **livre** des objets TMA / Planning Analytics **V12** d'un serveur source vers un
> serveur cible, en **s'inspirant du repo GitHub PA-PROMOTE** (qui a déjà avancé sur
> les features de livraison).

---

## Contexte et bascule : PA-Explorer, de la lecture à la livraison

Jusqu'à la semaine 8, PA-Explorer est une API FastAPI qui **lit** un modèle IBM PA
(serveurs, cubes, dimensions, processus). La suite étend **le même projet PA-Explorer** :
passer de la **lecture** à la **livraison** (promotion source → cible), et d'une API à
une **app desktop** utilisable par un consultant TM1 sans terminal. Le nom du projet
reste PA-Explorer ; « livraison » / « promotion » désigne la nouvelle capacité.

**Rôle du repo PA-PROMOTE :** c'est une **source d'inspiration** (référence de code sur
les features de livraison déjà avancées), **pas** le repo cible. On construit sur
PA-Explorer et on s'inspire de PA-PROMOTE — voir la gap analysis en semaine 9, étape 0.

**Deux briques réutilisées :** le backend FastAPI existant (client `httpx`, auth IBM PA,
pattern cache-aside, services `ServerService`/`CubeService`/`DimensionService`) devient
le **cœur du moteur de livraison** ; on l'empaquette en **sidecar** derrière une UI.

**Le référentiel qui pilote la suite :** `docs/learning/REGLES-LIVRAISON-TM1.md`
(les règles de livraison à tous les niveaux). Aucune feature de livraison ne se code
sans qu'une règle correspondante y soit écrite et testée.

### Décisions de stack (à figer en semaine 9)

- **App desktop :** **Electron + React + IBM Carbon Design System** (`@carbon/react`),
  pour un rendu proche de PAW/PA. Empaquetage `.exe` via `electron-builder` (NSIS).
- **Backend :** FastAPI existant embarqué en **sidecar** (processus Python packagé
  avec PyInstaller, lancé par le main process Electron ; IPC via HTTP localhost).
- **Moteur de livraison :** nouveau module `app/promotion/` (diff, tri topologique,
  validation des dépendances, exécution ordonnée, journal/rollback).
- **Cible V12 :** API OData uniquement, auth OIDC/OAuth, endpoints scopés par base.
- **Support multi-version V11 ⇄ V12 :** un serveur source ou cible peut être en V11
  **ou** V12 → couche d'abstraction (voir encadré).

### Couche d'abstraction de version (V11 ⇄ V12) — `VersionProvider`

Constat validé sur la doc IBM : **V11 et V12 exposent le même modèle objet OData v4**
(`/api/v1/Cubes`, `/Dimensions`, `/Processes`, `/Chores`, hiérarchies, subsets, vues…).
Les **payloads d'objets sont donc quasi identiques**. On peut proposer un **switch de
version** à condition d'isoler les trois seules vraies différences derrière une interface
commune :

| Ce qui change | V11 | V12 |
|---|---|---|
| **Authentification** | Basic (natif, mode 1) **ou CAM** : `CAMNamespace base64(user:pass:namespace)` / `CAMPassport` (modes 2–5, dont **mode 5 = CAM/Cognos**). HTTPS (`UseSSL=T`). | **OIDC / OAuth** : bearer token, `WWW-Authenticate: openid`, client OAuth. |
| **URL de base / scope** | `https://host:port/api/v1/...` | scopé par base : `.../api/v1/Databases('tm1-i-<id>')/...` (endpoints par base de données). |
| **Accès fichier (TI, `Files` tm1project)** | disponible (chemins locaux, ODBC). | **supprimé** → tout par REST. |

**Conception.** Une interface `VersionProvider` (ou `Connector`) avec deux
implémentations `V11Provider` / `V12Provider` exposant une API uniforme au moteur de
livraison : `base_url(objectPath)`, `auth_headers()`, `normalize_payload(obj)`,
`supports_file_datasource()`. Le moteur de livraison et l'explorateur ne connaissent
que l'interface — ils ignorent la version. **À vérifier en tracer bullet (S9) :** que
la même requête `GET Cubes` renvoie une structure exploitable de façon identique sur une
instance V11 (mode 5 CAM) et une instance V12 (OAuth), avant de généraliser.

**Prérequis côté V11 pour le mode 5.** L'accès REST complet ne dépend pas du mode de
sécurité, seulement du builder d'en-tête d'auth : en mode 5 il faut le namespace CAM et
un utilisateur autorisé, en HTTPS. Valider en S9 qu'une instance V11 mode 5 répond bien
sur `/api/v1/Cubes` avec l'en-tête `CAMNamespace` (ou passport) avant d'implémenter le
provider.

---

## Semaine 9 — Fondations PA-PROMOTE : desktop shell + double connexion [À VENIR]

**Objectif pédagogique.** Utiliser Claude Code pour *bootstrapper une nouvelle
surface* (Electron + Carbon) au-dessus d'un backend existant, sans casser l'API :
Plan Mode pour l'architecture desktop, subagents pour explorer `PA-PROMOTE`, tracer
bullet pour valider l'empaquetage `.exe` de bout en bout avant d'investir.

**Étape 0 — Réconciliation.** Faire explorer le repo `PA-PROMOTE` par un subagent :
inventorier les features de livraison déjà présentes, extraire ce qui est réutilisable,
et produire un `docs/pa-promote/gap-analysis.md` (ce qui existe vs ce qui manque vs les
règles de `REGLES-LIVRAISON-TM1.md`).

**Livrables.**
- Décision d'architecture D-016 : Electron + Carbon + FastAPI sidecar (documentée dans `decisions.md`).
- Squelette Electron (`desktop/`) + React + `@carbon/react`, thème `g10`/`g100`, `UIShell` (header + nav latérale).
- Empaquetage `.exe` minimal fonctionnel (tracer bullet) : l'app démarre, lance le sidecar, ping le health endpoint.
- Écran **Connexions** : configurer *deux* serveurs (source, cible), chacun avec un **sélecteur de version (V11 / V12)** — URL base, base de données, auth (Basic/CAM `CAMNamespace`/CAMPassport en V11, OIDC/OAuth en V12). Secrets chiffrés (réutiliser le service de chiffrement existant).
- Interface `VersionProvider` + `V11Provider` / `V12Provider` (auth, URL de base, normalisation payload, capacité fichier). Tracer bullet : même `GET Cubes` exploitable sur V11 mode 5 CAM et V12 OAuth.
- Skill Claude Code `add_carbon_screen.md` (comment ajouter un écran Carbon cohérent).

---

## Semaine 10 — Exploration du modèle façon IBM PA (arbre d'objets) [À VENIR]

**Objectif pédagogique.** Concevoir un PRD exécutable multi-phases pour une feature
« large » (l'explorateur d'objets), et le découper sur plusieurs fenêtres de contexte.
Réinvestir le pattern feedback-loop (semaine 5) : tests d'abord sur le mapping objets.

**Livrables.**
- Endpoints backend d'inventaire : lister **cubes, dimensions, processus, chores** + leurs enfants (hiérarchies, éléments, edges, subsets, vues, règles, feeders) via l'API OData, avec cache-aside.
- UI **arbre d'objets** type PA : `TreeView` Carbon, chargement paresseux (lazy) des enfants, recherche/filtre, icônes par type d'objet. « Exactement comme sur IBM PA ».
- Panneau de détail par objet (dimensions d'un cube, membres d'une hiérarchie, source d'un processus, processus d'un chore).
- Tests des services d'inventaire avec un faux IBM PA (dans la lignée des 51 tests existants).
- MAJ `ibm_pa.md` : endpoints d'inventaire découverts, structures de réponse, pièges V12.

---

## Semaine 11 — Moteur de livraison : diff, dépendances, dry-run [À VENIR]

**Objectif pédagogique.** Le cœur technique et le plus risqué : implémenter les
**règles de livraison** comme code testable. Utiliser Claude Code en HITL strict
(revue de diff systématique) car on touche à des opérations destructives potentielles.
Chaque règle de `REGLES-LIVRAISON-TM1.md` = au moins un test.

**Livrables.**
- Module `app/promotion/` : (1) **diff** source↔cible par type d'objet ; (2) **graphe de dépendances** + **tri topologique** (ordre canonique §0 des règles) ; (3) **validateur de dépendances** produisant un rapport de bloquants (ex. « cube X non livrable : dimensions A, B manquantes côté cible »).
- **Dry-run** obligatoire : simule la livraison, liste créations/mises à jour/bloquants, **sans écrire**.
- UI **Sélection & Plan de livraison** : sélectionner des objets dans l'arbre → écran de plan (ordre d'exécution, dépendances entêtées, avertissements Carbon `InlineNotification`).
- Journalisation des lots + squelette rollback logique (backup avant, log d'opérations).
- Suite de tests couvrant les règles D/H/M/C/CH/G (dimensions manquantes, chore avant process, idempotence, aucune suppression implicite…).
- Skill `add_promotion_rule.md` : comment ajouter une règle (doc + code + test) de façon cohérente.

---

## Semaine 12 — Exécution, sécurité de déploiement, packaging & bilan [À VENIR]

**Objectif pédagogique.** Passer du prototype au livrable installable. Écrire un skill
« Improve My Codebase » orienté PA-PROMOTE, soigner l'empaquetage et la robustesse
(la partie qu'une IA — et un humain — doivent pouvoir maintenir). Bilan réflexif.

**Livrables.**
- **Exécution ordonnée** de la livraison (structure) avec barre de progression Carbon, gestion d'erreurs par objet, arrêt/reprise, **séparation livraison ≠ exécution** (les TI/chores livrés ne se lancent pas tout seuls).
- Piste **données/sécurité** minimale : orchestration export TI → import TI (attributs/sécurité), avec `SaveDataAll` + backup en pré-pull.
- **Journal d'audit** consultable dans l'app (qui/quoi/quand/source→cible/résultat).
- Packaging final : `.exe` signé (si certificat), auto-update optionnel, doc d'installation utilisateur.
- Skill `improve_my_codebase.md` adapté PA-PROMOTE + passage ruff/pre-commit (dette reportée de la semaine 5).
- Bilan du parcours (journal) : de la lecture PA-Explorer à la livraison PA-PROMOTE.

---

## Roadmap produit PA-PROMOTE (vue jalons, complémentaire aux semaines)

| Jalon | Contenu | Semaine cible |
|-------|---------|---------------|
| **M0 — Shell** | Electron+Carbon, sidecar FastAPI, `.exe` qui démarre, double connexion source/cible | S9 |
| **M1 — Explorer** | Arbre d'objets type PA (cubes/dims/process/chores + enfants) | S10 |
| **M2 — Dry-run** | Diff + dépendances + validation bloquants, aucun write | S11 |
| **M3 — Deliver** | Exécution ordonnée de la structure, journal, rollback logique | S12 |
| **M4 — Data & Security** | Piste données/sécurité via TI, backups | S12+ |
| **M5 — Hardening** | Signature .exe, auto-update, audit, perfs, packaging distribuable | post-parcours |

---

## Fils rouges de gouvernance (valables sur les 4 semaines)

1. **Les règles avant le code.** `REGLES-LIVRAISON-TM1.md` est la source de vérité ;
   toute feature de livraison référence la (les) règle(s) qu'elle implémente.
2. **Dry-run par défaut, write sur confirmation.** Jamais d'écriture côté cible sans
   plan validé (règle G2/G4).
3. **HITL sur le moteur de livraison** (opérations destructives) ; AFK toléré seulement
   sur tests et UI non critiques (cf. `docs/agent-workflows/sandbox.md`).
4. **Compatibilité V11/V12** vérifiée à chaque connexion (auth, OData-only, accès fichier).
5. **Un worktree/branche par agent** (cf. `docs/agent-workflows/operating-modes.md`) si travail parallèle.
