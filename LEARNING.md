# Session d'apprentissage Py

## Lancement du projet le 22/04/2026

Premières impression avec Claude Code, assisté par Claude AI afin de guider l'apprentissage sur ce projet file rouge planning analytucs.

Première impréssion, la structure a l'air solide, le lancement ce fait bien. la doc sur swagger à été lancé sans soucis. J'ai bloqué sur : postman n'à pas été réussi car j'ai mal configuré les variable Auth mais j'ai compris le principe et je préfère me focaliser pour le moment sur l'installation et l'implémentation du projet depuis VS Code.

```
pa-explorer/
├── app/
│   ├── main.py          # Point d'entrée FastAPI
│   ├── config.py        # Configuration via .env
│   ├── database.py      # SQLAlchemy engine et session
│   ├── models/          # Modèles ORM
│   ├── routers/         # Endpoints par domaine
│   └── schemas/         # Schémas Pydantic (request/response)
├── .env.example         # Template des variables d'env
├── requirements.txt
└── README.md
```

J'ai appris qu'un projet python contient un fichier venv qui doit contenir les packages nécessaires, je vois cela comme un node_module en javascript. 

IL y a un requirements.txt qui est similaire a un package.json 

on active le venv avec pip install -r requirements.txt
Une fois les packages installé on lance le venv (qui signifie peut etre virtual env) et on lance python -m uvicorn app.main:app --reload, qui revient a faire pnpm run dev sur un projet js

## retour au projet le 26/04/2026

### retour sur expérience Claude
Quand tu as travaillé avec Claude Code la semaine dernière ? mise en place d'une structure de base scalable pour un projet pythin basé sur TM1.
à quels moments as-tu senti qu'il atteignait une limite ? Je n'ai pas vu de limites ni de probleme a comprendre le prompt.
Est-ce qu'il y a eu des moments où il a oublié quelque chose de précédent dans la conversation ? non pas a ce stade.
Est-ce qu'il y a eu des moments où il a inventé une fonction ou une syntaxe qui n'existait pas ? non , en revanche il m'a suggeré de créer un fichier .env ou .env.local, j'ai donc créé un .env.local mais il avait pas prévu le .env.local dans le model config.py en écrivant uniquement env_file(".env"), on a ajouté ensuite en debug le ".env.local" a la suite de ".env"
Est-ce qu'il y a eu des moments où il était sûr de lui sur quelque chose de faux ? non.

    - J'ai été surpris par l'efficacité de l'implémentation, tout ce qui à été demandé à été bien fait. Claude m'est venu en aide pour lancer les commande et j'ai compris l'importance de lancer le script Activate pour remplir le venv avec le contenu de requirements.txt
    - Je regrette que Claude ne m'ai pas demandé d'enregistrer un repo github mais il ne pouvait pas le savoir sans indications de ma part.
    - Tout à été bien expliqué; aucune remarque négative ou point d'amélioration a souligner.

### Les zones d'ombres

    En revanche pour ma part, je ne sais pas encore définir a quoi sert les packages qu'on a installé, il y a des zones d'ombres, a quoi sert FASTAPI? qu'est ce que uvicorn, qu'est de que pa_explorer.db ? cela me dit connected mais je n'ai pas de DB pour le moment donc cela me questionne.

### Ce que je retiens 

    Reconnaissance d'un service OData
    Un document $metadata , disponible sur le serveur TM1 , renvoie un document CSDL qui décrit le TM1 EDM mis à disposition par le service OData .
    Structure EDM
    Le $metadata de chaque modèle décrit la structure du modèle de données conformément aux conventions définies dans le protocole OData .
    Cubes et vues
    Un cube est le conteneur de base des données et une vue définit l'agencement des dimensions d'un cube.
    Dimensions de contexte et membres
    Les dimensions de contexte filtrent le contexte d'une grille mais n'apparaissent pas sur les lignes ou les colonnes.
    Dimensions en colonne et en ligne
    Lorsqu'une dimension est utilisée dans une ligne ou une colonne, chacun de ses éléments de liste possède un en-tête. Une cellule est créée pour chaque ligne et chaque colonne qui se croisent.
    Ensembles de cellules
    Un ensemble de cellules est le résultat d'une exécution d'une vue ou d'une expression MDX, représentant un instantané de vos données à un certain moment. Vous pouvez utiliser l'ID de l'ensemble de cellules dans une session au lieu d'exécuter une vue ou une expression MDX plusieurs fois.
    Eléments
    Un élément identifie l'emplacement d'une cellule dans un cube et la position de l'élément dans une dimension.
    Tâches
    Les tâches agissent comme n'importe quelle autre entité dans l'API REST TM1 . Vous pouvez utiliser des opérations de création, de lecture, de mise à jour et de suppression sur des tâches. Vous pouvez également exécuter une tâche.
    Dossiers et contenu
    Vous pouvez utiliser les dossiers et le contenu pour charger tous les éléments du dossier Applications.
    Fonctions et actions
    Le modèle d'entité TM1 expose diverses fonctions et actions spécifiques à TM1.
    Journaux d'audit
    Vous pouvez extraire des journaux d'audit à l'aide des API REST TM1® de la même manière que vous extrayez d'autres données de journalisation, telles que les journaux de transactions et de messages. Vous pouvez également utiliser des filtres ODATA, tels que top, skip et select pour interroger les informations détaillées des journaux d'audit. Le contenu du journal d'audit reste inchangé.
    Options et filtres
    Vous pouvez utiliser des options de requête / mise à jour par lots pour regrouper des requêtes, des options de requête de pagination pour limiter les résultats de votre requête et des options de filtrage pour gérer les résultats de votre requête.
    Attributs et localisation
    Vous pouvez localiser un IBM® TM1 Server en affectant des valeurs spécifiques à l'environnement local à des attributs associés à des cubes, des dimensions, des vues, des processus TI, des sous-ensembles et des éléments.

