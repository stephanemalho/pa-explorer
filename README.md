# PA-Explorer

API REST Python/FastAPI pour interagir avec IBM Planning Analytics SaaS.

## Prérequis

- Python 3.11+
- pip

## Installation

```bash
# 1. Cloner le dépôt
git clone <repo-url>
cd pa-explorer

# 2. Créer et activer un environnement virtuel
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
.\venv\Scripts\activate  

# 3. Installer les dépendances
pip install -r requirements.txt

# 4. Configurer les variables d'environnement
cp .env.example .env
# Éditer .env et renseigner les valeurs IBM_PA_TENANT_ID et IBM_PA_API_KEY
```

## Lancement

```bash
uvicorn app.main:app --reload
```

```powershell
 python -m uvicorn app.main:app --reload
```

L'API est disponible sur `http://localhost:8000`.  
La documentation interactive Swagger est accessible sur `http://localhost:8000/docs`.

## Procédures de développement

### Premier démarrage
1. Activer le venv : `.\venv\Scripts\activate` (PowerShell)
2. Installer les dépendances : `pip install -r requirements.txt`
3. Copier `.env.example` vers `.env.local` et renseigner les valeurs
4. Lancer le serveur : `python -m uvicorn app.main:app --reload`
5. Ouvrir Swagger : http://localhost:8000/docs

### Réinitialiser la base après modification d'un modèle
1. Arrêter uvicorn avec Ctrl+C
2. Fermer l'onglet pa_explorer.db dans VS Code (s'il est ouvert)
3. Supprimer la base : `del pa_explorer.db`
4. Relancer le serveur : `python -m uvicorn app.main:app --reload`

### En cas de fichier verrouillé
Si la suppression échoue avec un message "fichier en cours d'utilisation" :
1. Lister les processus Python : `Get-Process | Where-Object {$_.ProcessName -like "*python*"}`
2. Tuer les instances : `Get-Process python3.12 | Stop-Process -Force`
3. Réessayer la suppression

## Variables d'environnement

| Variable | Description | Exemple |
|---|---|---|
| `APP_NAME` | Nom de l'application | `pa-explorer` |
| `APP_VERSION` | Version de l'application | `0.1.0` |
| `DEBUG` | Mode debug FastAPI | `true` / `false` |
| `DATABASE_URL` | URL de connexion SQLAlchemy | `sqlite:///./pa_explorer.db` |
| `IBM_PA_BASE_URL` | URL de base IBM PA SaaS | `https://eu-central-1.planninganalytics.saas.ibm.com` |
| `IBM_PA_TENANT_ID` | Identifiant du tenant IBM PA | `your-tenant-id` |
| `IBM_PA_API_KEY` | Clé API IBM PA | `your-api-key` |

## Endpoints

| Méthode | Route | Description |
|---|---|---|
| `GET` | `/api/v1/health` | Statut du service et de la base de données |

## Structure du projet

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
