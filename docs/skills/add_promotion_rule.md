# Compétence : ajouter une règle de livraison

Ce skill décrit comment ajouter une règle de livraison de façon cohérente : d'abord
la **documenter** dans le référentiel, puis l'**implémenter**, puis la **couvrir par
un test**. Aucune feature de livraison ne se code sans une règle correspondante
écrite et testée. Elle doit être consultée chaque fois qu'une tâche touche au moteur
de promotion (`app/promotion/`).

→ Règle complète : `docs/agent-rules/promotion-rules.md`

> Squelette — sections à compléter en semaine 11 (moteur de livraison).

---

## Quand utiliser cette compétence

> À compléter : quand une nouvelle contrainte de livraison apparaît (dépendance,
> ordre, cas destructif) et doit devenir une règle testable.

## Étape 1 : Écrire la règle dans le référentiel

> À compléter : ajouter ou compléter la règle dans
> `docs/learning/REGLES-LIVRAISON-TM1.md` (identifiant D/H/M/A/S/C/R/V/P/CH/X/DT/G,
> justification, place dans l'ordre topologique §0).

## Étape 2 : Implémenter la règle

> À compléter : code dans `app/promotion/`, respect de l'ordre topologique et du
> dry-run par défaut, aucune suppression implicite, séparation livraison ≠ exécution.

## Étape 3 : Couvrir la règle par un test

> À compléter : au moins un test par règle, avec un faux IBM PA (cf.
> `docs/skills/test_new_service.md`).

## Pièges connus à anticiper

> À compléter.

## Référence

- `docs/agent-rules/promotion-rules.md` — règle canonique (invariants)
- `docs/learning/REGLES-LIVRAISON-TM1.md` — référentiel (source de vérité)
- `docs/skills/test_new_service.md` — tester un service avec un faux IBM PA
- `docs/learning/decisions.md` — D-016 (architecture de livraison)
