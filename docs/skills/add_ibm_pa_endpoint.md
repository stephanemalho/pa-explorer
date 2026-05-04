# Compétence : ajouter un endpoint IBM PA

Cette compétence décrit la procédure standard d'ajout d'un nouvel endpoint 
qui consomme une nouvelle entité de l'API IBM Planning Analytics dans 
PA-Explorer. Elle doit être consultée par Claude Code chaque fois que 
l'utilisateur demande "ajoute un endpoint pour [entité]" où entité est 
une entité IBM PA comme Cubes, Dimensions, Processes, Views, etc.

## Quand utiliser cette compétence

Utiliser cette compétence quand l'utilisateur demande de créer un nouveau 
endpoint qui consomme une nouvelle entité IBM PA. Ne pas utiliser cette 
compétence pour des modifications d'un endpoint existant ou pour des 
features non liées à IBM PA.

## Contexte du pattern existant

Le pattern de référence est l'endpoint Servers, implémenté en semaine 2 
du parcours et constitué des fichiers suivants.

- app/clients/ibm_pa.py contient IBMPAClient avec la méthode get_servers
- app/services/server_service.py contient ServerService avec cache aside
- app/models/server.py contient le modèle Server SQLAlchemy
- app/schemas/server.py contient ServerResponse et ServersListResponse
- app/routers/servers.py contient les routes GET et POST

Toute nouvelle entité doit suivre exactement la même architecture en 
respectant les conventions ci-dessous.

## Étape 1 : Recherche documentaire IBM PA

Avant toute écriture de code, consulter la documentation IBM Planning 
Analytics REST API pour identifier le pattern d'URL exact de l'entité 
demandée. Pour les déploiements SaaS, la structure générale est :

```
GET /api/{tenant_id}/v0/tm1/{contexte}/{Entité}
```

Où le contexte peut inclure le nom du serveur si l'entité est rattachée 
à un serveur (cas des Cubes, Dimensions, Processes). Identifier aussi 
les champs renvoyés par l'API et leur nommage exact (CamelCase 
typiquement comme AcceptingClients, isV12, Href).

Si la documentation IBM consultée est pour une version on-premise (URL 
contenant /3.1.0/ ou /3.0/), noter que la structure exacte SaaS peut 
différer et prévoir un test runtime pour valider l'URL.

## Étape 2 : Étendre le client IBM PA

Dans app/clients/ibm_pa.py, ajouter une nouvelle méthode get_[entité] 
qui suit le pattern de get_servers existant. Si l'entité est rattachée 
à un serveur, la méthode doit prendre server_name comme paramètre.

Exemple structurel pour get_cubes :

```python
_CUBES_PATH = "/api/{tenant_id}/v0/tm1/{server_name}/Cubes"

def get_cubes(self, server_name: str) -> list[dict]:
    url = self._url(self._CUBES_PATH).format(server_name=server_name)
    # même structure de try/except que get_servers
    # même gestion des codes HTTP 401, 403, 5xx
    # même extraction de data["value"]
```

Conserver la même hiérarchie d'exceptions IBMPAError. Les nouvelles 
méthodes ne doivent pas inventer de nouveaux types d'exceptions.

## Étape 3 : Créer le service

Créer app/services/[entité]_service.py avec une classe [Entité]Service 
qui suit le pattern de ServerService.

Le service doit avoir.

- Un constructeur qui injecte db Session et IBMPAClient
- Une méthode get_[entité] qui retourne tuple[list[Model], bool] avec 
  le booléen indiquant si la donnée vient du cache
- Une méthode privée _get_cached_[entité] qui vérifie la fraîcheur du 
  cache via cache_expires_at, en normalisant les datetimes naive vers 
  UTC pour la comparaison
- Une méthode privée _refresh_from_ibm_pa qui appelle le client, fait 
  l'upsert en base, met à jour cache_expires_at et last_synced_at
- Si l'entité est rattachée à un serveur, toutes ces méthodes prennent 
  server_name comme paramètre

Utiliser un TTL configurable via settings, avec une nouvelle variable 
ibm_pa_[entité]_ttl_seconds dans config.py et .env.example.

## Étape 4 : Créer le modèle SQLAlchemy

Créer app/models/[entité].py avec une classe [Entité] qui hérite de Base.

Colonnes obligatoires.

