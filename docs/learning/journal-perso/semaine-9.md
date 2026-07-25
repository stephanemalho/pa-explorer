# Semaine 9 — Fondations PA-PROMOTE

> État : À VENIR. Ce fichier ouvre le cap PA-PROMOTE (livraison) et sera
> complété au fil de l'eau avec le récit rétrospectif du travail réalisé.

La semaine 9 marque un troisième changement de nature. Les semaines 1 à 5 ont
construit et fiabilisé une API qui **lit** un modèle IBM PA. La semaine 6 a posé
le cadre du travail délégué (HITL/AFK, sandbox). Les semaines 9 à 12 changent la
finalité du projet : PA-Explorer passe de la **lecture** à la **livraison**, en
promouvant des objets TM1 d'un serveur source vers un serveur cible, sous la forme
d'une application desktop téléchargeable.

---

## Session du 25 juillet 2026 — Cap PA-PROMOTE et démarrage de la semaine 9

Ouverture du cap PA-PROMOTE. L'objectif n'est plus d'exposer un modèle, mais de le
**livrer** : reprendre la logique de promotion d'objets TMA / Planning Analytics
V12 en s'inspirant du repo GitHub PA-PROMOTE, qui reste une source d'inspiration
(référence de code) et non le repo cible. On construit sur PA-Explorer.

La stack est figée par la décision D-016 : une app desktop Electron + React + IBM
Carbon Design System, avec le backend FastAPI existant embarqué en sidecar, et une
couche d'abstraction `VersionProvider` pour absorber les différences entre serveurs
V11 (Basic/CAM mode 5) et V12 (OIDC/OAuth, endpoints scopés par base, sans accès
fichier). Le référentiel `docs/learning/REGLES-LIVRAISON-TM1.md` devient la source
de vérité : aucune feature de livraison ne se code sans une règle correspondante
écrite et testée. La règle canonique `docs/agent-rules/promotion-rules.md` en fixe
les invariants — ordre topologique, dry-run par défaut, aucune suppression
implicite, séparation livraison ≠ exécution, validation des dépendances avant tout
write.

Premier jalon visé (M0) : le shell desktop qui démarre, lance le sidecar et répond
au health endpoint, l'écran de double connexion source/cible avec sélecteur de
version, et un tracer bullet prouvant qu'un même `GET Cubes` est exploitable de
façon identique en V11 (mode 5 CAM) et en V12 (OAuth) avant de généraliser. Une
étape 0 de gap analysis du repo PA-PROMOTE précède le code, pour cartographier ce
qui est réutilisable face aux règles du référentiel.

Prochaine étape : lancer l'exploration de PA-PROMOTE (subagent en lecture seule) et
poser le squelette `desktop/`.