### Gestion des actifs de DB TM1 avec Git (cela m'intéresse beaucoup)
https://www.ibm.com/docs/fr/planning-analytics/3.1.0?topic=api-managing-tm1-database-assets-git

    - Je peux utiliser le contrôle des sources Git pour déployer des actifs de     base de données tels que des cubes, des livres et des vues. En tant     qu'administrateur d'une base de données TM1 , je peux déployer des actifs de     base de données entre des environnements (par exemple, du développement à la     production) sans arrêter la base de données ou copier et coller manuellement     des actifs. Les spécifications source des modèles et leurs actifs de base de     données sont créées et gérées à l'aide de commandes Git. Vous pouvez voir la     structure des actifs de base de données dans Git et utiliser les commandes Git     pour ajouter et supprimer des versions de vos actifs.

### TM1 Admin server 
    TM1 Admin Server
    Je peux découvrir le IBM TM1 Admin Server ici. Pour accéder aux métadonnées du     TM1 Admin Server : http://<adminserver>:5895/api/v1/$metadata ou https://    <adminserver>:5898/api/v1/$metadata.

### traitement des incidents :
    - Surveiller le traffic : https://www.ibm.com/docs/fr/planning-analytics/3.1.0?    topic=api-troubleshooting

### Paramètres de TM1
    Il y a aussi les paramètres de TM1 que je n'ai pas bien saisi : https://www.    ibm.com/docs/fr/planning-analytics/3.1.0?topic=api-tm1-settings

## retour au projet le 28/04/2026
## Concepts techniques de la semaine deux.

### Le pattern client API
Quand une application doit parler à un service distant, on encapsule cette communication dans un module dédié qu'on appelle un client. Ce client est une couche d'abstraction qui isole le reste de l'application des détails du protocole HTTP, des URLs spécifiques, des headers d'authentification, et de la sérialisation. Le bénéfice principal est que si l'API distante change, tu modifies uniquement le client et le reste de ton code continue de fonctionner. Le bénéfice secondaire est que tu peux remplacer le vrai client par un mock pour tester ton application sans appeler la vraie API. Dans notre projet, le client IBM PA va vivre dans un dossier dédié et exposer des méthodes lisibles comme list_servers ou get_cube_dimensions, sans laisser fuiter dans l'application les détails de l'authentification ou des chemins d'URL.

### La séparation métadonnées et données
Une bonne architecture distingue les données qui décrivent la structure du système de celles qui en représentent les valeurs. Les métadonnées sont les informations relativement stables et de petite taille qui décrivent les entités du système, par exemple la liste des serveurs, la structure des cubes, les dimensions associées, les processus disponibles. Les données sont les valeurs numériques volumineuses qui peuplent ces structures, par exemple les chiffres de ventes par mois et par région. Ces deux types n'ont ni la même fréquence d'évolution, ni la même volumétrie, ni les mêmes patterns d'accès. Les modéliser séparément avec des technologies adaptées à chacun est une pratique d'architecte qui paye sur la durée. Dans notre projet, les métadonnées vont vivre dans une base relationnelle SQLite via SQLAlchemy, et les données volumineuses vont vivre dans des fichiers Parquet, qui est un format columnar optimisé pour la compression et la lecture sélective.

