# Backlog des tâches déléguables — Semaine 6

Ce fichier est la **source de vérité** des tâches délimitées candidates au
travail autonome (pattern Ralph). Il complète :

- `docs/agent-workflows/operating-modes.md` — les modes Explore/Plan/Implement/Review/Validate
- `docs/skills/do_work.md` — les vérifications de complétion avant de cocher une tâche

Chaque tâche est cadrée pour qu'un agent puisse la prendre en haut de pile, la
réaliser, et vérifier lui-même son travail via un feedback loop automatique.

---

## Cadre de décision HITL vs AFK

Une tâche se classe selon deux axes.

- **Axe risque** — réversibilité et périmètre du changement.
  - *Faible* : n'ajoute que des tests, ne touche pas le code applicatif.
  - *Moyen* : introduit un comportement applicatif nouveau (router + service).
  - *Large* : changement transverse au repo (ex. reformatage massif).
- **Axe clarté** — le critère de « done » est-il net et **vérifiable
  automatiquement** par un feedback loop (pytest, ruff) sans jugement humain ?

Règle :

- **AFK-candidate** = risque *faible* **ET** spec nette **ET** vérifiable
  automatiquement. L'agent peut travailler sans supervision étape par étape ;
  les tests disent seuls si le résultat est bon.
- **HITL** = tout le reste : dès qu'il y a une décision de design, un diff large
  à relire, ou un critère non automatisable, l'humain reste dans la boucle.

---

## Backlog priorisé

| # | Tâche | Risque | Classement | Périmètre fichiers |
|---|---|---|---|---|
| T-01 | Tests de `get_current_user` | Faible | **AFK-candidate** | `tests/` seul |
| T-02 | Tests de `get_ibm_pa_client_for_user` | Faible | **AFK-candidate** | `tests/` seul |
| T-03 | Endpoint `POST /auth/logout` | Moyen | **HITL** | `app/` + `tests/` |
| T-04 | Outillage ruff (lint + format) | Large | **HITL** | racine + tout le repo |

Ordre recommandé : **T-01 → T-02 → T-03 → T-04**. Les deux premières sont le
terrain d'essai idéal d'une première boucle Ralph (aucun risque applicatif) ;
les deux suivantes servent à observer où l'humain redevient nécessaire.

---

## T-01 — Tests de `get_current_user` · AFK-candidate

