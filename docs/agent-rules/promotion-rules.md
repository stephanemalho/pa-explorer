# Règle : promotion / livraison d'objets TM1

## Champ d'application

- `app/promotion/**` (moteur de livraison, à créer en semaine 11)
- Toute feature de livraison / promotion d'objets d'un serveur **source** vers un serveur **cible**

## Règle

Le référentiel `docs/learning/REGLES-LIVRAISON-TM1.md` est la **source de vérité** de la
livraison. **Aucune feature de livraison ne se code sans une règle correspondante écrite et
testée dans ce référentiel (MUST).**

Toute opération de promotion respecte les invariants suivants :

1. **Ordre topologique obligatoire.** La livraison résout les dépendances d'abord (dimensions →
   hiérarchies → éléments → edges → attributs → subsets → cubes → règles/feeders → vues →
   processus → chores → données/sécurité). La **suppression** suit l'**ordre inverse**.
   Référence : `docs/learning/REGLES-LIVRAISON-TM1.md` §0 et G3.
2. **Validation des dépendances avant tout write.** Un objet n'est livré que si **toutes** ses
   dépendances existent déjà côté cible. Produire un rapport de bloquants (ex. « cube non
   livrable : dimensions manquantes côté cible ») **avant** d'écrire. Exemple canonique : règle
   C1. Référence : G2.
3. **Dry-run par défaut, write sur confirmation.** Le mode par défaut simule la livraison et
   liste créations / mises à jour / bloquants **sans écrire**. Toute écriture côté cible exige un
   plan validé explicitement. Référence : G2.
4. **Aucune suppression implicite.** La cible ne perd un objet que sur une action explicite,
   séparée et confirmée par un humain. Une disparition côté source ne déclenche **jamais** de
   suppression côté cible. Référence : fait fondateur n°2 et G4.
5. **Séparer livraison et exécution.** Livrer un processus TI ou un chore ne l'exécute pas. Les
   objets exécutables livrés restent inertes (chores désactivés par défaut) jusqu'à décision
   explicite. Référence : G6, P5, CH2.
6. **Compatibilité de version vérifiée.** La compatibilité source ↔ cible (V11 ⇄ V12, accès
   fichier, hiérarchies réelles) est validée avant livraison, via la couche d'abstraction
   `VersionProvider`. Référence : §14 (VN1–VN6) et G7.

**Interdit :**

- Écrire côté cible sans dry-run validé au préalable.
- Supprimer un objet côté cible de façon implicite ou non confirmée.
- Exécuter un processus / chore livré sans validation explicite.
- Coder une feature de livraison sans règle correspondante dans le référentiel.

**Procédure obligatoire pour toute feature de livraison :**

1. Écrire (ou compléter) la règle métier dans `docs/learning/REGLES-LIVRAISON-TM1.md`.
2. Couvrir la règle par au moins un test (cf. `docs/skills/add_promotion_rule.md`).
3. Implémenter la feature en respectant l'ordre topologique et le dry-run par défaut.
4. Sur toute opération destructive, rester en HITL — proposer, ne pas forcer.

Le moteur de livraison relève d'opérations destructives potentielles : travail en **HITL
strict** (revue de diff systématique), cf. `docs/agent-workflows/sandbox.md` et
`docs/agent-workflows/operating-modes.md`. Décision d'architecture associée :
`docs/learning/decisions.md` — D-016 (app desktop + sidecar + `VersionProvider`).
