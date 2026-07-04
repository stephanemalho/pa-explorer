# Référentiel sources — Écosystème OpenAI

Sources de référence pour l'utilisation de Codex et de l'API OpenAI dans ce
projet.

## Sources Codex

| Page | URL | Quand consulter |
| --- | --- | --- |
| Documentation principale Codex | `https://developers.openai.com/codex/` | Point d'entrée général pour Codex |
| Custom instructions avec AGENTS.md | `https://developers.openai.com/codex/guides/agents-md` | Chargement automatique des instructions projet, ordre de précédence, `AGENTS.override.md`, fallbacks |
| Config basics | `https://developers.openai.com/codex/config-basic` | Emplacement de `config.toml`, précédence des couches, paramètres courants |
| Advanced Config | `https://developers.openai.com/codex/config-advanced` | Configuration avancée projet, `.codex/config.toml`, hooks, profiles, providers |
| Configuration Reference | `https://developers.openai.com/codex/config-reference` | Vérifier les clés exactes supportées par `config.toml` |
| Agent Skills | `https://developers.openai.com/codex/skills` | Créer ou adapter un workflow réutilisable sous forme de skill |
| Hooks | `https://developers.openai.com/codex/hooks` | Ajouter des validations de cycle de vie ou automatisations de session |
| Rules | `https://developers.openai.com/codex/rules` | Contrôler les commandes exécutables hors sandbox, sans confondre avec des règles métier par chemin |
| Subagents | `https://developers.openai.com/codex/subagents` | Définir ou utiliser des agents spécialisés parallèles |
| Model Context Protocol | `https://developers.openai.com/codex/mcp` | Connecter Codex à des outils ou sources externes |
| Import to Codex | `https://developers.openai.com/codex/import` | Migrer une configuration existante depuis un autre agent vers Codex |

## Sources API OpenAI

| Page | URL | Quand consulter |
| --- | --- | --- |
| Documentation API | `https://developers.openai.com/api/` | APIs OpenAI, modèles, paramètres et guides de développement |
| Plateforme OpenAI | `https://platform.openai.com/docs` | Référence plateforme et console développeur |

## Consignes valables pour tout harness

1. Vérifier la doc officielle de son écosystème avant de proposer une structure
   avancée (hooks, MCP, sub-agents, rules scoping)
2. Ne jamais affirmer qu'une fonctionnalité existe sans la référencer dans
   la documentation officielle
3. La doc fraîche prime sur la mémoire entraînée — les versions évoluent

## Notes PA-Explorer pour Codex

- `AGENTS.md` est le point d'entrée natif pour les instructions durables du
  projet.
- `.codex/config.toml` porte la configuration projet Codex quand le dépôt est
  approuvé comme trusted.
- `.agents/skills/` porte les workflows Codex réutilisables propres au repo.
- Les `rules/` Codex documentées contrôlent les commandes hors sandbox ; elles
  ne remplacent pas les règles métier scopées par chemin de `.claude/rules/`.