- id integer primary key autoincrement
- name string 255 unique nullable False index True (sauf si l'entité 
  n'a pas de nom unique, auquel cas définir une autre clé naturelle)
- raw_data Text nullable True pour le JSON brut
- last_synced_at DateTime timezone True nullable True
- cache_expires_at DateTime timezone True nullable True
- created_at DateTime timezone True server_default func.now nullable False

Colonnes typées spécifiques à l'entité, à déterminer après lecture du 
payload réel d'IBM PA. Suivre la convention de nommage snake_case en 
Python qui mappe vers les clés CamelCase d'IBM PA.

Si l'entité est rattachée à un serveur, ajouter une colonne 
server_id ForeignKey vers servers.id, ou une colonne server_name 
String si on préfère ne pas avoir de contrainte FK (plus souple pour 
le cache).

## Étape 5 : Créer le schéma Pydantic

Créer app/schemas/[entité].py avec deux classes.

[Entité]Response avec tous les champs du modèle, tous Optional sauf id, 
name et created_at, plus le champ raw_data Optional Any pour le mode 
debug. Utiliser model_config ConfigDict from_attributes True.

[Entité]sListResponse avec servers list[ServerResponse], count int, 
from_cache bool, cache_expires_at Optional datetime.

## Étape 6 : Créer le router

Créer app/routers/[entité]s.py avec.

- L'import de toutes les exceptions IBMPAError du client
- get_ibm_pa_client comme dépendance
- get_[entité]_service comme dépendance qui injecte db et client
- _build_response qui construit la réponse Pydantic depuis les modèles
- _handle_ibm_pa_error qui mappe les exceptions vers les bonnes 
  HTTPException 502 503 504 selon la convention établie
- Une route GET /[entité]s avec query params force_refresh et 
  include_raw, plus server_name si l'entité est rattachée à un serveur 
  (en path param plutôt qu'en query pour la lisibilité de l'URL)
- Une route POST /[entité]s/refresh symétrique

Pour une entité rattachée à un serveur comme les cubes, le pattern 
d'URL sera typiquement /api/v1/servers/{server_name}/cubes plutôt 
que /api/v1/cubes?server_name=X.

## Étape 7 : Monter le router

Modifier app/main.py pour inclure le nouveau router avec 
app.include_router([entité]s.router, prefix="/api/v1").

## Étape 8 : Mettre à jour la configuration

Ajouter dans app/config.py la nouvelle variable de TTL.

Ajouter dans .env.example la même variable avec sa valeur par défaut 
(typiquement 300 en dev).

## Étape 9 : Réinitialiser la base SQLite

En environnement de développement, supprimer pa_explorer.db pour que 
SQLAlchemy recrée la base avec la nouvelle table au prochain démarrage. 
La procédure complète est dans le README à la racine.

## Étape 10 : Tester via Swagger

Suivre le plan de validation manuelle standard.

1. Démarrer uvicorn et vérifier qu'il démarre sans erreur
2. Appeler GET /api/v1/[entité]s avec force_refresh=false et 
   include_raw=true pour voir le payload brut
3. Vérifier que les champs typés sont bien peuplés depuis le raw_data
4. Appeler une seconde fois pour valider que from_cache passe à true
5. Tester force_refresh=true pour valider la couche 3 du cache
6. Si erreur 500, consulter les logs uvicorn ou tester en navigateur 
   direct (rappel : logs invisibles dans PowerShell Windows parfois)

## Pièges connus à anticiper

Datetimes SQLite naive : appliquer la normalisation UTC dans 
_get_cached comme dans server_service.py.

Mapping incomplet : vérifier que tous les champs typés sont bien dans 
_build_response du router ET dans le mapping de _refresh_from_ibm_pa 
du service. C'est la double omission qui a causé le bug accepting_clients 
en semaine 2.

URL avec espaces : si les noms TM1 contiennent des espaces (cubes 
Sales Budget par exemple), encoder l'URL avec urllib.parse.quote ou 
laisser httpx faire l'encodage automatique.

Tenant de démonstration : certains champs documentés peuvent être absents 
du tenant SaaS de démo. Ne pas paniquer, valider via raw_data.

## Référence

Le code source du pattern de référence est dans.

- app/clients/ibm_pa.py pour la classe IBMPAClient
- app/services/server_service.py pour le pattern de service
- app/models/server.py pour le pattern de modèle
- app/schemas/server.py pour le pattern de schéma
- app/routers/servers.py pour le pattern de router

Toute déviation de ce pattern doit être justifiée explicitement.