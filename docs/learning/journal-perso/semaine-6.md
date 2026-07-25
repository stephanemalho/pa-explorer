# Semaine 6 — Pattern Ralph et tâches autonomes

> État : EN_COURS. Ce fichier s'ouvre sur les objectifs de la semaine et sera
> complété au fil de l'eau avec le récit rétrospectif du travail réalisé.

La semaine 6 marque un deuxième changement de nature. Les semaines 1 à 4 ont
construit des fonctionnalités avec un humain dans la boucle à chaque étape. La
semaine 5 a posé l'infrastructure de qualité — tests, feedback loops, Alembic —
qui rend le code fiable. La semaine 6 exploite cette fiabilité pour un nouveau
palier : déléguer à l'agent des tâches délimitées qu'il exécute en boucle, avec
un humain qui supervise plutôt qu'il ne pilote chaque étape.

L'apprentissage central est double. D'une part comprendre le compromis entre
HITL (Human In The Loop) et AFK (Away From Keyboard) : quand rester dans la
boucle et quand s'en retirer sans danger. D'autre part découvrir le pattern
Ralph, une boucle d'orchestration où l'agent pioche des tâches dans un backlog,
les réalise, et vérifie son travail avant de passer à la suivante.

---

## Pourquoi la semaine 5 était le prérequis

Le travail autonome n'est pas gratuit : il n'est sûr que si l'agent dispose
d'un moyen rapide et fiable de savoir s'il vient de casser quelque chose. C'est
exactement ce que la semaine 5 a mis en place.

- **51 tests pytest** qui s'exécutent en ~0,2 s : le filet de sécurité qui dit
  à l'agent, à chaque itération, si son changement est bon.
- **Skill `do_work`** (`docs/skills/do_work.md`) : les vérifications de
  complétion que l'agent doit passer avant de déclarer une tâche terminée.
- **Alembic** : le schéma évolue de façon reproductible, sans manipulation
  manuelle destructive de la base.
- **Règles canoniques** (`docs/agent-rules/`) : les garde-fous architecturaux
  que l'agent ne doit pas franchir, même en autonomie.

Sans ces trois piliers, une boucle autonome amplifierait les erreurs au lieu de
produire de la valeur. C'est la thèse à valider cette semaine.

---

## Concepts à explorer

1. **HITL vs AFK.** Cartographier les tâches PA-Explorer selon deux axes :
   risque (réversible ou non) et clarté de la spécification. Les tâches à faible
   risque et spécification nette sont candidates à l'AFK ; les autres restent en
   HITL.

2. **Le pattern Ralph.** Une boucle simple : lire le backlog → prendre la tâche
   du haut → l'implémenter → lancer les feedback loops → cocher ou signaler →
   recommencer. La difficulté n'est pas la boucle, c'est la définition de tâches
   assez petites et assez précises pour qu'elle converge.

3. **Le sandbox et les limites.** Quelles permissions accorder à un agent qui
   travaille sans surveillance ? Quelles commandes autoriser, lesquelles
   interdire, et comment cadrer le périmètre de fichiers modifiables.

4. **Le backlog comme interface.** Relier l'agent à une liste de tâches — issues
   GitHub ou fichier de backlog versionné — pour qu'il ait une source de vérité
   sur quoi faire ensuite.

---

## Objectifs concrets pour PA-Explorer

Ces objectifs sont une proposition de départ ; le périmètre exact sera arbitré
en début de semaine avec le porteur du projet.

- Constituer un **backlog de petites tâches à faible risque** (par exemple :
  tests des dépendances de sécurité `get_current_user` et
  `get_ibm_pa_client_for_user`, endpoint `logout`, mise en place de ruff) —
  précisément les reports assumés de la semaine 5, qui font un terrain d'essai
  idéal parce qu'ils sont bien cadrés et couverts par les tests.
- Définir un **périmètre de sandbox** explicite pour une session AFK sur ce
  repo.
- Expérimenter une **première boucle Ralph** sur une ou deux de ces tâches, en
  observant où elle réussit et où elle a besoin d'un humain.

---

## Point de départ proposé

État de santé vérifié au démarrage de la semaine : 51 tests au vert, migration
Alembic `5e9bf0f2db8c` en head, feedback loops opérationnels. La base est saine
pour expérimenter l'autonomie.

Première décision à prendre ensemble : **par quelle brique commencer** —
cartographier HITL/AFK et construire le backlog, cadrer le sandbox, ou tenter
directement une boucle Ralph sur une tâche bien délimitée.

---

## Avancement — brique 1 : le backlog

Première brique traitée : le backlog des tâches déléguables, dans
`docs/agent-workflows/backlog.md`. Il pose d'abord le cadre de décision HITL/AFK
sur deux axes — risque (réversibilité et périmètre) et clarté (critère de done
vérifiable automatiquement) — puis classe quatre tâches issues des reports de la
semaine 5.

Résultat de la cartographie :

- **AFK-candidates** : T-01 (tests de `get_current_user`) et T-02 (tests de
  `get_ibm_pa_client_for_user`). Risque faible car elles ne touchent que
  `tests/`, spec nette, vérifiables par pytest seul.
- **HITL** : T-03 (endpoint `POST /auth/logout`, décisions de design à trancher)
  et T-04 (ruff, diff potentiellement transverse au repo).

Enseignement de cette étape : ce ne sont pas les tâches « intéressantes » qui
sont candidates à l'autonomie, mais les tâches **cadrées et auto-vérifiables**.
Les deux tâches de tests, souvent perçues comme secondaires, sont justement les
plus sûres à déléguer — précisément parce que la semaine 5 leur a donné un
feedback loop qui tranche sans jugement humain.

Prochaine brique à choisir : cadrer le sandbox, lancer une boucle Ralph sur
T-01, ou traiter T-01 en HITL classique comme rendu de référence.

---

## Avancement — brique 2 : le sandbox

Deuxième brique traitée : le cadrage du périmètre AFK, avec deux artefacts
complémentaires.

- **Politique neutre** : `docs/agent-workflows/sandbox.md` définit le périmètre
  de commandes (autorisé / interdit), le périmètre de fichiers (`tests/**` pour
  les tâches AFK actuelles, `app/**` en HITL, le reste hors périmètre) et les
  garde-fous adossés à `do_work` et aux règles canoniques.
- **Application Claude Code** : `.claude/settings.json` (versionné) encode la
  partie commandes en `permissions.allow` / `deny`.

Choix de conception important : `.claude/settings.json` s'applique à **toutes**
les sessions Claude Code, pas seulement AFK. On garde donc la config
conservatrice — auto-autoriser le sûr (pytest, git en lecture, alembic en
lecture, ruff check) et interdire dur le catastrophique (`rm -r/-rf`,
`git push`, `git reset --hard`, `git clean`, `alembic downgrade`, lecture/écriture
des secrets). Le périmètre fin de fichiers reste appliqué par la **revue humaine
du diff**, pas par la config partagée, pour ne pas brider le travail supervisé
légitime hors périmètre.

Enseignement de l'étape : un sandbox n'est pas qu'une liste de blocages. C'est
la traduction, en règles exécutables par le harness, de la frontière entre ce
qui est réversible/vérifiable et ce qui ne l'est pas. Le `deny` prime sur
l'`allow` : en cas de doute, c'est l'interdiction qui gagne.

Prochaine brique : lancer une première boucle Ralph sur T-01, ou traiter T-01
en HITL classique comme rendu de référence.
