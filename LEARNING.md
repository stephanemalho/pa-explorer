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