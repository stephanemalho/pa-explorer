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
