# Référentiel sources — Écosystème Anthropic

Sources de référence pour l'utilisation de Claude Code et de l'API Anthropic.

## Sources Claude Code (CLI)

| Page | URL | Contenu |
| --- | --- | --- |
| Documentation principale | `https://code.claude.com/docs/en/` | Point d'entrée de la doc Claude Code |
| Memory et rules | `https://code.claude.com/docs/en/memory` | Mécanisme `.claude/rules/`, CLAUDE.md, auto-memory |
| Features overview | `https://code.claude.com/docs/en/features-overview` | Répartition CLAUDE.md / rules / skills / AGENTS.md |
| Sub-agents | `https://code.claude.com/docs/en/sub-agents` | Agents parallèles, exploration codebase |
| Agent teams | `https://code.claude.com/docs/en/agent-teams` | Orchestration d'équipes d'agents |
| Workflows | `https://code.claude.com/docs/en/workflows` | Workflows déterministes multi-agents |
| Hooks guide | `https://code.claude.com/docs/en/hooks-guide` | Hooks exécutés sur événements outil |
| Skills | `https://code.claude.com/docs/en/skills` | Création et référencement de skills |
| Plugins | `https://code.claude.com/docs/en/plugins` | Extension par plugins |

## Source API Anthropic

| Page | URL |
| --- | --- |
| Documentation API | `https://docs.claude.com` |

## Consignes valables pour tout harness

1. Vérifier la doc officielle de son écosystème avant de proposer une structure
   avancée (hooks, MCP, sub-agents, rules scoping)
2. Ne jamais affirmer qu'une fonctionnalité existe sans la référencer dans
   la documentation officielle
3. La doc fraîche prime sur la mémoire entraînée — les versions évoluent

**Exemple vécu** : la syntaxe du frontmatter des rule files utilise `paths:`
(liste YAML), non `glob:`. Détecté par consultation de la doc officielle lors
de la Phase A S5 (juillet 2026). Toujours vérifier la syntaxe exacte dans la doc.