### Le cache aside avec TTL
Le cache aside est un pattern où l'application gère elle-même la lecture et l'écriture du cache, par opposition à un cache transparent. Quand une donnée est demandée, l'application regarde d'abord dans le cache. Si elle y est et qu'elle est encore valide selon un délai d'expiration appelé TTL pour Time To Live, l'application sert la donnée du cache. Sinon, l'application appelle la source de vérité, stocke le résultat dans le cache avec un nouveau TTL, et sert la donnée. Cette approche te donne un contrôle fin sur les politiques de fraîcheur, parce que tu peux donner des TTL différents selon le type de donnée, par exemple une heure pour la liste des serveurs qui change rarement, et cinq minutes pour les valeurs de cellules qui peuvent évoluer plus vite. Dans notre projet, le TTL sera stocké en colonne sur les tables de métadonnées, et la logique de cache vivra dans une couche service entre les routers et le client IBM PA.

### L'injection de dépendance dans FastAPI
FastAPI propose un mécanisme appelé Depends qui permet de déclarer dans la signature d'une route les services dont elle a besoin, sans les instancier elle-même. C'est l'équivalent moderne du pattern dependency injection en programmation orientée objet. Le bénéfice principal est la testabilité, parce que tu peux remplacer une dépendance réelle par un mock dans les tests sans toucher au code de la route. Le bénéfice secondaire est la lisibilité, parce que les dépendances sont déclarées explicitement plutôt que masquées dans le corps de la fonction. Dans notre projet, la session de base de données et le client IBM PA vont être injectés par Depends dans les routes qui en ont besoin, ce qui rendra le code plus modulaire et plus testable.

### Le format Parquet
Parquet est un format de fichier binaire pour stocker des données tabulaires de manière efficace. Il stocke les valeurs colonne par colonne plutôt que ligne par ligne, ce qui permet trois bénéfices majeurs. Premièrement, la compression est très efficace parce que les valeurs d'une même colonne sont souvent similaires. Deuxièmement, la lecture peut être sélective sur les colonnes nécessaires, ce qui évite de charger les données inutiles en mémoire. Troisièmement, le format est compatible avec tous les outils modernes de data analysis comme Pandas, PyArrow, DuckDB, et il est natif dans l'écosystème Spark si tu veux passer à grande échelle. Pour notre projet, les ensembles de cellules retournés par l'API IBM PA seront stockés en Parquet dans un dossier dédié, avec une convention de nommage qui permet de retrouver rapidement le fichier correspondant à une requête.

### Mise en place des routes 
get /api/v1/health
get /api/v1/servers
Post /api/v1/servers/refresh

premier constat, tout fonctionne comme prévu, face a la lecture des données, mon premier réflexe est de comparer les attentes du code avec ce que la source retourne réellement, plutôt que de présumer un bug dans le code. 

Leçon du jour: 
1. La documentation d'une API et la réalité de ce qu'elle renvoie peuvent diverger. Le plan que Claude a produit s'appuyait sur la documentation IBM mais la réalité de mon tenant SaaS est différente de la doc. C'est pour ça que l'observation de raw-data est précieuse et donne la réalité du terrain.
2. Les valeurs null dans une réponse ne sont pas forcement un bug. Elles peuvent simplement refléter une absence d'information à la source. Garder du recule sur la lecture des données.
3. Une erreur runtime comme le 500 sur incluse_raw = false, fait partie intégrante du processus de validation. Tester deux appels au lieu d'un seul, c'est ce qui révèle ces bugs. Le débogage d'une erreur 500 sur une API REST suit toujours le même rituel. On part d'un symptôme observable côté client, ici le 500, et on remonte progressivement la chaîne de causes vers la racine du problème. Les outils principaux du remonté sont le traceback côté serveur, l'inspection de l'état des données qui transitent, et la comparaison entre cas qui marchent et cas qui plantent.
   
### Sur la suppression de pa_explorer.db
C'est ici que je veux te ralentir une seconde, parce que la suppression de la base est correcte techniquement mais elle mérite que tu comprennes pourquoi c'est nécessaire.
Quand tu ajoutes des colonnes à un modèle SQLAlchemy, il y a deux façons de propager ces nouvelles colonnes à la base existante. La première est une migration, c'est-à-dire un script qui modifie la structure de la base sans perdre les données existantes. C'est ce qu'on fait en production avec des outils comme Alembic. La seconde est de supprimer la base et de la laisser se recréer entièrement, ce qui efface tout l'historique mais garantit un schéma cohérent. C'est acceptable en développement quand les données sont volatiles et facilement reproductibles.
Tu es exactement dans ce cas. Tes données sont rechargeables depuis IBM PA en quelques secondes, donc supprimer la base et la laisser se recréer est la bonne stratégie pour un environnement de dev. En production, ce serait inacceptable, mais nous sommes loin de la production.
Note dans ton LEARNING.md ce concept de migration que tu vas rencontrer beaucoup plus formellement en semaine cinq ou six quand on parlera de la robustesse du projet. Pour l'instant, supprimer et recréer est notre stratégie acceptable.