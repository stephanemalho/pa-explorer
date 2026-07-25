# Règle : discipline git (branche et commits)

## Champ d'application

- Tout le dépôt, toutes les sessions d'agent.

## Règle

### Branche par harness

Chaque harness travaille **uniquement sur sa propre branche**, jamais sur celle
d'un autre harness.

- Claude Code → `claude-code-instructions`
- Codex → `codex-instructions`

Avant toute modification, vérifier la branche courante
(`git branch --show-current`). Si la branche appartient à un autre harness,
**ne pas travailler dessus** : le signaler et attendre d'être placé sur la bonne
branche. La règle canonique worktree/branche vit dans
`docs/agent-workflows/operating-modes.md`.

### Proposition de commit après chaque action (MUST)

Après **chaque action terminée et prête à être poussée**, l'agent DOIT proposer
un message de commit prêt à l'emploi :

- Format Conventional Commits, cohérent avec l'historique du dépôt
  (`type(scope): sujet` — ex. `docs:`, `feat:`, `test:`, `refactor:`, `chore:`).
- Sujet concis, à l'impératif.
- Regrouper par unité logique : plusieurs actions distinctes → plusieurs commits
  proposés, pas un commit fourre-tout.

L'agent **ne commite pas** sans feu vert explicite de l'humain, et **ne pousse
jamais** (`git push`) sans demande explicite. Il propose ; l'humain valide et
pousse. « Prêt à pousser » signifie que le message est finalisé et n'attend que
l'accord humain.