**Contexte.** [`app/security/dependencies.py:20`](../../app/security/dependencies.py#L20)
valide la session à partir du cookie `session_token`. Aucun test ne la couvre.

**Spec — chemins à couvrir :**

1. Pas de cookie `session_token` → `HTTPException` 401.
2. Cookie présent mais session inexistante en base → 401.
3. Session existante mais expirée → 401.
4. Session valide mais `User` introuvable → 401.
5. Chemin nominal : session valide → l'`User` est retourné **et** `last_used_at`
   est mis à jour.

**Piège attendu.** La comparaison d'expiration normalise le datetime naïf de
SQLite (`docs/agent-rules/datetime-utc.md`) : construire les sessions de test
avec des `expires_at` explicites, aware et naïfs, pour valider les deux cas.

**Technique de test.** Réutiliser l'infra pytest de la S5 : base SQLite isolée +
`dependency_overrides` de `get_db` sur un endpoint de test protégé par la
dépendance. (Alternative : appel direct de la fonction avec une `Request`
factice — à arbitrer par l'implémenteur.)

**Fichiers.** `tests/test_security_dependencies.py` (nouveau).

**Done.** Nouveaux tests au vert **et** suite globale toujours verte
(`pytest -q`).

**Règles applicables.** `no-test-workarounds.md`, `datetime-utc.md`.

---

## T-02 — Tests de `get_ibm_pa_client_for_user` · AFK-candidate

**Contexte.** [`app/security/dependencies.py:44`](../../app/security/dependencies.py#L44)
déchiffre les credentials et construit un `IBMPAClient` pour la version V12,
sinon renvoie 501.

**Spec — chemins à couvrir :**

1. `ibm_pa_version == "V12"` → un `IBMPAClient` est retourné, construit avec le
   `tenant_id` et l'`api_key` issus du déchiffrement.
2. Version non supportée (ex. `"V11"`) → `HTTPException` 501.

**Technique de test.** `patch` d'`IBMPAClient` **dans `app.security.dependencies`**
(technique 2 de la S5 : on patche là où l'objet est utilisé) pour vérifier les
arguments de construction sans instancier le vrai client. Fabriquer un `User`
avec `credentials_encrypted` produit par la vraie fonction `encrypt`.

**Fichiers.** `tests/test_security_dependencies.py`.

**Done.** Tests au vert, suite globale verte.

**Règles applicables.** `no-test-workarounds.md`, `ibm-pa-auth.md`,
`architecture-layers.md`.

---

## T-03 — Endpoint `POST /auth/logout` · HITL

**Contexte.** Il n'existe aucune route de déconnexion. La session est une ligne
`UserSession` désignée par le cookie `session_token`.

**Spec.** Invalider la session courante : lire le cookie, supprimer (ou marquer
révoquée) la `UserSession` correspondante, effacer le cookie côté réponse.

**Décisions de design à trancher avec l'humain (raison du classement HITL) :**

- Suppression dure de la ligne **ou** révocation douce (`revoked_at`) ?
- Comportement idempotent si aucun cookie / session déjà expirée : 200 ou 401 ?
- Code de retour et schéma de réponse.

**Contrainte architecture.** La logique de suppression/révocation vit dans
`AuthService` (ex. `revoke_session(token)`), **jamais** dans le router
(`architecture-layers.md`). Le router reste fin.

**Fichiers.** `app/services/auth_service.py`, `app/routers/auth.py`,
`app/schemas/auth.py`, `tests/test_auth_endpoints.py`.

**Done.** Test démontrant qu'après logout, un appel à une route protégée avec
le même cookie renvoie 401 ; cookie effacé. Suite globale verte.

**Règles applicables.** `architecture-layers.md`, `no-test-workarounds.md`.
Voir aussi la dette D-010 (atomicité de `verify_magic_link`) dans
`docs/learning/decisions.md` — garder la transaction simple.

---

## T-04 — Outillage ruff (lint + format) · HITL

**Contexte.** ruff n'est ni installé ni configuré.

**Spec.**

1. Ajouter `ruff` aux dépendances de développement.
2. Configurer ruff (`pyproject.toml` ou `ruff.toml`) : règles activées/ignorées.
3. `ruff check` d'abord en **mesure seule** pour évaluer l'ampleur, puis
   corriger les erreurs auto-fixables.
4. `ruff format` : **ne pas** l'appliquer en masse sans revue du diff.

**Raison du classement HITL.** Un `ruff format` peut toucher tout le repo (diff
large à relire) ; le choix des règles est une décision. Une fois la config
figée, la sous-tâche « corriger les lint auto-fixables » pourra devenir AFK.

**Fichiers.** `requirements.txt` (ou `requirements-dev.txt`), `pyproject.toml`,
puis potentiellement de nombreux fichiers.

**Done.** `ruff check` passe (ou baseline documentée dans decisions.md) ; suite
de tests toujours verte.

**Règles applicables.** —

---

## Definition of Done commune

Avant de cocher **toute** tâche, passer les vérifications bloquantes du skill
`docs/skills/do_work.md` — en particulier :

- `pytest -q` : suite complète au vert (pas de test contourné, cf.
  `no-test-workarounds.md`).
- Respect du pattern client → service → router et des règles `docs/agent-rules/`.
- Datetimes normalisés en UTC là où c'est pertinent.

---

## Prochaine étape

Le backlog est posé. Trois suites possibles pour la semaine 6 :

- **Cadrer le sandbox** — définir le périmètre AFK (commandes/fichiers autorisés)
  avant de lâcher un agent sur T-01/T-02.
- **Lancer une première boucle Ralph** sur T-01 (la plus sûre) pour observer la
  mécanique en conditions réelles.
- **Traiter T-01 en HITL classique** d'abord, pour disposer d'un modèle de
  référence auquel comparer le rendu autonome.
