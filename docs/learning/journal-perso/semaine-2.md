# Semaine 2 — Fondamentaux de Claude Code

La semaine 2 est la première semaine d'implémentation feature complète. Elle introduit
le Plan Mode, le pattern client/service/router, et la première connexion réelle à
IBM Planning Analytics. Le livrable principal est l'endpoint GET /api/v1/servers avec
cache aside, gestion d'erreurs structurée, et débogage des pièges datetime SQLite.

---

## Session du 28 avril 2026 — Semaine 2, implémentation de la feature serveurs

La troisième session est la plus dense du parcours à ce stade. Elle couvre 
la conception, l'implémentation, et le débogage de la première feature métier 
réelle du projet.

La session débute par un apprentissage théorique. Avant d'écrire une ligne de 
code, cinq concepts techniques sont expliqués et intégrés : le pattern client 
API et son rôle d'isolation, la séparation architecturale entre métadonnées 
relationnelles et données volumineuses, le cache aside avec TTL, l'injection 
de dépendance FastAPI via `Depends`, et le format Parquet pour le stockage 
futur des cellules. Ces concepts sont rédigés en prose dans LEARNING.md et 
constituent la base conceptuelle sur laquelle repose toute l'architecture de 
la feature.

Le cycle Plan Mode est utilisé pour la première fois sur une feature 
structurante. Un prompt de planification en neuf sections déclenche une 
recherche documentaire sur l'authentification IBM PA SaaS, une investigation 
qui révèle que les tentatives Postman de la semaine 1 avaient échoué pour une 
raison précise : le username du Basic Auth doit être la chaîne littérale 
`"apikey"` et non l'adresse email de l'utilisateur. Cette découverte valide 
à posteriori la démarche de recherche documentaire avant implémentation.

L'implémentation se déroule sans accroc majeur : client IBM PA avec hiérarchie 
d'exceptions, modèle SQLAlchemy `Server` avec sept colonnes typées plus 
`raw_data`, service cache-aside avec TTL de 300 secondes, router FastAPI avec 
les routes GET /api/v1/servers et POST /api/v1/servers/refresh. Les premiers 
appels à IBM PA retournent des données réelles.

Le débogage commence immédiatement après les premiers tests. Le premier bug 
se manifeste par un HTTP 500 sur le chemin `force_refresh=false`, alors que 
`force_refresh=true` fonctionne correctement. La méthode de diagnostic adoptée 
est celle qui deviendra une habitude : comparer le cas qui marche et le cas 
qui plante pour cerner la zone exacte du problème. La cause est une comparaison 
entre un `datetime` avec timezone (créé avec `timezone.utc`) et un `datetime` 
naïf (retourné par SQLite, qui ne stocke pas les informations de fuseau horaire 
malgré la déclaration `DateTime(timezone=True)` dans le modèle SQLAlchemy). 
Le correctif consiste à détecter les datetimes naïfs lors de la lecture et à 
leur attacher `UTC` via `.replace(tzinfo=timezone.utc)`.

Le deuxième bug est plus subtil : les champs `accepting_clients`, `href` et 
`is_v12` sont présents dans `raw_data` mais restent `null` dans la réponse 
API. Le service écrit bien ces champs en base, mais la fonction `_build_response` 
dans le router les omet lors de la construction des objets `ServerResponse`. 
Les données transitent correctement jusqu'à la base de données et s'arrêtent 
là, silencieusement, sans aucune erreur. C'est une illustration directe du 
type de régression invisible que seuls les tests automatisés permettraient de 
détecter systématiquement — la motivation concrète pour la semaine 5 du 
parcours.

La session se termine par une réflexion sur les migrations SQLAlchemy. Chaque 
modification de schéma en développement nécessite de supprimer `pa_explorer.db` 
pour que `create_all` recrée la table avec le bon schéma. C'est une pratique 
acceptable en développement sur des données rechargeables, et radicalement 
inacceptable en production où Alembic prend le relais.

À la fin de la semaine 2, le projet expose une API REST fonctionnelle connectée 
à IBM PA, avec un cache local, une gestion d'erreurs en sept catégories, et 
une architecture en couches prête à accueillir les prochaines entités.
