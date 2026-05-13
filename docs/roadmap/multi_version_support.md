# Support multi-version IBM PA TM1

Ce document décrit la vision long terme pour le support simultané des 
versions V11 et V12 d'IBM Planning Analytics dans PA-Explorer. Il n'est 
pas un plan d'implémentation immédiat mais une note de direction pour 
orienter les décisions architecturales en cours et préparer le terrain 
pour l'implémentation future.

## Statut

Vision documentée. Implémentation prévue dans les semaines 5 à 8 du 
parcours d'apprentissage Claude Code, après stabilisation de 
l'authentification et préparation architecturale par introduction d'un 
pattern d'adaptateur.

## Motivation métier

Les déploiements TM1 en entreprise coexistent souvent en V11 on premise 
et V12 SaaS, soit pour des raisons de migration progressive, soit pour 
des raisons d'usage différencié. Un outil de monitoring de performance 
des cubes TM1 doit pouvoir adresser les deux versions sans imposer aux 
utilisateurs de choisir entre deux applications distinctes.

PA-Explorer doit donc à terme exposer une expérience unifiée. 
L'utilisateur sélectionne sa version dans l'interface, fournit les 
credentials adaptés, et navigue dans les données TM1 sans se soucier 
des différences techniques sous-jacentes.

## Les deux contextes techniques à supporter

### IBM PA SaaS V12, supporté actuellement

URL pattern.
https://<base_url>/api/<tenant_id>/v0/tm1/<server_name>/<entity>

Authentification. Basic Auth avec username littéral apikey et clé 
API en password.

Découverte des serveurs. Via /api/<tenant_id>/v0/tm1/Servers.

C'est le contexte actuellement implémenté dans PA-Explorer.

### IBM PA V11 on premise, à supporter ultérieurement

URL pattern direct vers le serveur TM1.
https://<tm1_host>:<http_port>/api/v1/<entity>

Découverte des serveurs via le TM1 Admin Server, qui tourne sur un 
hôte et un port différents.
http://<admin_host>:5895/api/v1/Servers
https://<admin_host>:5898/api/v1/Servers

Authentification variable selon IntegratedSecurityMode du fichier 
tm1s.cfg.

Mode 1, Basic Auth TM1 standard avec username et password TM1.

Mode 5, authentification CAM Cognos qui est le plus probable en 
contexte entreprise. Deux variantes possibles. Authorization CAMNamespace 
avec base64 de user password namespace. Ou Authorization CAMPassport 
avec un passport déjà obtenu.

Le mode 5 est le plus complexe à implémenter et probablement le plus 
fréquent en entreprise.

## Stratégie architecturale envisagée

Le code actuel mélange routes FastAPI et logique IBM PA V12 dans le 
client IBMPAClient. Pour préparer le support multi-version, le code 
doit être refactorisé selon le pattern d'adaptateur.

### Couche métier abstraite

Les routes FastAPI manipulent des concepts métier abstraits comme 
Server, Cube, Dimension. Elles ne connaissent ni l'URL exacte ni le 
mode d'authentification. Elles déléguent à une interface abstraite.

### Adaptateurs spécifiques

Deux implémentations de l'interface coexistent.

Un adaptateur V12 qui encapsule la logique actuelle d'appel à la 
gateway SaaS avec apikey.

Un adaptateur V11 qui encapsule la logique d'appel direct au serveur 
TM1 avec gestion des modes d'authentification.

### Sélection à l'exécution

Le choix de l'adaptateur se fait à partir de la session utilisateur. 
Lors de la création de session, l'utilisateur indique sa version et 
fournit les credentials adaptés. Le backend instancie le bon 
adaptateur pour cette session.

## Implications sur les décisions actuelles

### Modèle de session utilisateur

La structure de la session utilisateur doit pouvoir stocker des 
credentials de natures différentes selon la version. Pour V12 ce sont 
tenant_id et api_key. Pour V11 ce sont host, port, et selon le mode 
soit username plus password, soit camnamespace, soit campassport.

Cette flexibilité doit être anticipée dans le modèle User dès la 
semaine 4, même si seul le cas V12 est implémenté initialement.

### Stockage du raw_data

Le pattern schema on read avec raw_data documenté en D-008 est 
particulièrement précieux pour la double version, parce que les 
payloads V11 et V12 peuvent différer sur certains champs. Stocker le 
raw brut permet de gérer les divergences au point de lecture sans 
contrainte structurelle.

### Découverte des serveurs

L'endpoint actuel POST /api/v1/servers/refresh fait un appel direct 
à la gateway V12. Pour V11, l'équivalent passe par l'Admin Server. 
L'abstraction doit prévoir une méthode discover_servers de l'interface 
qui retourne une liste homogène quel que soit le mode.

## Planning indicatif

Semaine 4. Implémentation de l'authentification utilisateur en restant 
sur V12. Anticipation du multi-version dans la structure de la session.

Semaine 5 et 6. Refactoring vers un pattern d'adaptateur sans changer 
le comportement fonctionnel. Introduction d'une couche d'abstraction 
TM1Source ou équivalent entre les routes et le client.

Semaine 7 et 8 ou ultérieurement. Implémentation de l'adaptateur V11 
avec gestion du mode CAM. Tests de basculement V11 V12 à chaud sur 
une même session utilisateur.

## Risques et points d'attention

### Complexité de l'authentification CAM

Le mode CAM en V11 est nettement plus complexe que apikey en V12. Il 
implique potentiellement la gestion de passports renouvelables, de 
namespaces multiples, et de cookies. À investiguer en profondeur 
avant de figer l'architecture de l'adaptateur V11.

### Tests d'intégration

Disposer d'un environnement V11 de test sera nécessaire pour valider 
l'adaptateur V11. À anticiper, idéalement via un environnement de 
démo accessible ou une machine virtuelle de développement.

### Pas de dépendance directe entre adaptateurs

Les deux adaptateurs ne doivent partager que l'interface, pas du code 
d'implémentation. Sinon un changement V12 risque de casser V11 et 
réciproquement.